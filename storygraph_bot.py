#!/usr/bin/env python3
import sys
import os
import os.path
import json
from datetime import datetime
import argparse


def get_data(start,end):
	cmd = ('sgtk --pretty-print -o graphs_tmp/current_storygraphdata.json maxgraph --cluster-stories-by="max_avg_degree" --cluster-stories --start-datetime="'+start+'" --end-datetime="'+end+'" > graphs_tmp/console_output.log  2>&1')
	a = os.system(cmd)
	read_file = open("graphs_tmp/current_storygraphdata.json", "r")
	data = json.load(read_file)
	return data

def get_cache(date):
	cache_filename = "cache/"+'cache_'+date
	if os.path.isfile(cache_filename):
		cache = json.load(open(cache_filename, "r"))
		#print("cache exists")
	else:
		cache = new_cache(date)
		print("new cache initiated")
	return(cache)

def new_cache(date):
	#current_date = datetime.today().strftime('%Y-%m-%d')
	current_date = date
	#current_datetime = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
	cache = {
			current_date: {  
				"start_datetime": current_date+' 00:00:00',
				#"end_datetime": "",
				#"no_of_updates": init 0 then inc++,
				"stories": [
					]
				}
			}
	return(cache)


def overlap_stories(first, second):
	#first, second = set(first), set(second) 
	intersection = float(len(first & second))
	minimum = min(len(first), len(second))
	if( minimum != 0 ):
		return round(intersection/minimum, 4)
	else:
		return 0 

def get_stories_uri_datetimes(jdata): 
	stories_uri_datetimes = []
	for story in jdata[date]["stories"]:
		story_uri_datetimes = set([graph["graph_uri_local_datetime"] for graph in story["graph_ids"]])
		stories_uri_datetimes.append(story_uri_datetimes)
	return(stories_uri_datetimes)

def map_cache_stories(cache, data, overlap_threshold):
	map_cachestories = {}	
	topstory_incache = True
	#extract graph_uri_local_datetime from data(list of list) 
	stories_uri_dts =  get_stories_uri_datetimes(data["story_clusters"])
	cachedstories_uri_dts = get_stories_uri_datetimes(cache)
	if cachedstories_uri_dts == []	:
		print("empty cache")
		topstory_incache = False
	else:
		for sn in range(len(stories_uri_dts)):
			s_uridt = stories_uri_dts[sn]
			coeff_list = [overlap_stories(cs_uridt, s_uridt) for cs_uridt in cachedstories_uri_dts]
			maxcoeff = max(coeff_list) 
			if maxcoeff >= overlap_threshold:
				c_indx = coeff_list.index(maxcoeff)
				supdate = s_uridt - cachedstories_uri_dts[c_indx]	
				map_cachestories.update({c_indx: [sn, supdate]})
			elif sn == 0:
				topstory_incache = False
				print("top story is not in cache")
			if len(map_cachestories) == len(cachedstories_uri_dts):
				break
	return(map_cachestories, topstory_incache)


def get_topstory(activation_degree, stories, date):
	top_story = stories[0]		
	#check activation degree
	c = top_story["max_avg_degree"] > activation_degree
	if c:
		return(top_story)
	else:
		print("No top story")


def new_story(date, top_story, cache_stories):
	story_no = len(cache_stories)
	top_story["topstory_no"] = story_no
	cache_stories.append(top_story) 
	story_graph = top_story["graph_ids"][0]	
	print("Creating 1 new thread for new top story (Story"+ str(story_no)+")")			
	print_story(date, story_no, story_graph) #print top graph of top_story


def update_story(date, story_no, story_cache, story_data, update):
	cache_graphs = story_cache["graph_ids"]
	story_graphs = story_data["graph_ids"]
	print("updating the thread for the Story"+str(story_no))
	if story_graphs[0] != cache_graphs[0]:
		print("Average degree for Story"+str(story_no)+" has increased") #the avg degree is increased
		latest_graph = story_graphs[0]
	else: #top snapshot hasnt changed
		latest_graph_uri = sorted(update, reverse=True)[0]
		latest_story_graphs = [dic for dic in story_graphs if dic["graph_uri_local_datetime"]==latest_graph_uri] 
		l_id = sorted(latest_story_graphs, key=lambda k: int(k['id'].split("-")[1]), reverse=True) #id used identify graphs
		latest_graph = l_id[0]
		if "reported_graph" in story_cache:
			if story_cache["reported_graph"]["avg_degree"] < latest_graph["avg_degree"]:
				print("Average degree for Story"+str(story_no)+" has increased") #the avg degree is increased
			else:
				print("Average degree for Story"+str(story_no)+" has decreased")
		else:
			print("Average degree for Story"+str(story_no)+" has decreased") #the avg degree is decreased
	print_story(date, story_no, latest_graph)
	return(latest_graph)	


def print_story(date, story_no, story_graph):
	story_fname = "output/"+date+"_story"+str(story_no)+".txt"
	info =  ['avg_degree','graph_uri', 'max_node_title']
	if os.path.exists(story_fname):
		mode = 'a+' 
	else:
		mode = 'w+'
	story_file = open(story_fname, mode)
	print("")	
	for k,v in sorted(story_graph.items()): 
		if k in info:
			print("{}: {}".format(k,v))
			story_file.write("{}:{}\n".format(k,v))			
	story_file.write("\n")
	#print("")

def get_generic_args():
    parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30), description='Query StoryGraphbot')
    parser.add_argument('--start-datetime', default='', help='"YYYY-mm-DD HH:MM:SS" datetime for filtering graphs based on datetime')
    parser.add_argument('--end-datetime', default='', help='"YYYY-mm-DD HH:MM:SS" datetime for filtering graphs based on datetime')    
    parser.add_argument('-a','--activation-degree', dest='activation_degree', default= 5.0, type=float, help='The criteria for filtering top stories of the day')
    parser.add_argument('-ol','--overlap-threshold', default=0.9, type=float, help='The criteria for matching two stories')
    return parser


if __name__ == "__main__":
	args = get_generic_args().parse_args()
	data = get_data(args.start_datetime, args.end_datetime)
	date = list(data["story_clusters"])[0] 
	cache = get_cache(date)
	map_cachestories, st0_incache = map_cache_stories(cache, data, args.overlap_threshold)
	stories = data["story_clusters"][date]["stories"]	
	if stories == []:
		sys.exit("No stories in the new data")
	top_story = get_topstory(args.activation_degree,stories, date)
	print("Activation degree: "+str(args.activation_degree))
	print("Overlap threshold: "+str(args.overlap_threshold))
	cache_stories = cache[date]['stories']
	if top_story:		
		if not st0_incache or not map_cachestories: 			#add story to cache
			new_story(date, top_story, cache_stories)

	print("\nTotal threads: "+str(len(cache_stories))+"\n") 
	if map_cachestories:   		#{cache_story_index: [data_story_index, data_story_update]}
		#print(map_cachestories)
		print("Updating Stories ...")
		for cache_sidx, data_story in map_cachestories.items():
			story_cache = cache_stories[cache_sidx]
			story_no = story_cache["topstory_no"]
			data_sidx, update = data_story
			if update:
				story_data = data["story_clusters"][date]["stories"][data_sidx] 				#get story's current update from data
				story_data["topstory_no"] = story_no				
				latest_graph = update_story(date, story_no, story_cache, story_data, update) 
				story_data["reported_graph"] = latest_graph 
				cache_stories[cache_sidx] = story_data 				#update_cache					
			else:
				print("No new graphs for Story"+str(story_no))

	if len(map_cachestories) < len(cache_stories):
		print("\nThere are no updates on the other stories")
 			
				
	#dump_cache 
	json.dump(cache, open('cache/cache_'+date, 'w'))	
