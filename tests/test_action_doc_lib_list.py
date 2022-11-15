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
from doc_lib_list import DocLibList
import mock


class SharepointSitesListTest(SharePointBaseActionTestCase):
    __test__ = True
    action_cls = DocLibList

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, DocLibList)

    @mock.patch('lib.base_action.SharepointBaseAction.get_doc_libs')
    @mock.patch('lib.base_action.SharepointBaseAction.create_ntlm_auth_cred')
    def test_run(self, mock_auth, mock_get_doc_libs):
        action = self.get_action_instance({})

        test_site_url = 'https://test.com'
        test_domain = 'dom'
        test_output_file = None
        test_output_file_append = False
        test_output_type = 'console'
        test_pass = 'pass'
        test_user = 'user'
        test_auth = 'auth'
        test_rsa_private_key = 'rsa_test'
        test_cert_thumbprint = 'cert_test'
        test_tenent_id = '123abc'
        test_client_id = '456dfg'

        expected_result = 'result'

        mock_auth.return_value = test_auth

        mock_get_doc_libs.return_value = expected_result

        result = action.run(test_domain, test_output_file, test_output_file_append,
                            test_output_type, test_pass, test_site_url, test_user, False,
                            test_rsa_private_key, test_cert_thumbprint, test_tenent_id,
                            test_client_id)

        self.assertEqual(result, expected_result)
        mock_auth.assert_called_with(test_domain, test_user, test_pass)
        mock_get_doc_libs.assert_called_with(test_site_url, test_auth)

    @mock.patch('lib.base_action.SharepointBaseAction.get_doc_libs')
    @mock.patch('lib.base_action.SharepointBaseAction.create_ntlm_auth_cred')
    @mock.patch('lib.base_action.SharepointBaseAction.save_sites_list_to_file')
    def test_run_file(self, mock_save, mock_auth, mock_get_doc_libs):
        action = self.get_action_instance({})

        test_site_url = 'https://test.com/'
        test_domain = 'dom'
        test_output_file = '/path/to/sites_file.json'
        test_output_file_append = False
        test_output_type = 'file'
        test_pass = 'pass'
        test_user = 'user'
        test_auth = 'auth'
        test_doc_libs = ['doc1', 'doc2']
        test_rsa_private_key = 'rsa_test'
        test_cert_thumbprint = 'cert_test'
        test_tenent_id = '123abc'
        test_client_id = '456dfg'

        expected_result = 'result'

        mock_auth.return_value = test_auth
        mock_get_doc_libs.return_value = test_doc_libs
        mock_save.return_value = expected_result

        result = action.run(test_domain, test_output_file, test_output_file_append,
                            test_output_type, test_pass, test_site_url, test_user, False,
                            test_rsa_private_key, test_cert_thumbprint, test_tenent_id,
                            test_client_id)

        self.assertEqual(result, expected_result)
        mock_auth.assert_called_with(test_domain, test_user, test_pass)
        mock_get_doc_libs.assert_called_with(test_site_url, test_auth)
        mock_save.assert_called_with(test_doc_libs, test_output_file, test_output_file_append)
