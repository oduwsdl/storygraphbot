import json
import logging
import os
import sys

logger = logging.getLogger('sgbot.sgbot')

def proc_log_handler(handler, logger_dets):
    
    if( handler is None ):
        return
        
    if( 'level' in logger_dets ):
        handler.setLevel( logger_dets['level'] )    
        
        if( logger_dets['level'] == logging.ERROR ):
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s :\n%(message)s')
            handler.setFormatter(formatter)

    if( 'format' in logger_dets ):
        
        logger_dets['format'] = logger_dets['format'].strip()
        if( logger_dets['format'] != '' ):
            formatter = logging.Formatter( logger_dets['format'] )
            handler.setFormatter(formatter)

    logger.addHandler(handler)

def set_logger_dets(logger, logger_dets):

    if( len(logger_dets) == 0 ):
        return

    console_handler = logging.StreamHandler()

    if( 'level' in logger_dets ):
        logger.setLevel( logger_dets['level'] )
    else:
        logger.setLevel( logging.INFO )

    if( 'file' in logger_dets ):
        logger_dets['file'] = logger_dets['file'].strip()
        
        if( logger_dets['file'] != '' ):
            file_handler = logging.FileHandler( logger_dets['file'] )
            proc_log_handler(file_handler, logger_dets)

    proc_log_handler(console_handler, logger_dets)

def set_log_defaults(params):
    
    params['log_dets'] = {}

    if( params['log_level'] == '' ):
        params['log_dets']['level'] = logging.INFO
    else:
        
        log_levels = {
            'CRITICAL': 50,
            'ERROR': 40,
            'WARNING': 30,
            'INFO': 20,
            'DEBUG': 10,
            'NOTSET': 0
        }

        params['log_level'] = params['log_level'].strip().upper()

        if( params['log_level'] in log_levels ):
            params['log_dets']['level'] = log_levels[ params['log_level'] ]
        else:
            params['log_dets']['level'] = logging.INFO
    
    params['log_format'] = params['log_format'].strip()
    params['log_file'] = params['log_file'].strip()

    if( params['log_format'] != '' ):
        params['log_dets']['format'] = params['log_format']

    if( params['log_file'] != '' ):
        params['log_dets']['file'] = params['log_file']

def generic_error_info(slug=''):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    
    err_msg = fname + ', ' + str(exc_tb.tb_lineno)  + ', ' + str(sys.exc_info())
    logger.error(err_msg + slug)

    return err_msg

def get_dct_frm_json(json_str):
    try:
        return json.loads(json_str)
    except:
        generic_error_info('\tError: json_str prefix: ' + json_str[:100])
    return {}

def read_txt_frm_file(infilename):
    
    text = ''
    try:
        with open(infilename, 'r') as infile:
            text = infile.read()
    except:
        generic_error_info('\tError: read_txt_frm_file() filename: ' + infilename)
    
    return text

def get_dict_frm_file(filename):

    try:
        if( os.path.exists(filename) is False ):
            return {}
        return get_dct_frm_json( read_txt_frm_file(filename) )
    except:
        generic_error_info('\tError: get_dict_frm_file(): filename ' + filename)
    return {}

def dump_json_to_file(outfilename, dict_to_write, indent_flag=True, extra_params=None):

    if( extra_params is None ):
        extra_params = {}

    extra_params.setdefault('verbose', True)

    try:
        outfile = open(outfilename, 'w')
        
        if( indent_flag is True ):
            json.dump(dict_to_write, outfile, ensure_ascii=False, indent=4)#by default, ensure_ascii=True, and this will cause  all non-ASCII characters in the output are escaped with \uXXXX sequences, and the result is a str instance consisting of ASCII characters only. Since in python 3 all strings are unicode by default, forcing ascii is unecessary
        else:
            json.dump(dict_to_write, outfile, ensure_ascii=False)

        outfile.close()

        if( extra_params['verbose'] is True ):
            logger.info('\tdump_json_to_file(), wrote: ' + outfilename)
    except:
        generic_error_info('\n\tError: outfilename: ' + outfilename)
        return False

    return True



def get_storygraph_stories(sgbot_path, start_datetime, end_datetime):
    
    data = {}
    try:
        cmd = (f'sgtk --pretty-print -o {sgbot_path}/tmp/current_storygraphdata.json maxgraph --cluster-stories-by="max_avg_degree" --cluster-stories --start-datetime="{start_datetime}" --end-datetime="{end_datetime}" > {sgbot_path}/tmp/console_output.log  2>&1')
        a = os.system(cmd)
        data = get_dict_frm_file( f"{sgbot_path}/tmp/current_storygraphdata.json" )
    except FileNotFoundError as e:
        logger.error('Please install storygraph-toolkit: https://github.com/oduwsdl/storygraph-toolkit.git')
    
    return(data)

def check_cache_exist(sgbot_path, date):
    cache_filename = f'{sgbot_path}/cache/cache_{date}.json'
    cache = get_dict_frm_file(cache_filename)
    if( len(cache) == 0 ):
        return(False)
    else:
        return(cache)  

def get_cache(sgbot_path, date):
    cache = check_cache_exist(sgbot_path, date)
    if not cache:
        cache = create_new_cache(date)
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
    story_file.close()