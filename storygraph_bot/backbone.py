import json
import logging
import os
import os.path
import sys

from datetime import datetime, timedelta

from storygraph_bot.util import check_cache_exist
from storygraph_bot.util import create_new_cache
from storygraph_bot.util import dump_json_to_file
from storygraph_bot.util import get_cache
from storygraph_bot.util import get_dict_frm_file
from storygraph_bot.util import get_storygraph_stories
from storygraph_bot.util import generic_error_info
from storygraph_bot.util import overlap_stories
from storygraph_bot.util import post_story
from storygraph_bot.util import pretty_print_graph
from storygraph_bot.util import rm_all_but_yesterday_today_cache

logger = logging.getLogger('sgbot.sgbot')

def get_stories_uri_datetimes(jdata, date): 
    #extract graph_uri_local_datetime from data(list of list) 

    if( date not in jdata ):
        return []

    if( 'stories' not in jdata[date] ):
        return []

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

#this function should be renamed to a more specifc name
def mapper(overlap_threshold, cachedstories_uri_dts, stories_uri_dts, cache_stories):
    map_cachestories = {}     
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
        
        if maxcoeff >= overlap_threshold: 
            chosensgtk_story_id = overlap[0]['sgtk_story_id']                
            new_graphs = sorted(list(stories_uri_dts[chosensgtk_story_id] - cs_uridt), reverse=True)
            matched_stories.update({story_id: {'overlap': overlap, "new_graph_timestamps": new_graphs}})
            stories_uri_dts[chosensgtk_story_id] = set()            
        else:
            unmatched_stories.update({story_id: {'overlap': overlap}})
        
    map_cachestories["matched_stories"] = matched_stories
    map_cachestories["unmatched_stories"] = unmatched_stories
    return(map_cachestories)

def mapper_update(sgbot_path, map_cachestories, sg_stories, cur_story_date):
    ''' mapping json shows the update on the tracked stories at each timestamp'''
    mapper_file = f'{sgbot_path}/tmp/story_updates_{cur_story_date}.json'
    if os.path.isfile(mapper_file):
        try:
            mapper_info = get_dict_frm_file(mapper_file)
        except Exception as e:
            print(f"Error: Please clear the {mapper_file} created in earlier test run. cmd: rm -f {mapper_file}")
            sys.exit()
    else:
        mapper_info = {}

    if( 'end_date' in sg_stories ):
        mapper_info[sg_stories['end_date']] = map_cachestories

    dump_json_to_file( mapper_file, mapper_info, indent_flag=False, extra_params={'verbose': False} )

def map_cache_stories(sgbot_path, overlap_threshold, cache, sg_stories, cur_story_date, end_datetime, **kwargs):
    cache_stories = cache[cur_story_date]['stories']

    if cache_stories != []:
        stories_uri_dts =  get_stories_uri_datetimes(sg_stories["story_clusters"], cur_story_date)
        cachedstories_uri_dts = get_stories_uri_datetimes(cache, cur_story_date)
        #if cachedstories_uri_dts != []    :
        map_cachestories = mapper(overlap_threshold, cachedstories_uri_dts, stories_uri_dts, cache_stories)

    else:
        map_cachestories = {}     
        multiday_start_date = datetime.strptime(cur_story_date, "%Y-%m-%d").date() - timedelta(days=1)
        multiday_start_datetime = f'{multiday_start_date} 00:00:00'
        #check if previous day cache exist
        last_cache = check_cache_exist(sgbot_path, multiday_start_date)

        if last_cache:
            map_cachestories, cache = multiday_mapper(sgbot_path, overlap_threshold, cache, sg_stories, last_cache, multiday_start_date, end_datetime, cur_story_date)
            #print(map_cachestories)    

    
    if( kwargs.get('keep_history', False) is True ):
        mapper_update(sgbot_path, map_cachestories, sg_stories, cur_story_date)

    return(map_cachestories)

def multiday_mapper(sgbot_path, overlap_threshold, cache, sg_stories, last_cache, multiday_start_date, end_datetime, cur_story_date):    
    #get multiday sg_stories
    multiday_start_datetime = f'{multiday_start_date} 00:00:00'
    cmd = (f'sgtk --pretty-print -o {sgbot_path}/tmp/multi-day-clust.json maxgraph --multiday-cluster --cluster-stories-by="max_avg_degree" --cluster-stories --start-datetime="{multiday_start_datetime}" --end-datetime="{end_datetime}" > {sgbot_path}/tmp/console_output_multiday.log  2>&1')
    a = os.system(cmd)
    multiday_data = get_dict_frm_file(f'{sgbot_path}/tmp/multi-day-clust.json')


    #map last_cache with multiday_data 
    multiday_start_date = str(multiday_start_date)
    last_cache_stories = last_cache[multiday_start_date]['stories']
    multiday_stories_uri_dts =  get_stories_uri_datetimes(multiday_data["story_clusters"], "YYYY-MM-DD")
    last_cachedstories_uri_dts = get_stories_uri_datetimes(last_cache, multiday_start_date)
    map_cachestories_multiday = mapper(overlap_threshold, last_cachedstories_uri_dts, multiday_stories_uri_dts, last_cache_stories)


    #updated multiday mapper which will only include updated stories
    updated_map_cachestories_multiday={"matched_stories":{}, "unmatched_stories":{}}

    #check which stories have graph timestamp from new day and add those traversing stories to intermidiate cache
    intermidiate_cache = create_new_cache(cur_story_date)
    intermidiate_cache_stories = intermidiate_cache[cur_story_date]['stories']
    for story_id, update in map_cachestories_multiday["matched_stories"].items():
        new_graphs = update['new_graph_timestamps']
        if new_graphs:
            latest_graph_uri = new_graphs[0]
            if latest_graph_uri.startswith(cur_story_date):

                #get story from multiday_data
                data_sidx = update["overlap"][0]['sgtk_story_id']
                multiday_story = multiday_data["story_clusters"]["YYYY-MM-DD"]["stories"][data_sidx]
                multiday_story["story_id"] = story_id
                intermidiate_cache_stories.append(multiday_story)

                #add last_day_cache of the story to new cache
                last_story_cache, c_indx = get_story_cache(story_id, last_cache_stories)
                cache[cur_story_date]['stories'].append(last_story_cache)

                #add stories with new updates to updated multiday mapper dictionary
                updated_map_cachestories_multiday["matched_stories"].update({story_id:update})                


    #map intermidiate_cache with current sg_stories
    del(map_cachestories_multiday)
    if intermidiate_cache_stories != []:
        stories_uri_dts =  get_stories_uri_datetimes(sg_stories["story_clusters"], cur_story_date)
        intermcachedstories_uri_dts = get_stories_uri_datetimes(intermidiate_cache, cur_story_date)
        map_cachestories_interm = mapper(overlap_threshold, intermcachedstories_uri_dts, stories_uri_dts, intermidiate_cache_stories)
        for story_id, update in map_cachestories_interm["matched_stories"].items():
            data_overlap = update['overlap']
            updated_map_cachestories_multiday["matched_stories"][story_id]["overlap"] = data_overlap


    return(updated_map_cachestories_multiday, cache)

def story_incache(num, map_cachestories):
    is_story_incache = False
    if map_cachestories != {}:
        for story_id, update in map_cachestories["matched_stories"].items():
            data_sidx = update["overlap"][0]['sgtk_story_id']
            if data_sidx == num:
                is_story_incache = True
    
    return(is_story_incache)

def get_topstories(top_stories_count, activation_degree, stories, map_cachestories):
    k_top_stories = []

    if( len(stories) != 0 ):
        
        if len(stories) < top_stories_count:
            top_stories_count = len(stories)

        for num in range(top_stories_count):    
            top_story = stories[num]        
            if( 'max_avg_degree' not in top_story ):
                continue

            #check activation degree
            if top_story["max_avg_degree"] > activation_degree :
                if not story_incache(num, map_cachestories):
                    k_top_stories.append(top_story)
    
    return(k_top_stories)

def newstory_handler(sgbot_path, cache_stories, stories, map_cachestories, top_stories_count, activation_degree, cur_story_date, **kwargs):

    k_top_stories = get_topstories(top_stories_count, activation_degree, stories, map_cachestories)
    new_story_ids = []

    if k_top_stories != []:        
        for top_story in k_top_stories:
            new_story_id = new_story(sgbot_path, top_story, cache_stories, cur_story_date, enable_post_story=kwargs.get('keep_history', False))
            new_story_ids.append(new_story_id)

    if new_story_ids == []:
        new_story_ids = None
    else:
        new_story_ids = ', '.join(new_story_ids)

    return(new_story_ids) 

def cp_details_to_reported_graph(sg, graph_ids):

    timestamps = [ g['graph_uri_local_datetime'] for g in graph_ids if g['graph_uri_local_datetime'] <= sg['graph_uri_local_datetime'] ]
    timestamps.sort()

    if( len(timestamps) == 0 ):
        return

    sg.setdefault('more_details', {})
    sg['more_details']['earliest_graph_datetime'] = timestamps[0]

def new_story(sgbot_path, top_story, cache_stories, cur_story_date, enable_post_story=False):
    #print("Creating 1 new thread for new top story")            
    story_id = f'{cur_story_date.replace("-","")}_{len(cache_stories)}'
    top_story["story_id"] = story_id
    top_story["reported_graphs"] = []
    story_graph = top_story["graph_ids"][0]
    
    #post story to file
    if( enable_post_story is True ):
        post_story(sgbot_path, story_id, story_graph)    
    
    cp_details_to_reported_graph(story_graph, top_story["graph_ids"])

    #update cache
    top_story["reported_graphs"].append(story_graph)
    cache_stories.append(top_story)     
    return(story_id)

def update_handler(sgbot_path, cache_stories, stories, map_cachestories, enable_post_story=False):
    updated_ids = []
    if map_cachestories:       
        for story_id, update in map_cachestories["matched_stories"].items():
            is_updated = update_story(sgbot_path, story_id, update, cache_stories, stories, enable_post_story=enable_post_story)
            if is_updated:
                updated_ids.append(story_id)    

    if updated_ids == []:
        updated_ids = None
    else:
        updated_ids = ', '.join(updated_ids)
    return(updated_ids)    

def update_story(sgbot_path, story_id, update, cache_stories, stories, enable_post_story=False):
    story_cache, c_indx = get_story_cache(story_id, cache_stories)
    data_sidx = update["overlap"][0]['sgtk_story_id']
    new_graphs = update['new_graph_timestamps']

    if new_graphs:
        story_data = stories[data_sidx]             
        story_graphs = story_data["graph_ids"]

        if story_graphs[0]['id'] == story_cache["graph_ids"][0]['id']:
            #top snapshot hasnt changed
            latest_graph_uri = new_graphs[0]
            latest_story_graphs = [dic for dic in story_graphs if dic["graph_uri_local_datetime"]==latest_graph_uri] 
            l_id = sorted(latest_story_graphs, key=lambda k: int(k['id'].split("-")[1]), reverse=True) #id used identify graphs
            latest_graph = l_id[0]
        else:
            latest_graph = story_graphs[0]

        cp_details_to_reported_graph(latest_graph, story_graphs)

        if( enable_post_story is True ):
            post_story(sgbot_path, story_id, latest_graph)
        #update_cache
        story_data["story_id"] = story_id    
        story_data["reported_graphs"] = story_cache["reported_graphs"]                                                
        story_data["reported_graphs"].append(latest_graph)                                                    
        cache_stories[c_indx] = story_data                 
        return(True)    

def console_log_stories(cache_stories):
    
    logger.info('\nAll Stories:\n')
    for story in cache_stories:    
        story_id = story["story_id"]
        reported_graphs = story["reported_graphs"]

        formatted_story = pretty_print_graph(story_id, reported_graphs[-1], '')
        for k,v in formatted_story.items(): 
            logger.info(f'\t{k}: {v}')

        if len(reported_graphs) > 1:    
            logger.info(f'\t\tHistory:')
            for i in range( len(reported_graphs)-1 ):
                formatted_story = pretty_print_graph(story_id, reported_graphs[i], '{}. '.format(i+1))
                for k,v in formatted_story.items():
                    if k!="Story ID": 
                        logger.info(f'\t\t\t{k}: {v}')
                logger.info('')        
        logger.info('')

def setup_storage(stories_path):

    try:
        os.makedirs( stories_path + '/cache', exist_ok=True )
        os.makedirs( stories_path + '/tmp', exist_ok=True )
        os.makedirs( stories_path + '/tracked_stories', exist_ok=True )
    except:
        generic_error_info()
        return False

    return True

def transfer_dets_frm_maxgraphs_to_story_clusters(sggraph):

    if( 'maxgraphs' not in sggraph ):
        logger.error('maxgraphs not in sggraph, returning')
        return 

    if( 'story_clusters' not in sggraph ):
        logger.error('story_clusters not in sggraph, returning')
        return

    for date, payload in sggraph['story_clusters'].items():
        for i in range( len(payload['stories']) ):
            for j in range( len(payload['stories'][i]['graph_ids']) ):
                
                main_graph = payload['stories'][i]['graph_ids'][j]
                indx = main_graph['maxgraph_idx']
                
                if( indx >= len(sggraph['maxgraphs'][date]['graphs']) ):
                    continue

                clone_graph = sggraph['maxgraphs'][date]['graphs'][indx]
                if( main_graph['graph_uri'] != clone_graph['graph_uri'] ):
                    continue

                #copy - start
                main_graph['max_node_link'] = clone_graph['max_connected_comp_dets']['max_node_link']
                #copy - end


def sgbot(sgbot_path, activation_degree, overlap_threshold, top_stories_count, start_datetime, end_datetime, **kwargs):

    if( setup_storage(sgbot_path) is False ):
        return {}

    sgbot_path = sgbot_path.strip()
    sgbot_path = sgbot_path[:-1] if sgbot_path.endswith('/') else sgbot_path
    logger.info(f'Sgbot Path: {sgbot_path}\nActivation degree: {activation_degree}\nOverlap threshold: {overlap_threshold}\nTop stories count: {top_stories_count}')

    sg_stories = get_storygraph_stories(sgbot_path, start_datetime, end_datetime)
    if 'story_clusters' not in sg_stories:
        logger.info('No stories returned by storygraph-toolkit')
        return {}

    kwargs.setdefault('update_cache', True)#cache is updated by default, but could be delayed (update_cache=False) when user (post tweet) needs to add information before cache is updated. User must ensure cache is updated
    kwargs.setdefault('keep_history', False)
    transfer_dets_frm_maxgraphs_to_story_clusters( sg_stories )

    cur_story_date = list(sg_stories["story_clusters"])[0]      
    cache = get_cache(sgbot_path, cur_story_date)
    cache_stories = cache[cur_story_date]['stories']
    stories = sg_stories["story_clusters"][cur_story_date]["stories"]    

    #match stories
    map_cachestories = map_cache_stories(sgbot_path, overlap_threshold, cache, sg_stories, cur_story_date, end_datetime, keep_history=kwargs['keep_history'])
    
    #update tracking stories
    updated_ids = update_handler(sgbot_path, cache_stories, stories, map_cachestories, enable_post_story=kwargs['keep_history'])    
    logger.info(f'Updates of previous stories: {updated_ids}')

    #new top story    
    new_story_ids = newstory_handler(sgbot_path, cache_stories, stories, map_cachestories, top_stories_count, activation_degree, cur_story_date, **kwargs)
    logger.info(f'New top story ids: {new_story_ids}')

    #dump_cache 
    cache_path = f'{sgbot_path}/cache/cache_{cur_story_date}.json'
    cache[cur_story_date]["end_datetime"] = sg_stories["end_date"]
    cache[cur_story_date]['self'] = kwargs.get('self_cmd', '')

    if( kwargs['update_cache'] is True ):
        dump_json_to_file( cache_path, cache, indent_flag=False, extra_params={'verbose': False} ) 
    else:
        logger.warning(f'Warning: Cache not update since update_cache is False, ensure to update cache to avoid application failure during next run.')

    #print stories on console
    console_log_stories(cache_stories)
    if( kwargs['keep_history'] is False ):
        rm_all_but_yesterday_today_cache(sgbot_path, cur_story_date)

    return {
        'new_story_ids': new_story_ids,
        'updated_ids': updated_ids,
        'cache_stories': cache,
        'cache_path': cache_path
    }



