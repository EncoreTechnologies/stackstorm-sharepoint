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

import mock

from st2tests.base import BaseActionTestCase
from lib.base_action import SharepointBaseAction
from st2common.runners.base_action import Action
# Using this to run tests. Otherwise get an error for no run method.
from sites_list import SitesList


class SharePointBaseActionTestCase(BaseActionTestCase):
    __test__ = True
    action_cls = SitesList

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, SharepointBaseAction)
        self.assertIsInstance(action, Action)

    @mock.patch('lib.base_action.SharepointBaseAction.rest_request')
    def test_get_doc_libs(self, mock_request):
        action = self.get_action_instance({})

        test_base_url = 'https://test.com/api'
        test_auth = 'user'

        # This endpoint is hard coded in base_action.py
        endpoint_uri = '/_api/web/lists?$filter=BaseTemplate eq ' \
                       '101&$select=Title,Id,DocumentTemplateUrl'

        expected_result = 'doc_lib'

        rest_result = {
            'd': {
                'results': expected_result
            }
        }

        mock_request.return_value = mock.MagicMock()
        mock_request.return_value.json.return_value = rest_result

        result = action.get_doc_libs(test_base_url, test_auth)

        self.assertEqual(result, expected_result)
        mock_request.assert_called_with(test_base_url + endpoint_uri, test_auth)

    @mock.patch('lib.base_action.requests.request')
    def test_rest_request(self, mock_request):
        action = self.get_action_instance({})

        test_headers = {
            'accept': 'application/json;odata=verbose',
            'content-type': 'application/json;odata=verbose',
            'odata': 'verbose',
            'X-RequestForceAuthentication': 'true'
        }

        test_endpoint = 'https://test.com/api/endpoint'
        test_auth = 'user'
        test_payload = {'data': 'test'}
        test_method = 'POST'
        test_verify = False

        expected_result = 'response'

        mock_request.return_value = expected_result

        result = action.rest_request(test_endpoint, test_auth, test_method,
                                     test_payload, test_verify)

        self.assertEqual(result, expected_result)
        mock_request.assert_called_with(test_method, test_endpoint,
                                        auth=test_auth, data=test_payload,
                                        headers=test_headers, verify=test_verify)

    @mock.patch('lib.base_action.HttpNtlmAuth')
    def test_create_auth_cred(self, mock_auth):
        action = self.get_action_instance({})

        test_domain = 'dom'
        test_pass = 'pass'
        test_user = 'user'
        test_auth = 'auth'

        mock_auth.return_value = test_auth

        result = action.create_auth_cred(test_domain, test_user, test_pass)

        self.assertEqual(result, test_auth)
        mock_auth.assert_called_with(test_domain + '\\' + test_user, test_pass)

    @mock.patch("lib.base_action.json")
    @mock.patch("lib.base_action.open")
    def test_save_sites_list_to_file_append(self, mock_open, mock_json):
        action = self.get_action_instance({})

        test_site_objs = ['site1', 'site2']
        test_file_path = '/path/to/sites_file.json'
        test_file_append = True
        expected_result = 'Output saved to: ' + test_file_path

        m = mock.mock_open(read_data='test data')
        mock_open.return_value = m.return_value
        mock_json.loads.return_value = ['site3', 'site4']

        result = action.save_sites_list_to_file(test_site_objs, test_file_path, test_file_append)

        self.assertEqual(result, expected_result)
        mock_json.loads.assert_called_with('test data')
        mock_json.dump.assert_called_with(['site3', 'site4', 'site1', 'site2'], m.return_value)
        mock_open.assert_has_calls(
            [mock.call(test_file_path, 'r'),
             mock.call(test_file_path, 'w')])

    @mock.patch("lib.base_action.json")
    @mock.patch("lib.base_action.open")
    def test_save_sites_list_to_file_overwrite(self, mock_open, mock_json):
        action = self.get_action_instance({})

        test_site_objs = ['site1', 'site2']
        test_file_path = '/path/to/sites_file.json'
        test_file_append = False
        expected_result = 'Output saved to: ' + test_file_path

        m = mock.mock_open(read_data='test data')
        mock_open.return_value = m.return_value

        result = action.save_sites_list_to_file(test_site_objs, test_file_path, test_file_append)

        self.assertEqual(result, expected_result)
        mock_json.dump.assert_called_with(['site1', 'site2'], m.return_value)
        mock_open.assert_called_with(test_file_path, 'w')
