import logging
import tweepy

from datetime import datetime
from storygraph_bot.util import generic_error_info

logger = logging.getLogger('sgbot.sgbot')

def post_msg(consumer_key, consumer_secret, access_token, access_token_secret, msg='Hello, Test Message. Could delete soon.', reply_id=''):
    
    resp_payload = {}
    try:
        # OAuth process, using the keys and tokens
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Creation of the actual interface, using authentication
        api = tweepy.API(auth)
        
        if( reply_id == '' ):
            resp = api.update_status(msg)
        else:
            resp = api.update_status(msg, in_reply_to_status_id=reply_id)

        resp_payload = {
            'tweet_id': resp._json['id_str']
        }
    except:
        generic_error_info()

    return resp_payload

def compose_msg_for_story(graph, graph_pos, story, story_date, **kwargs):
    
    '''
        NEW MESSAGE FORMAT:
        fmt 1
        Breaking story (2018-05-19): Texas gov calls for action after shooting: ‘We need to do more than... (http://thehill.com/homenews/state-watch/388426-texas-gov-calls-for-action-after-shooting-we-need-to-do-more-than-just)

        |●●●●○○○○○○○○○○○○○○○○○○○○|
        Avg degree: 4.17
        Age: 0h:50m

        Graph: http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=26&hist=1440&t=2018-05-19T04:21:13
        #SGBotTimetravel
    
        fmt 2
        2. Story update, falling (2020-11-03): Biden and Trump criticize their opponent in multiple states on the ... (https://washingtonpost.com/politics/campaign-biden-trump/2020/11/02/dd36f5e2-1d0e-11eb-ba21-f2f001f0554b_story.html?utm_source=rss&utm_medium=referral&utm_campaign=wp_politics)

        |●●●○○○○○○○○○○○○○○○○○○○○○|
        Avg degree: 3.12
        Age: 6h:30m

        Graph: http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=83&hist=1440&t=2020-11-03T13:51:12
    '''
    progress_bar_glyph_on = kwargs.get('progress_bar_glyph_on', '●')
    progress_bar_glyph_off = kwargs.get('progress_bar_glyph_off', '○')

    progress_bar_glyph_on = progress_bar_glyph_on.strip()
    progress_bar_glyph_off = progress_bar_glyph_off.strip()

    progress_bar_glyph_on = progress_bar_glyph_on[0] if len(progress_bar_glyph_on) > 1 else progress_bar_glyph_on
    progress_bar_glyph_off = progress_bar_glyph_off[0] if len(progress_bar_glyph_off) > 1 else progress_bar_glyph_off

    def get_progress_bar(avg_degree, max_bar=24):
        avg_degree = int(avg_degree)

        pg_bar = '|' + (progress_bar_glyph_off * max_bar).replace(progress_bar_glyph_off, progress_bar_glyph_on, avg_degree) + '|'

        return pg_bar

    def get_hashtag(story_date):
        if( datetime.now().strftime('%Y-%m-%d') == story_date ):
            return '#SGBotBreakingNews'
        else:
            return '#SGBotTimetravel'

    def get_fmt_age(story):
        
        d0 = story['reported_graphs'][0]['graph_uri_local_datetime']
        d1 = story['reported_graphs'][-1]['graph_uri_local_datetime']
        
        if( d0 == d1 ):
            age = story['timedelta']
        else:
            d0 = datetime.strptime(d0, '%Y-%m-%dT%H:%M:%S')
            d1 = datetime.strptime(d1, '%Y-%m-%dT%H:%M:%S')
            age = str(d1 - d0)

        '''
            age formats:
            xx days, HH:MM:SS.abcde
        '''
        age = age.split('.')[0]
        age = age.split(':')[:-1]
        age = age[0] + 'h:' + age[1] + 'm'

        return age


    degree_msg = kwargs.get('degree_msg', '')
    degree_msg = degree_msg if degree_msg == '' else f', {degree_msg}'

    max_title_len = 95
    max_node_title = graph['max_node_title'].strip()
    max_node_title = max_node_title if len(max_node_title) <= max_title_len else max_node_title[:max_title_len-3] + '...'

    
    age = get_fmt_age(story)
    link = graph['max_node_link']
    if( graph_pos == 0 ):
        msg_start = f'Breaking story ({story_date}): {max_node_title} ({link})\n\n'
    else:
        story_indx = str(graph_pos+1)[:3]
        msg_start = f'{story_indx}. Story update{degree_msg} ({story_date}): {max_node_title} ({link})\n\n'

    msg_start += '{:.2f}'.format( graph['avg_degree'] )+ ':\n' 
    msg_start += get_progress_bar( graph['avg_degree'] ) + '\n'
    msg_start += 'Age: {}'.format(age) + '\n\n'
    
    msg_start += graph['graph_uri']
    if( graph_pos == 0 ):
        msg_start += '\n' + get_hashtag(story_date)
    
    return msg_start

def post_tweet(stories, consumer_key, consumer_secret, access_token, access_token_secret, selected_dates=[], tweet_activation_degree=4, **kwargs):
    
    def check_should_post_story(story, tweet_activation_degree):

        if( 'reported_graphs' not in story ):
            return False

        for sg in story['reported_graphs']:
            if( sg['avg_degree'] >= tweet_activation_degree ):
                return True

        return False

    logger.info('\npost_tweet():')
    logger.info(f'\ttweet_activation_degree: {tweet_activation_degree}')

    def post_tweets_for_story(story, story_date):

        if( 'reported_graphs' not in story ):
            return

        for i in range( len(story['reported_graphs']) ):
            
            graph = story['reported_graphs'][i]
            if( 'tweet_id' in graph ):
                continue

            reply_id = ''
            degree_msg = ''
            if( len(story['reported_graphs']) > 1 ):

                prev_deg = story['reported_graphs'][i-1]['avg_degree']
                now_deg = story['reported_graphs'][i]['avg_degree']
                
                if( prev_deg == now_deg ):
                    degree_msg = 'same'
                elif( now_deg > prev_deg ):
                    degree_msg = 'rising'
                else:
                    degree_msg = 'falling'

                if( 'tweet_id' in story['reported_graphs'][i-1] ):
                    reply_id = story['reported_graphs'][i-1]['tweet_id']

            msg = compose_msg_for_story(graph=graph, graph_pos=i, story=story, story_date=story_date, degree_msg=degree_msg, **kwargs)
            
            logger.info( 'Posting story id: {}'.format(story['story_id']) )
            logger.info(msg)

            resp_payload = post_msg(consumer_key, consumer_secret, access_token, access_token_secret, msg=msg, reply_id=reply_id)
            if( 'tweet_id' in resp_payload ):
                logger.info( '\tPosted successfully: {}'.format(resp_payload['tweet_id']) )
                graph['tweet_id'] = resp_payload['tweet_id']

            logger.info('')

            
    for date, date_payload in stories.items():


        if( len(selected_dates) != 0 ):
            if( date not in selected_dates ):
                continue

        for i in range( len(date_payload['stories']) ):
            
            story = date_payload['stories'][i]
            reply_id = ''
            if( check_should_post_story(story, tweet_activation_degree) == False ):
                continue

            post_tweets_for_story(story, date)