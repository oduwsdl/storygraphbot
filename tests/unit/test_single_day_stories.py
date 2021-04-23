import json
import unittest

from storygraph_bot.backbone import sgbot
from storygraph_bot.util import cleanup

class TestSGBot(unittest.TestCase):
    
    sgbot_path = '/tmp/SGBOT_TEST_PATH'
    activation_degree = 0
    overlap_threshold = 0.9

    def generic_tester(self, test_cases):

        def test_template():

            if( run_cleanup is True ):
                cleanup(TestSGBot.sgbot_path, verify_deletion=False)
            
            if( run_sgbot is True ):
                stories = sgbot(TestSGBot.sgbot_path, TestSGBot.activation_degree, TestSGBot.overlap_threshold, start_datetime, end_datetime)
            else:
                stories = prev_stories

            for ky in ['new_story_id', 'updated_ids', 'cache_stories']:
                self.assertTrue( ky in stories, f'"{ky}" not in stories' )
            
            self.assertTrue( stories['new_story_id'] == expected_new_story_id, f'"{expected_new_story_id}" not new_story_id' )
            self.assertTrue( stories['updated_ids'] == expected_updated_ids, 'expected_updated_ids MISMATCH, expected: "' + str(expected_updated_ids) + '", got: "'+ str(stories['updated_ids']) +'"' )
            res_g_uri = stories['cache_stories'][story_indx]['reported_graphs'][-1]['graph_uri']
            self.assertTrue( res_g_uri == expected_g_uri, f'graph_uri MISMATCH, expected: {expected_g_uri}, got: {res_g_uri}' )
            
            print('\nPassed Test !!! :)')
            print('\tNew Story ID:', expected_new_story_id)
            print('\tUpdated IDs:', expected_updated_ids)
            print('\tGraph URI:', expected_g_uri)
            print()

            return stories

        for c in test_cases:

            run_cleanup = c.get('run_cleanup', False)
            run_sgbot = c.get('run_sgbot', True)

            start_datetime = c['start_datetime']
            end_datetime = c['end_datetime']
            expected_new_story_id = c['expected_new_story_id']
            expected_updated_ids = c['expected_updated_ids']

            story_indx = c['story_indx']
            expected_g_uri = c['expected_g_uri']
            prev_stories = test_template()

    def test_multi_day_stories(self):

        cases = [
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 01:00:00',
                'expected_new_story_id': '20201006_0',
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=26&hist=1440&t=2020-10-06T04:20:07'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201006_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=37&hist=1440&t=2020-10-06T06:11:01'
            },
        ]

        cleanup(TestSGBot.sgbot_path, verify_deletion=False)
        self.generic_tester(cases)


    def test_single_day_stories(self):

        cases = [
            {
                'start_datetime': '2020-06-10 00:00:00',
                'end_datetime': '2020-06-10 06:00:00',
                'expected_new_story_id': '20200610_0',
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=24&hist=1440&t=2020-06-10T04:05:38'
            },
            {
                'start_datetime': '2020-06-10 00:00:00',
                'end_datetime': '2020-06-10 09:00:00',
                'expected_new_story_id': '20200610_1',
                'expected_updated_ids': None,
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=76&hist=1440&t=2020-06-10T12:47:07'
            },
            {
                'start_datetime': '2020-06-10 00:00:00',
                'end_datetime': '2020-06-10 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20200610_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=79&hist=1440&t=2020-06-10T13:17:17'
            },
            {

                'start_datetime': '2020-06-10 00:00:00',
                'end_datetime': '2020-06-10 15:00:00',
                'expected_new_story_id': '20200610_2',
                'expected_updated_ids': None,
                'story_indx': 2,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=103&hist=1440&t=2020-06-10T17:18:36'
            },
            {
                'start_datetime': '2020-06-10 00:00:00',
                'end_datetime': '2020-06-10 18:00:00',
                'expected_new_story_id': '20200610_3',
                'expected_updated_ids': '20200610_2',#the graph_uri of this story is NOT (story_indx = 3) tested since expected_g_uri assumes only one state
                'story_indx': 3,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2020-06-10T21:58:16'
            },
            {
                'run_sgbot': False,
                'start_datetime': '2020-06-10 00:00:00',
                'end_datetime': '2020-06-10 18:00:00',
                'expected_new_story_id': '20200610_3',
                'expected_updated_ids': '20200610_2',#the graph_uri of this story IS tested (story_indx = 2, expected_g_uri updated)
                'story_indx': 2,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=117&hist=1440&t=2020-06-10T19:38:46'
            },
            {
                'run_cleanup': True,
                'start_datetime': '2020-04-07 00:00:00',
                'end_datetime': '2020-04-07 06:00:00',
                'expected_new_story_id': '20200407_0',
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=26&hist=1440&t=2020-04-07T04:30:39'
            },
            {
                'start_datetime': '2020-04-07 00:00:00',
                'end_datetime': '2020-04-07 09:00:00',
                'expected_new_story_id': '20200407_1',
                'expected_updated_ids': '20200407_0',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=72&hist=1440&t=2020-04-07T12:11:37'
            },
            {
                'run_sgbot': False,
                'start_datetime': '2020-04-07 00:00:00',
                'end_datetime': '2020-04-07 09:00:00',
                'expected_new_story_id': '20200407_1',
                'expected_updated_ids': '20200407_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=66&hist=1440&t=2020-04-07T11:11:46'
            },
            {
                'start_datetime': '2020-04-07 00:00:00',
                'end_datetime': '2020-04-07 12:00:00',
                'expected_new_story_id': '20200407_2',
                'expected_updated_ids': '20200407_1',
                'story_indx': 2,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=92&hist=1440&t=2020-04-07T15:32:15'
            },
            {
                'run_sgbot': False,
                'start_datetime': '2020-04-07 00:00:00',
                'end_datetime': '2020-04-07 12:00:00',
                'expected_new_story_id': '20200407_2',
                'expected_updated_ids': '20200407_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2020-04-07T13:01:29'
            },
            {
                'start_datetime': '2020-04-07 00:00:00',
                'end_datetime': '2020-04-07 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20200407_2',
                'story_indx': 2,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=103&hist=1440&t=2020-04-07T17:22:39'
            },
            {
                'run_cleanup': True,
                'start_datetime': '2019-09-24 00:00:00',
                'end_datetime': '2019-09-24 06:00:00',
                'expected_new_story_id': '20190924_0',
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=25&hist=1440&t=2019-09-24T04:13:01'
            },
            {
                'start_datetime': '2019-09-24 00:00:00',
                'end_datetime': '2019-09-24 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20190924_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=75&hist=1440&t=2019-09-24T12:34:31'
            },
            {
                'start_datetime': '2019-09-24 00:00:00',
                'end_datetime': '2019-09-24 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20190924_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2019-09-24T15:53:28'
            },
            {
                'start_datetime': '2019-09-24 00:00:00',
                'end_datetime': '2019-09-24 15:00:00',
                'expected_new_story_id': '20190924_1',
                'expected_updated_ids': None,
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=113&hist=1440&t=2019-09-24T18:54:02'
            },
            {
                'start_datetime': '2019-09-24 00:00:00',
                'end_datetime': '2019-09-24 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20190924_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=129&hist=1440&t=2019-09-24T21:36:19'
            }
        ]

        cleanup(TestSGBot.sgbot_path, verify_deletion=False)
        self.generic_tester(cases)

if __name__ == '__main__':
    unittest.main()