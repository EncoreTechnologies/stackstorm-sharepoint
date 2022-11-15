#!/usr/bin/env python
# Copyright 2022 Encore Technologies
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
from subsites_list import SubsitesList
import mock


class SharepointSubsitesListTest(SharePointBaseActionTestCase):
    __test__ = True
    action_cls = SubsitesList

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, SubsitesList)

    @mock.patch('subsites_list.urljoin')
    @mock.patch('lib.base_action.SharepointBaseAction.rest_request')
    def test_get_parent_site(self, mock_request, mock_urljoin):
        action = self.get_action_instance({})
        action.token_auth = False

        test_base_url = 'https://test.com/api'
        test_auth = 'user'
        test_subsite = '/test/subsite'
        test_id = '1234'

        # The following variable is hard coded in the sites_list action
        endpoint_uri = '/_api/web/parentweb'
        test_urljoin = 'https://test.com/api/test/subsite/_api/web/parentweb'

        expected_result = {
            'd': {
                'Id': test_id
            }
        }

        mock_request.return_value = mock.MagicMock()
        mock_request.return_value.json.return_value = expected_result

        mock_urljoin.return_value = test_urljoin

        result = action.get_parent_site(test_base_url, test_auth, test_subsite)

        self.assertEqual(result, test_id)
        mock_request.assert_called_with(test_urljoin, test_auth)
        mock_urljoin.assert_called_with(test_base_url, test_subsite + endpoint_uri)

    @mock.patch('subsites_list.SubsitesList.get_doc_libs')
    @mock.patch('subsites_list.SubsitesList.get_parent_site')
    @mock.patch('lib.base_action.SharepointBaseAction.rest_request')
    def test_get_sites_list(self, mock_request, mock_get_parent, mock_doc_libs):
        action = self.get_action_instance({})
        action.token_auth = False

        test_base_url = 'https://test.com'
        test_auth = 'user'
        # The following variable is hard coded in the sites_list action
        endpoint_uri = '/_api/web/getsubwebsfilteredforcurrentuser' \
                       '(nwebtemplatefilter=-1,nconfigurationfilter=0)'

        # test sharepoint site objects
        site1 = {
            'Id': '1234',
            'ServerRelativeUrl': '/endpoint1'
        }
        site2 = {
            'Id': '6789',
            'ServerRelativeUrl': '/endpoint2'
        }
        subsite1 = {
            'Id': '4321',
            'ServerRelativeUrl': '/subsite'
        }

        # Add a result for each rest_request
        mock_request.return_value = mock.MagicMock()
        mock_request.return_value.json.side_effect = [
            {'d': {'results': [site1, site2]}},
            {'d': {'results': []}},
            {'d': {'results': [subsite1]}},
            {'d': {'results': []}}
        ]

        # These parent IDs will get added to the site objects and
        # are in the expected result
        mock_get_parent.side_effect = ['p123', 'p987', 'p567']
        # These doc libs will also be in the result
        mock_doc_libs.side_effect = ['doc1', 'doc2', 'doc3']

        # Add parent IDs and site URLs to the site objects
        expected_result = [
            {
                'Id': '1234',
                'DocLibs': 'doc1',
                'ParentId': 'p123',
                'ServerRelativeUrl': '/endpoint1',
                'SiteUrl': 'https://test.com/endpoint1'
            },
            {
                'Id': '6789',
                'DocLibs': 'doc2',
                'ParentId': 'p987',
                'ServerRelativeUrl': '/endpoint2',
                'SiteUrl': 'https://test.com/endpoint2'
            },
            {
                'Id': '4321',
                'DocLibs': 'doc3',
                'ParentId': 'p567',
                'ServerRelativeUrl': '/subsite',
                'SiteUrl': 'https://test.com/subsite'
            }
        ]

        result = action.get_sites_list(test_base_url, test_auth)

        self.assertEqual(result, expected_result)
        mock_request.assert_has_calls([
            mock.call(test_base_url + endpoint_uri, test_auth),
            mock.call(test_base_url + '/endpoint1' + endpoint_uri, test_auth),
            mock.call(test_base_url + '/endpoint2' + endpoint_uri, test_auth),
            mock.call(test_base_url + '/subsite' + endpoint_uri, test_auth),
            mock.call().json()
        ], any_order=True)
        # The get_parent function should be called once for every site
        mock_get_parent.assert_has_calls([
            mock.call(test_base_url, test_auth, '/endpoint1'),
            mock.call(test_base_url, test_auth, '/endpoint2'),
            mock.call(test_base_url, test_auth, '/subsite')
        ])

    @mock.patch('subsites_list.SubsitesList.get_sites_list')
    @mock.patch('lib.base_action.SharepointBaseAction.create_ntlm_auth_cred')
    def test_run(self, mock_auth, mock_get_sites_list):
        action = self.get_action_instance({})
        action.token_auth = False

        test_base_url = 'https://test.com/'
        test_domain = 'dom'
        test_output_file = None
        test_output_file_append = False
        test_output_type = 'console'
        test_pass = 'pass'
        test_user = 'user'
        test_auth = 'auth'
        test_endpoint = 'endp1'
        test_rsa_private_key = 'rsa_test'
        test_cert_thumbprint = 'cert_test'
        test_tenent_id = '123abc'
        test_client_id = '456dfg'

        expected_result = ['result']

        mock_auth.return_value = test_auth
        mock_get_sites_list.return_value = expected_result

        result = action.run(test_base_url, test_domain, test_endpoint, test_output_file,
                            test_output_file_append, test_output_type, test_pass, test_user, False,
                            test_rsa_private_key, test_cert_thumbprint, test_tenent_id,
                            test_client_id)

        self.assertEqual(result, expected_result)
        mock_auth.assert_called_with(test_domain, test_user, test_pass)
        mock_get_sites_list.assert_called_with(test_base_url, test_auth, test_endpoint)

    @mock.patch('subsites_list.SubsitesList.get_sites_list')
    @mock.patch('lib.base_action.SharepointBaseAction.create_ntlm_auth_cred')
    @mock.patch('lib.base_action.SharepointBaseAction.save_sites_list_to_file')
    def test_run_file(self, mock_save, mock_auth, mock_get_sites_list):
        action = self.get_action_instance({})
        action.token_auth = False

        test_base_url = 'https://test.com/'
        test_domain = 'dom'
        test_output_file = '/path/to/sites_file.json'
        test_output_file_append = False
        test_output_type = 'file'
        test_pass = 'pass'
        test_user = 'user'
        test_auth = 'auth'
        test_endpoint = 'endp1'
        test_sites = ['site1', 'site2']
        test_rsa_private_key = 'rsa_test'
        test_cert_thumbprint = 'cert_test'
        test_tenent_id = '123abc'
        test_client_id = '456dfg'

        expected_result = 'result'

        mock_auth.return_value = test_auth
        mock_get_sites_list.return_value = test_sites
        mock_save.return_value = expected_result

        result = action.run(test_base_url, test_domain, test_endpoint, test_output_file,
                            test_output_file_append, test_output_type, test_pass, test_user, False,
                            test_rsa_private_key, test_cert_thumbprint, test_tenent_id,
                            test_client_id)

        self.assertEqual(result, expected_result)
        mock_auth.assert_called_with(test_domain, test_user, test_pass)
        mock_get_sites_list.assert_called_with(test_base_url, test_auth, test_endpoint)
        mock_save.assert_called_with(test_sites, test_output_file, test_output_file_append)
