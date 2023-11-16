import os
import sys
import time

from getpass import getpass

from bs4 import BeautifulSoup
from datetime import datetime
from NwalaTextUtils.textutils import genericErrorInfo
from NwalaTextUtils.textutils import getLinks

from playwright.sync_api import sync_playwright
from urllib.parse import quote_plus

from storygraph_bot.scrape_twitter_util import paral_rehydrate_tweets
from storygraph_bot.scrape_twitter_util import readTextFromFile
from storygraph_bot.scrape_twitter_util import rehydrate_tweet
from storygraph_bot.scrape_twitter_util import write_tweets_to_jsonl_file
from storygraph_bot.scrape_twitter_util import writeTextToFile

def is_twitter_user_auth(links, cur_page_uri):

    if( cur_page_uri.strip().startswith('https://twitter.com/home') ):
        return True

    logged_in_links = ['https://twitter.com/home', 'https://t.co/']

    for l in links:
        for log_l in logged_in_links:
            if( l['link'].startswith(log_l) ):
                return True
    return False

def scroll_up(page):
    page.evaluate("window.scrollTo( {'top': 0, 'left': 0, 'behavior': 'smooth'} );")

def scroll_down(page):
    page.evaluate("window.scrollTo( {'top': document.body.scrollHeight, 'left': 0, 'behavior': 'smooth'} );")

def post_tweet(browser_dets, msg, button_name='Post', after_post_sleep=2.5, **kwargs):

    if( len(browser_dets) == 0 ):
        return {}

    get_new_tweet_link = kwargs.get('get_new_tweet_link', False)
    twitter_accnt = kwargs.get('twitter_account', '')
    reply_to_link = kwargs.get('reply_to_link', '')

    if( reply_to_link != '' ):
        button_name = 'Reply'
        browser_dets['page'].goto(reply_to_link)
        time.sleep(3)

    #Post, Reply
    # [id$='someId'] will match all ids ending with someId: https://stackoverflow.com/a/8714421
    eval_str = f''' 
    reply_bottons = document.querySelectorAll('[aria-label$="{button_name}"]');
    reply_bottons[reply_bottons.length-1].click();
    '''
    browser_dets['page'].evaluate(eval_str)
    time.sleep(1)
    browser_dets['page'].keyboard.type(msg, delay=20)
    browser_dets['page'].evaluate(''' document.querySelectorAll('[data-testid="tweetButton"]')[0].click(); ''')

    #added because I observed that tweets were not posted without it
    time.sleep(after_post_sleep)
    tweet_link = ''

    if( get_new_tweet_link is True and twitter_accnt != '' ):
        
        tweets = get_search_tweets( browser_dets, f'(from:{twitter_accnt})' )
        tweets['tweets'] = sorted(tweets['tweets'], key=lambda k: k['id_str'], reverse=True)

        for t in tweets['tweets']:
            
            #assume first tweet is the most recent tweet (review logic)
            tweet_link = 'https://twitter.com/{}/status/{}'.format( t['user']['screen_name'], t['id_str'] )
            print(f'\tposted tweet: {tweet_link}')
            break
    
    return {
        'tweet_link': tweet_link
    }

    
def color_tweet(page, tweet_link):

    query_slc = f'''article = document.querySelectorAll('[href="{tweet_link}"]');'''
    page.evaluate(query_slc + '''
        if( article.length != 0 )
        {
            article = article[0];
            article.style.backgroundColor = 'red';
            i = 0;
            while(i < 1000)
            {
                if( article.nodeName == 'ARTICLE' )
                {
                    article.style.outline = "thick solid red";
                    article.className = "cust-tweet";
                    break;
                }
                article = article.parentElement;
                i++;
            }
        }
    ''')


def get_tweet_ids_user_timeline_page(screen_name, page, max_tweets):

    empty_result_count = 0
    prev_len = 0
    tweets = []
    tweet_links = set()
    tweet_dets = {}
    break_flag = False

    while( True ):

        page_html = page.content()
        soup = BeautifulSoup(page_html, 'html.parser')
        articles = soup.find_all('article')        

        for i in range(len(articles)):
            
            t = articles[i]
            is_retweet = t.find('span', {'data-testid': 'socialContext'})
            is_retweet = False if is_retweet is None else is_retweet.text.strip().lower().endswith(' retweeted')
            
            tweet_datetime = ''
            tweet_link = t.find('time')
            
            if( tweet_link is None ):
                tweet_link = ''  
            else:
                tweet_datetime = tweet_link.get('datetime', '')
                tweet_link = tweet_link.parent.get('href', '')

            if( tweet_link == '' ):
                continue


            if( screen_name != '' and is_retweet is False and tweet_link.startswith(f'/{screen_name}/') is False ):
                #This tweet was authored by someone else, NOT the owner of the timeline, and since it was not retweeted
                continue

            #color_tweet(page, tweet_link)
            tweet_dets[tweet_link] = {'datetime': tweet_datetime, 'is_retweet': is_retweet}
            tweet_links.add( tweet_link )

            print( '\textracted {} tweets'.format(len(tweet_links)) )
            if( len(tweet_links) == max_tweets ):
                break_flag = True
                print(f'breaking reached ({len(tweet_links)}) maximum: {max_tweets}')
                break
        
        if( break_flag is True ):
            break

        empty_result_count = empty_result_count + 1 if prev_len == len(tweet_links) else 0
        if( empty_result_count > 5 ):
            print(f'No new tweets found, so breaking')
            break

        prev_len = len(tweet_links)
        print('\tthrottling/scrolling, then sleeping for 2 second\n')
        scroll_down(page)
        time.sleep(2)


    for tlink in tweet_links:

        stat_screen_name, tid = tlink.split('/status/')
        twt_uri_dets = {
            'tid': tid,
            'status_screen_name': stat_screen_name[1:],
            'datetime': tweet_dets[tlink]['datetime']
        }
        twt_uri_dets['notes'] = {'timeline_screen_name': screen_name, 'is_retweet': tweet_dets[tlink]['is_retweet']}
        tweets.append(twt_uri_dets)
        

    tweets = sorted(tweets, key=lambda x:x['tid'])
    return tweets

def get_timeline_tweets(browser_dets, screen_name, max_tweets=20):

    screen_name = screen_name.strip()
    uri = f'https://twitter.com/{screen_name}/with_replies'
    payload = {'self': uri, 'tweets': []}
    if( max_tweets < 0  or len(browser_dets) == 0 or screen_name == '' ):
        return {}

    print( f'\nget_timeline_tweets(): {screen_name}' )
    browser_dets['page'].goto(uri)

    tweet_ids = get_tweet_ids_user_timeline_page( screen_name, browser_dets['page'], max_tweets )
    payload['tweets'] = paral_rehydrate_tweets(tweet_ids)

    return payload

def get_search_tweets(browser_dets, query, max_tweets=20):

    query = query.strip()
    uri = 'https://twitter.com/search?q=' + quote_plus(query) + '&f=live&src=typd'
    payload = {'self': uri, 'tweets': []}
    if( max_tweets < 0  or len(browser_dets) == 0 or query == '' ):
        return payload

    print('\nget_search_tweets():')
    browser_dets['page'].goto(uri)
    
    tweet_ids = get_tweet_ids_user_timeline_page( '', browser_dets['page'], max_tweets )
    payload['tweets'] = paral_rehydrate_tweets(tweet_ids)

    return payload

def try_to_login(page, username, password):

    print('\ntry_to_login()')
    username = username.strip()
    password = password.strip()

    if( username == '' or password == '' ):
        return
        
    page.get_by_role('textbox').fill(username)
    page.keyboard.press('Enter')
    page.get_by_label('Password', exact=True).type(password, delay=20)
    page.keyboard.press('Enter')


def get_auth_twitter_pg(playwright, unsafe_cred_path='/tmp/', callback_uri='', do_unsafe_login=True, headless=False):
    
    print('\nget_auth_twitter_pg()')
    unsafe_cred_path = unsafe_cred_path.strip()

    if( unsafe_cred_path == '' ):
        print('unsafe_cred_path is empty, returning')
        return

    unsafe_cred_path = unsafe_cred_path if unsafe_cred_path.endswith('/') else f'{unsafe_cred_path}/'
    print('\tunsafe_cred_path:', unsafe_cred_path)

    username = ''
    password = ''

    if( do_unsafe_login is True ):
        print('\t--- Unsafe login ---')

        if( os.path.exists(f'{unsafe_cred_path}unsafe_twitter_username.txt') and os.path.exists(f'{unsafe_cred_path}unsafe_twitter_password.txt') ):
            username = readTextFromFile(f'{unsafe_cred_path}unsafe_twitter_username.txt').strip()
            password = readTextFromFile(f'{unsafe_cred_path}unsafe_twitter_password.txt').strip()
            
            print(f'retrieved username from {unsafe_cred_path}unsafe_twitter_username.txt')
            print(f'retrieved password from {unsafe_cred_path}unsafe_twitter_password.txt')

        if( username == '' or password == '' ):
            username = input('\n\tEnter Twitter username: ')
            password = getpass('\tEnter Twitter password: ')

            writeTextToFile(f'{unsafe_cred_path}unsafe_twitter_username.txt', username)
            writeTextToFile(f'{unsafe_cred_path}unsafe_twitter_password.txt', password)

    chromium = playwright.firefox #"chromium" or "firefox" or "webkit".
    browser = chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    
    sleep_seconds = 3
    page.goto('https://twitter.com/login')

    if( do_unsafe_login is True ):
        time.sleep(sleep_seconds)
        try_to_login(page, username, password)
    
    while( True ):

        print(f'\twaiting for login, sleeping for {sleep_seconds} seconds')
        time.sleep(sleep_seconds)
        
        page_html = page.content()
        page_links = getLinks(uri='', html=page_html, fromMainTextFlag=False)
        scroll_down(page)

        if( is_twitter_user_auth(page_links, page.url) ):
            
            print('\tauthenticated')
            if( callback_uri != '' ):
                page.goto(callback_uri)
                print(f'\tauthenticated, loaded {callback_uri}')
                
            print('\tsleeping for 3 seconds')
            time.sleep(3)
            return {
                'page': page,
                'context': context,
                'browser': browser
            }
    
    return {}

def main():
    
    '''
    token = 'abcde'
    res = rehydrate_tweet('1288498682971795463', token=token)
    print(res)
    return
    '''

    with sync_playwright() as playwright:
        
        unsafe_cred_path = f'/tmp/'
        browser_dets = get_auth_twitter_pg(playwright, headless=False, unsafe_cred_path=unsafe_cred_path)
        if( len(browser_dets) == 0 ):
            return
        
        get_new_tweet_link = True
        twitter_account = 'xnwala'
        reply_to_link = 'https://twitter.com/xnwala/status/1699844461545836833'
        
        msg = f"\nAnother testing reply, posting @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        post_tweet(browser_dets, msg, twitter_account=twitter_account, get_new_tweet_link=get_new_tweet_link, reply_to_link=reply_to_link)
        time.sleep(100000)

        '''
        from playwright.sync_api import sync_playwright
        from scrape_twitter import get_auth_twitter_pg
        from scrape_twitter import post_tweet

        with sync_playwright() as playwright:
                
            browser_dets = get_auth_twitter_pg(playwright)
            if( len(browser_dets) != 0 ):
                post_tweet(browser_dets, "Hello, World!\nWelcome to my timeline!")
        '''

if __name__ == "__main__":
    main()
