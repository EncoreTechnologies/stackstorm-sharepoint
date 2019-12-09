#!/usr/bin/env python
# Copyright 2019 Encore Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from test_action_lib_base_action import SharePointBaseActionTestCase
from sites_list import SitesList
import mock


class SharepointSitesListTest(SharePointBaseActionTestCase):
    __test__ = True
    action_cls = SitesList

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, SitesList)

    @mock.patch('sites_list.urlparse.urljoin')
    @mock.patch('lib.base_action.SharepointBaseAction.rest_request')
    def test_get_sites_list(self, mock_request, mock_urljoin):
        action = self.get_action_instance({})

        test_base_url = 'https://test.com/'
        test_auth = 'user'
        # The following variable is hard coded in the sites_list action
        endpoint_uri = '/_api/search/query?querytext=\'contentclass:STS_Site\''
        test_urljoin = 'https://test.com/_api/search/query?querytext=\'contentclass:STS_Site\''
        test_site1 = 'https://test.com/endpoint1'
        test_site2 = 'https://test.com/endpoint2'

        test_cells = [{'Key': 'TestKey', 'Value': 'TestValue'},
                      {'Key': 'SiteName', 'Value': test_site1},
                      {'Key': 'SiteName', 'Value': test_site2}]

        rest_result = {'d':
                       {'query':
                        {'PrimaryQueryResult':
                         {'RelevantResults':
                          {'Table':
                           {'Rows':
                            {'results':
                             [{'Cells':
                              {'results': test_cells}}]}}}}}}}

        # The expected result should be the same as the rest_result with 2
        # additional variables
        expected_result = [test_site1, test_site2]

        mock_request.return_value = mock.MagicMock()
        mock_request.return_value.json.return_value = rest_result

        mock_urljoin.return_value = test_urljoin

        result = action.get_sites_list(test_base_url, test_auth)

        self.assertEqual(result, expected_result)
        mock_request.assert_called_with(test_urljoin, test_auth)
        mock_urljoin.assert_called_with(test_base_url, endpoint_uri)

    @mock.patch('lib.base_action.SharepointBaseAction.get_doc_libs')
    @mock.patch('lib.base_action.SharepointBaseAction.rest_request')
    def test_get_site_objects(self, mock_request, mock_get_doc_libs):
        action = self.get_action_instance({})

        test_base_url = 'https://test.com'
        test_auth = 'user'
        # The following variable is hard coded in the sites_list action
        endpoint_uri = '/_api/site/rootweb'

        test_site_urls = ['https://test.com/endpoint1',
                          'https://test.com/endpoint2']

        # test sharepoint site objects
        site1 = {
            'Id': '1234',
            'ServerRelativeUrl': '/endpoint1'
        }
        site2 = {
            'Id': '6789',
            'ServerRelativeUrl': '/endpoint2'
        }

        mock_request.return_value = mock.MagicMock()
        mock_request.return_value.json.side_effect = [
            {'d': site1},
            {'d': site2}
        ]

        # These parent IDs will get added to the site objects and
        # are in the expected result
        mock_get_doc_libs.side_effect = ['doc1', 'doc2']

        # Add parent IDs and site URLs to the site objects
        expected_result = [
            {
                'Id': '1234',
                'DocLibs': 'doc1',
                'Endpoint': '/endpoint1',
                'ParentId': None,
                'ServerRelativeUrl': '/endpoint1',
                'SiteUrl': 'https://test.com/endpoint1'
            },
            {
                'Id': '6789',
                'DocLibs': 'doc2',
                'Endpoint': '/endpoint2',
                'ParentId': None,
                'ServerRelativeUrl': '/endpoint2',
                'SiteUrl': 'https://test.com/endpoint2'
            }
        ]

        result = action.get_site_objects(test_base_url, test_auth, test_site_urls)

        self.assertEqual(result, expected_result)
        mock_request.assert_has_calls([
            mock.call('https://test.com/endpoint1' + endpoint_uri, test_auth),
            mock.call('https://test.com/endpoint2' + endpoint_uri, test_auth),
            mock.call().json()
        ], any_order=True)
        # The get_doc_libs function should be called once for every site
        mock_get_doc_libs.assert_has_calls([
            mock.call('https://test.com/endpoint1', test_auth),
            mock.call('https://test.com/endpoint2', test_auth)
        ])

    @mock.patch('sites_list.SitesList.get_sites_list')
    @mock.patch('sites_list.SitesList.get_site_objects')
    @mock.patch('sites_list.HttpNtlmAuth')
    def test_run(self, mock_auth, mock_get_site_objects, mock_get_sites_list):
        action = self.get_action_instance({})

        test_base_url = 'https://test.com/'
        test_domain = 'dom'
        test_pass = 'pass'
        test_user = 'user'
        test_auth = 'auth'
        test_site_list = ['site1', 'site2']

        expected_result = 'result'

        mock_auth.return_value = test_auth

        mock_get_site_objects.return_value = expected_result
        mock_get_sites_list.return_value = test_site_list

        result = action.run(test_base_url, test_domain, test_pass, test_user)

        self.assertEqual(result, expected_result)
        mock_auth.assert_called_with(test_domain + '\\' + test_user, test_pass)
        mock_get_sites_list.assert_called_with(test_base_url, test_auth)
        mock_get_site_objects.assert_called_with(test_base_url, test_auth, test_site_list)
