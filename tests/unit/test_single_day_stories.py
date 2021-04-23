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
        
        start_datetime = "2020-06-10 00:00:00" 
        end_datetime = "2020-06-10 06:00:00"
        stories = sgbot(TestSGBot.sgbot_path, TestSGBot.activation_degree, TestSGBot.overlap_threshold, start_datetime, end_datetime)
        
        for ky in ['new_story_id', 'updated_ids', 'cache_stories', '2020-06-10']:
            self.assertTrue( ky in stories, f'"{ky}" not in stories' )
        
        
        print( stories['new_story_id'] )
        print( stories['updated_ids'] )
        stories['cache_stories']['2020-06-10'].keys()
        
        #self.assertTrue( 'new_story_id' in stories, '"new_story_id" not in stories' )
        #self.assertGreater( sumgrams['ranked_docs'][0]['score'], 0, "sumgrams['ranked_docs'][0]['score']" )
        #self.assertGreater( sumgrams['ranked_sentences'][0]['avg_overlap'], 0, "sumgrams['ranked_sentences'][0]['avg_overlap']" )


if __name__ == '__main__':
    unittest.main()