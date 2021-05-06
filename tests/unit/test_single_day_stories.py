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
            
            if( expected_new_story_id is None and expected_updated_ids is None ):
                return

            yyyy_mm_dd = list( stories['cache_stories'].keys() )[0]           
            res_g_uri = stories['cache_stories'][yyyy_mm_dd]['stories'][story_indx]['reported_graphs'][-1]['graph_uri']
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

    def test_multi_day_stories_part_1(self):

        cases = [
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 06:00:00',
                'expected_new_story_id': '20201002_0',
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=57&hist=1440&t=2020-10-02T09:34:49'
            },
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2020-10-02T12:55:40'
            },
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2020-10-02T15:55:57'
            },
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=102&hist=1440&t=2020-10-02T17:07:41'
            },
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2020-10-02T21:54:18'
            },
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2020-10-03T00:54:32'
            },
            {
                'start_datetime': '2020-10-02 00:00:00',
                'end_datetime': '2020-10-02 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2020-10-03T02:54:07'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=28&hist=1440&t=2020-10-03T04:45:37'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=56&hist=1440&t=2020-10-03T09:25:19'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=70&hist=1440&t=2020-10-03T11:46:12'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2020-10-03T15:56:43'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=113&hist=1440&t=2020-10-03T18:57:21'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2020-10-03T21:56:48'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2020-10-04T00:57:03'
            },
            {
                'start_datetime': '2020-10-03 00:00:00',
                'end_datetime': '2020-10-03 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2020-10-04T02:56:41'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=28&hist=1440&t=2020-10-04T04:46:44'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=31&hist=1440&t=2020-10-04T05:16:34'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2020-10-04T12:58:21'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2020-10-04T15:58:59'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=113&hist=1440&t=2020-10-04T18:58:56'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2020-10-04T21:59:58'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2020-10-05T00:59:07'
            },
            {
                'start_datetime': '2020-10-04 00:00:00',
                'end_datetime': '2020-10-04 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2020-10-05T02:58:47'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=29&hist=1440&t=2020-10-05T04:58:21'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=52&hist=1440&t=2020-10-05T08:49:32'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=76&hist=1440&t=2020-10-05T12:50:19'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=87&hist=1440&t=2020-10-05T14:40:11'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=112&hist=1440&t=2020-10-05T18:51:20'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=130&hist=1440&t=2020-10-05T21:50:45'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=141&hist=1440&t=2020-10-05T23:40:22'
            },
            {
                'start_datetime': '2020-10-05 00:00:00',
                'end_datetime': '2020-10-05 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2020-10-06T02:50:36'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=26&hist=1440&t=2020-10-06T04:20:07'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=37&hist=1440&t=2020-10-06T06:11:01'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2020-10-06T12:51:44'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2020-10-06T15:51:51'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=113&hist=1440&t=2020-10-06T18:52:49'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2020-10-06T21:53:24'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2020-10-07T00:52:54'
            },
            {
                'start_datetime': '2020-10-06 00:00:00',
                'end_datetime': '2020-10-06 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2020-10-07T02:51:58'
            },
            {
                'start_datetime': '2020-10-07 00:00:00',
                'end_datetime': '2020-10-07 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=26&hist=1440&t=2020-10-07T04:22:20'
            },
            {
                'start_datetime': '2020-10-07 00:00:00',
                'end_datetime': '2020-10-07 06:00:00',
                'expected_new_story_id': '20201007_1',
                'expected_updated_ids': '20201002_0',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=31&hist=1440&t=2020-10-07T05:13:12'
            },
            {
                'run_sgbot': False,
                'start_datetime': '2020-10-07 00:00:00',
                'end_datetime': '2020-10-07 06:00:00',
                'expected_new_story_id': '20201007_1',
                'expected_updated_ids': '20201002_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=58&hist=1440&t=2020-10-07T09:43:55'
            }
        ]

        cleanup(TestSGBot.sgbot_path, verify_deletion=False)
        self.generic_tester(cases)
        cleanup(TestSGBot.sgbot_path, verify_deletion=False)

    def test_multi_day_stories_part_2(self):

        cases = [
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 06:00:00',
                'expected_new_story_id': '20180929_0',
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=24&hist=1440&t=2018-09-29T04:00:24'
            },
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2018-09-29T12:51:09'
            },
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2018-09-29T15:51:58'
            },
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=113&hist=1440&t=2018-09-29T18:52:12'
            },
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2018-09-29T21:51:53'
            },
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2018-09-30T00:52:19'
            },
            {
                'start_datetime': '2018-09-29 00:00:00',
                'end_datetime': '2018-09-29 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2018-09-30T02:53:14'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=29&hist=1440&t=2018-09-30T04:53:11'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=59&hist=1440&t=2018-09-30T09:53:46'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2018-09-30T12:54:10'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=94&hist=1440&t=2018-09-30T15:44:29'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=98&hist=1440&t=2018-09-30T16:23:43'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=131&hist=1440&t=2018-09-30T21:54:25'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2018-10-01T00:54:43'
            },
            {
                'start_datetime': '2018-09-30 00:00:00',
                'end_datetime': '2018-09-30 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2018-10-01T02:55:44'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=24&hist=1440&t=2018-10-01T04:05:02'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 06:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=42&hist=1440&t=2018-10-01T07:06:19'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=66&hist=1440&t=2018-10-01T11:06:38'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=95&hist=1440&t=2018-10-01T15:56:10'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=102&hist=1440&t=2018-10-01T17:07:24'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=122&hist=1440&t=2018-10-01T20:28:30'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2018-10-02T00:57:26'
            },
            {
                'start_datetime': '2018-10-01 00:00:00',
                'end_datetime': '2018-10-01 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2018-10-02T02:58:08'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20180929_0',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=25&hist=1440&t=2018-10-02T04:17:31'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 06:00:00',
                'expected_new_story_id': '20181002_1',
                'expected_updated_ids': None,
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=47&hist=1440&t=2018-10-02T07:58:02'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 09:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20181002_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=77&hist=1440&t=2018-10-02T12:58:56'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 12:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20181002_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=94&hist=1440&t=2018-10-02T15:50:51'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 15:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20181002_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=102&hist=1440&t=2018-10-02T17:09:37'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 18:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': None,
                'story_indx': 0,
                'expected_g_uri': ''
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 21:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20181002_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=5&hist=1440&t=2018-10-03T00:49:57'
            },
            {
                'start_datetime': '2018-10-02 00:00:00',
                'end_datetime': '2018-10-02 23:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20181002_1',
                'story_indx': 1,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=17&hist=1440&t=2018-10-03T02:50:33'
            },
            {
                'start_datetime': '2018-10-03 00:00:00',
                'end_datetime': '2018-10-03 01:00:00',
                'expected_new_story_id': None,
                'expected_updated_ids': '20181002_1',
                'story_indx': 0,
                'expected_g_uri': 'http://storygraph.cs.odu.edu/graphs/polar-media-consensus-graph/#cursor=28&hist=1440&t=2018-10-03T04:40:36'
            }
        ]

        cleanup(TestSGBot.sgbot_path, verify_deletion=False)
        self.generic_tester(cases)
        cleanup(TestSGBot.sgbot_path, verify_deletion=False)

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
        cleanup(TestSGBot.sgbot_path, verify_deletion=False)

if __name__ == '__main__':
    unittest.main()