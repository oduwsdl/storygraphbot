import json
import logging
import os
import sys

logger = logging.getLogger('sgbot.sgbot')

def generic_error_info(slug=''):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    
    err_msg = fname + ', ' + str(exc_tb.tb_lineno)  + ', ' + str(sys.exc_info())
    logger.error(err_msg + slug)

    return err_msg

def get_storygraph_stories(sgbot_path, start_datetime, end_datetime):
    try:
        cmd = (f'sgtk --pretty-print -o {sgbot_path}/tmp/current_storygraphdata.json maxgraph --cluster-stories-by="max_avg_degree" --cluster-stories --start-datetime="{start_datetime}" --end-datetime="{end_datetime}" > {sgbot_path}/tmp/console_output.log  2>&1')
        a = os.system(cmd)
        read_file = open(f"{sgbot_path}/tmp/current_storygraphdata.json", "r")
        data = json.load(read_file)
    except FileNotFoundError as e:
        sys.exit('Please install storygraph-toolkit: https://github.com/oduwsdl/storygraph-toolkit.git')
    return(data)

def check_cache_exist(sgbot_path, date):
    cache_filename = f'{sgbot_path}/cache/cache_{date}.json'
    if os.path.isfile(cache_filename):
        cache = json.load(open(cache_filename, "r"))
        return(cache)
    else:
        return(False)    

def get_cache(sgbot_path, date):
    cache = check_cache_exist(sgbot_path, date)
    if not cache:
        cache = create_new_cache(date)
        #print("New cache initiated")
    return(cache)

def create_new_cache(date):
    #current_date = datetime.today().strftime('%Y-%m-%d')
    current_date = date
    #current_datetime = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    cache = {
        current_date: {  
            "start_datetime": current_date + ' 00:00:00',
            "end_datetime": "",
            "stories": []
        }
    }
    return(cache)

def overlap_stories(first, second):
    #first, second = set(first), set(second) 
    intersection = float(len(first & second))
    minimum = min(len(first), len(second))
    if( minimum != 0 ):
        return(round(intersection/minimum, 4))
    else:
        return(0) 

def pretty_print_graph(story_id, story_graph):
    #format graph
    formatted_graph = {
        "Story ID" : story_id,
        "Title" : story_graph['max_node_title'],        
        "Avg Degree" : story_graph['avg_degree'],
        "Graph URI": story_graph['graph_uri']
    }    
    return(formatted_graph)

def post_story(sgbot_path, story_id, story_graph):
    '''Post story to file'''
    story_fname = f'{sgbot_path}/tracked_stories/{story_id}.txt'
    if os.path.exists(story_fname):
        mode = 'a+' 
    else:
        mode = 'w+'
    story_file = open(story_fname, mode)

    #format graph
    formatted_graph = pretty_print_graph(story_id, story_graph)    

    #print story to file        
    for k,v in formatted_graph.items(): 
        story_file.write("{}:{}\n".format(k,v))            
    story_file.write("\n")