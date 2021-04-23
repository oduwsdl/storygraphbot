import json
import unittest

from storygraph_bot.backbone import sgbot
from storygraph_bot.util import cleanup

class TestSGBot(unittest.TestCase):
    
    sgbot_path = '/tmp/SGBOT_TEST_PATH'
    activation_degree = 0
    overlap_threshold = 0.9
    def test_single_day_stories_script(self):

        cleanup(TestSGBot.sgbot_path, verify_deletion=False)
        def test_template():
            
            stories = sgbot(TestSGBot.sgbot_path, TestSGBot.activation_degree, TestSGBot.overlap_threshold, start_datetime, end_datetime)
            for ky in ['new_story_id', 'updated_ids', 'cache_stories']:
                self.assertTrue( ky in stories, f'"{ky}" not in stories' )
            
            self.assertTrue( stories['new_story_id'] == expected_new_story_id, f'"{expected_new_story_id}" not new_story_id' )
            self.assertTrue( stories['updated_ids'] is None, 'updated_ids has value, None expected' )
            res_g_uri = stories['cache_stories'][story_indx]['reported_graphs'][reported_graphs_indx]['graph_uri']
            self.assertTrue( res_g_uri == expected_g_uri, f'graph_uri MISMATCH, expected: {expected_g_uri}, got: {res_g_uri}' )
            

        start_datetime = '2020-06-10 00:00:00'
        end_datetime = '2020-06-10 06:00:00'
        expected_new_story_id = '20200610_0'

        story_indx = 0
        reported_graphs_indx = 0
        expected_g_uri = 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=24&hist=1440&t=2020-06-10T04:05:38'
        test_template()


        start_datetime = '2020-06-10 00:00:00'
        end_datetime = '2020-06-10 09:00:00'
        expected_new_story_id = '20200610_1'
        
        story_indx = 1
        reported_graphs_indx = 0
        expected_g_uri = 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=76&hist=1440&t=2020-06-10T12:47:07'
        test_template()



        #start_datetime = "2020-06-10 00:00:00" 
        #end_datetime = "2020-06-10 06:00:00"
        #stories = sgbot(TestSGBot.sgbot_path, TestSGBot.activation_degree, TestSGBot.overlap_threshold, start_datetime, end_datetime)

if __name__ == '__main__':
    unittest.main()