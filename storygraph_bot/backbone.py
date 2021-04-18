import json
import logging
import os
import os.path
import sys

from datetime import datetime, timedelta

from storygraph_bot.util import check_cache_exist
from storygraph_bot.util import create_new_cache
from storygraph_bot.util import get_cache
from storygraph_bot.util import get_storygraph_stories
from storygraph_bot.util import generic_error_info
from storygraph_bot.util import overlap_stories
from storygraph_bot.util import post_story
from storygraph_bot.util import pretty_print_graph

logger = logging.getLogger('sgbot.sgbot')

def get_stories_uri_datetimes(jdata, date): 
    #extract graph_uri_local_datetime from data(list of list) 
    stories_uri_datetimes = []
    for story in jdata[date]["stories"]:
        story_uri_datetimes = set([graph["graph_uri_local_datetime"] for graph in story["graph_ids"]])
        stories_uri_datetimes.append(story_uri_datetimes)
    return(stories_uri_datetimes)

def get_story_cache(story_id, cache_stories):
    for indx in range(len(cache_stories)):
        story = cache_stories[indx]
        if story["story_id"] == story_id:
            return(story, indx)

def get_topstory(activation_degree, stories):
    top_story = stories[0]        
    #check activation degree
    c = top_story["max_avg_degree"] > activation_degree
    if c:
        return(top_story)

#this function should be renamed to a more specifc name
def mapper(overlap_threshold, cachedstories_uri_dts, stories_uri_dts, cache_stories):
    map_cachestories = {}     
    topstory_incache = False    
    matched_stories = {}
    unmatched_stories = {}
    for c_indx in range(len(cachedstories_uri_dts)):
        cs_uridt = cachedstories_uri_dts[c_indx]
        story_id = cache_stories[c_indx]["story_id"]
        overlap = []
        for sn in range(len(stories_uri_dts)):
            s_uridt = stories_uri_dts[sn]
            coeff = overlap_stories(cs_uridt, s_uridt)
            overlap.append({"sgtk_story_id": sn, "coeff": coeff})

        overlap = sorted(overlap, key=lambda x: x['coeff'], reverse=True)
        maxcoeff = overlap[0]['coeff']
        chosensgtk_story_id = overlap[0]['sgtk_story_id']

        if chosensgtk_story_id == 0: 
            topstory_incache = True

        if maxcoeff >= overlap_threshold:                 
            new_graphs = sorted(list(stories_uri_dts[chosensgtk_story_id] - cs_uridt), reverse=True)
            matched_stories.update({story_id: {'overlap': overlap, "new_graph_timestamps": new_graphs}})
        else:
            unmatched_stories.update({story_id: {'overlap': overlap}})
        
        stories_uri_dts[chosensgtk_story_id] = set()            

    map_cachestories["matched_stories"] = matched_stories
    map_cachestories["unmatched_stories"] = unmatched_stories
    return(map_cachestories, topstory_incache)

#data and date needs to be renamed tomore specific names
def mapper_update(sgbot_path, map_cachestories, data, date):
    ''' mapping json shows the update on the tracked stories at each timestamp'''
    mapper_file = f'{sgbot_path}/tmp/story_updates_{date}.json'
    if os.path.isfile(mapper_file):
        try:
            mapper_info = json.load(open(mapper_file, "r"))
        except Exception as e:
            print(f"Error: Please clear the {mapper_file} created in earlier test run. cmd: rm -f {mapper_file}")
            sys.exit()
    else:
        mapper_info = {}

    mapper_info[data["end_date"]] = map_cachestories        
    json.dump(mapper_info, open(mapper_file, 'w'))

def map_cache_stories(sgbot_path, overlap_threshold, cache, data, date):
    cache_stories = cache[date]['stories']

    if cache_stories != []:
        stories_uri_dts =  get_stories_uri_datetimes(data["story_clusters"], date)
        cachedstories_uri_dts = get_stories_uri_datetimes(cache, date)
        #if cachedstories_uri_dts != []    :
        map_cachestories, topstory_incache = mapper(overlap_threshold, cachedstories_uri_dts, stories_uri_dts, cache_stories)

    else:
        map_cachestories = {}     
        topstory_incache = False
        multiday_start_date = datetime.strptime(date, "%Y-%m-%d").date() - timedelta(days=1)
        multiday_start_datetime = f'{multiday_start_date} 00:00:00'
        #check if previous day cache exist
        last_cache = check_cache_exist(sgbot_path, multiday_start_date)

        if last_cache:
            map_cachestories, topstory_incache, cache = multiday_mapper(sgbot_path, overlap_threshold, cache, data, last_cache, multiday_start_date, date)
            #print(map_cachestories)    

    #json.dump(cache, open(f'test_cache.json', 'w'))            
    mapper_update(sgbot_path, map_cachestories, data, date)
    return(map_cachestories, topstory_incache)

#data and date needs to be renamed tomore specific names
def multiday_mapper(sgbot_path, overlap_threshold, cache, data, last_cache, multiday_start_date, date):    
    topstory_incache = False


    #get multiday data
    multiday_start_datetime = f'{multiday_start_date} 00:00:00'
    cmd = (f'sgtk --pretty-print -o {sgbot_path}/tmp/multi-day-clust.json maxgraph --multiday-cluster --cluster-stories-by="max_avg_degree" --cluster-stories --start-datetime="{multiday_start_datetime}" --end-datetime="{args.end_datetime}" > {sgbot_path}/tmp/console_output_multiday.log  2>&1')
    a = os.system(cmd)
    multiday_data = json.load(open(f'{sgbot_path}/tmp/multi-day-clust.json', "r"))


    #map last_cache with multiday_data 
    multiday_start_date = str(multiday_start_date)
    last_cache_stories = last_cache[multiday_start_date]['stories']
    multiday_stories_uri_dts =  get_stories_uri_datetimes(multiday_data["story_clusters"], "YYYY-MM-DD")
    last_cachedstories_uri_dts = get_stories_uri_datetimes(last_cache, multiday_start_date)
    map_cachestories_multiday, topstory_incache_multiday = mapper(overlap_threshold, last_cachedstories_uri_dts, multiday_stories_uri_dts, last_cache_stories)
    del topstory_incache_multiday


    #updated multiday mapper which will only include updated stories
    updated_map_cachestories_multiday ={"matched_stories":{}, "unmatched_stories":{}}

    #check which stories have graph timestamp from new day and add those traversing stories to intermidiate cache
    intermidiate_cache = create_new_cache(date)
    intermidiate_cache_stories = intermidiate_cache[date]['stories']
    for story_id, update in map_cachestories_multiday["matched_stories"].items():
        new_graphs = update['new_graph_timestamps']
        if new_graphs:
            latest_graph_uri = new_graphs[0]
            if latest_graph_uri.startswith(date):

                #get story from multiday_data
                data_sidx = update["overlap"][0]['sgtk_story_id']
                multiday_story = multiday_data["story_clusters"]["YYYY-MM-DD"]["stories"][data_sidx]
                multiday_story["story_id"] = story_id
                intermidiate_cache_stories.append(multiday_story)

                #add last_day_cache of the story to new cache
                last_story_cache, c_indx = get_story_cache(story_id, last_cache_stories)
                cache[date]['stories'].append(last_story_cache)

                #add stories with new updates to updated multiday mapper dictionary
                updated_map_cachestories_multiday["matched_stories"].update({story_id:update})                


    #map intermidiate_cache with current data
    del(map_cachestories_multiday)
    if intermidiate_cache_stories != []:
        stories_uri_dts =  get_stories_uri_datetimes(data["story_clusters"], date)
        intermcachedstories_uri_dts = get_stories_uri_datetimes(intermidiate_cache, date)
        map_cachestories_interm, topstory_incache = mapper(overlap_threshold, intermcachedstories_uri_dts, stories_uri_dts, intermidiate_cache_stories)
        for story_id, update in map_cachestories_interm["matched_stories"].items():
            data_overlap = update['overlap']
            updated_map_cachestories_multiday["matched_stories"][story_id]["overlap"] = data_overlap


    return(updated_map_cachestories_multiday, topstory_incache, cache)

def newstory_handler(sgbot_path, activation_degree, cache_stories, stories, st0_incache, date):
    top_story = get_topstory(activation_degree, stories)
    new_story_id = None
    if top_story:        
        if not st0_incache:             #add story to cache
            new_story_id = new_story(sgbot_path, top_story, cache_stories, date)
    return(new_story_id)    

def new_story(sgbot_path, top_story, cache_stories, date):
    #print("Creating 1 new thread for new top story")            
    story_id = f'{date.replace("-","")}_{len(cache_stories)}'
    top_story["story_id"] = story_id
    top_story["reported_graphs"] = []
    story_graph = top_story["graph_ids"][0]
    #post story to file
    post_story(sgbot_path, story_id, story_graph)    
    #update cache
    top_story["reported_graphs"].append(story_graph)
    cache_stories.append(top_story)     
    return(story_id)

def update_handler(sgbot_path, cache_stories, stories, map_cachestories):
    updated_ids = []
    if map_cachestories:       
        for story_id, update in map_cachestories["matched_stories"].items():
            is_updated = update_story(sgbot_path, story_id, update, cache_stories, stories)
            if is_updated:
                updated_ids.append(story_id)    

    if updated_ids == []:
        updated_ids = None
    else:
        updated_ids = ', '.join(updated_ids)
    return(updated_ids)    

def update_story(sgbot_path, story_id, update, cache_stories, stories):
    story_cache, c_indx = get_story_cache(story_id, cache_stories)
    data_sidx = update["overlap"][0]['sgtk_story_id']
    new_graphs = update['new_graph_timestamps']

    if new_graphs:
        story_data = stories[data_sidx]             
        story_graphs = story_data["graph_ids"]

        if story_graphs[0]['id'] != story_cache["graph_ids"][0]['id']:
            latest_graph = story_graphs[0]
        else: 
            #top snapshot hasnt changed
            latest_graph_uri = new_graphs[0]
            latest_story_graphs = [dic for dic in story_graphs if dic["graph_uri_local_datetime"]==latest_graph_uri] 
            l_id = sorted(latest_story_graphs, key=lambda k: int(k['id'].split("-")[1]), reverse=True) #id used identify graphs
            latest_graph = l_id[0]
        
        post_story(sgbot_path, story_id, latest_graph)    
        #update_cache
        story_data["story_id"] = story_id    
        story_data["reported_graphs"] = story_cache["reported_graphs"]                                                
        story_data["reported_graphs"].append(latest_graph)                                                    
        cache_stories[c_indx] = story_data                 
        return(True)    

def console_log_stories(cache_stories):
    '''print stories on console'''
    print("\nAll Stories:\n")
    for story in cache_stories:    
        story_id = story["story_id"]
        reported_graphs = story["reported_graphs"]

        formatted_story = pretty_print_graph(story_id, reported_graphs[-1])
        for k,v in formatted_story.items(): 
            print(f'\t{k}: {v}')

        if len(reported_graphs) > 1:    
            print(f'\t\tHistory:')
            for graph in reported_graphs[:-1]:
                formatted_story = pretty_print_graph(story_id, graph)
                for k,v in formatted_story.items():
                    if k!="Story ID": 
                        print(f'\t\t\t{k}: {v}')
                print('')        
        print('')

def setup_storage(stories_path):

    try:
        os.makedirs( stories_path + '/cache', exist_ok=True )
        os.makedirs( stories_path + '/tmp', exist_ok=True )
        os.makedirs( stories_path + '/tracked_stories', exist_ok=True )
    except:
        generic_error_info()
        return False

    return True

def sgbot(sgbot_path, activation_degree, overlap_threshold, start_datetime, end_datetime, **kwargs):

    if( setup_storage(sgbot_path) is False ):
        return {}

    print('Sgbot Path:', sgbot_path)
    print("Activation degree: "+str(activation_degree))
    print("Overlap threshold: "+str(overlap_threshold))

    data = get_storygraph_stories(sgbot_path, start_datetime, end_datetime)
    if "story_clusters" not in data:
        print("No stories in the new data")
        return {}

    date = list(data["story_clusters"])[0]      
    cache = get_cache(sgbot_path, date)
    cache_stories = cache[date]['stories']
    stories = data["story_clusters"][date]["stories"]    

    #match stories
    map_cachestories, st0_incache = map_cache_stories(sgbot_path, overlap_threshold, cache, data, date)

    #new top story    
    new_story_id = newstory_handler(sgbot_path, activation_degree, cache_stories, stories, st0_incache, date)
    print(f'New top story id: {new_story_id}')
    
    #update tracking stories
    updated_ids = update_handler(sgbot_path, cache_stories, stories, map_cachestories)    
    print(f'Updates of previous stories: {updated_ids}')

    #dump_cache 
    cache[date]["end_datetime"] = data["end_date"]
    json.dump(cache, open(f'{sgbot_path}/cache/cache_{date}.json', 'w'))    

    #print stories on console
    console_log_stories(cache_stories)
    return {
        'new_story_id': new_story_id,
        'updated_ids': updated_ids,
        'cache_stories': cache_stories
    }



