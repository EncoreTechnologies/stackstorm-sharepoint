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
import requests
import json
from st2common.runners.base_action import Action
from msal.oauth2cli import JwtAssertionCreator
from requests_ntlm import HttpNtlmAuth


class SharepointBaseAction(Action):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        Also stores the Terraform class from python_terraform in a class variable
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(SharepointBaseAction, self).__init__(config)

    def get_doc_libs(self, base_url, auth_token):
        # Endpoint to return lists filtered for document libraries
        # The base template 101 is for document libraries
        # https://docs.microsoft.com/en-us/previous-versions/office/
        # sharepoint-server/ee541191(v=office.15)
        endpoint_uri = '/_api/web/lists?$filter=BaseTemplate eq ' \
                       '101&$select=Title,Id,DocumentTemplateUrl'
        result = self.rest_request(base_url + endpoint_uri, auth_token)

        return result.json()['d']['results']

    def rest_request(self, endpoint, auth_token, method='GET',
                     payload=None, ssl_verify=False):
        """Establish a connection with the sharepoint url and return the results
        :param endpoint: Sharepooint endpoint to connect to
        :returns: result from the rest request
        """
        headers = {
            'accept': 'application/json;odata=verbose',
            'content-type': 'application/json;odata=verbose',
            'odata': 'verbose',
            'X-RequestForceAuthentication': 'true'
        }

        if 'test':
            headers['Authorization'] = "Bearer {0}".format(auth_token)
            result = requests.request(method, endpoint, data=payload,
                                      headers=headers, verify=ssl_verify)
        else:
            result = requests.request(method, endpoint, auth=ntlm_auth, data=payload,
                                      headers=headers, verify=ssl_verify)

        return result

    def create_token_auth_cred(self, rsa_private_key, cert_thumbprint, tenent_id, client_id, site_url):
        """Create and return an NTLM auth object which will be used to make REST requests
        :param domain: Domain for the given username
        :param password: Password to login to sharepoint
        :param username: Username to login to sharepoint
        :returns: NTLM auth object to make REST requests
        """
        assertion = JwtAssertionCreator(
            rsa_private_key,
            algorithm="RS256",
            sha1_thumbprint=cert_thumbprint,
            headers={}
        )

        token_endpoint = "https://login.microsoftonline.com/{0}/oauth2/v2.0/token".format(tenent_id)

        client_assertion = assertion.create_normal_assertion(
            audience=token_endpoint,
            issuer=client_id
        )

        token_scope = "{0}/.default".format(site_url)

        token_payload = {
            'client_id': client_id,
            'scope': token_scope,
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': client_assertion
        }

        token_response = requests.request('POST', token_endpoint, data=token_payload)

        token_response.raise_for_status()

        return token_response.json()['access_token']

    def create_ntlm_auth_cred(self, domain, username, password):
        """Create and return an NTLM auth object which will be used to make REST requests
        :param domain: Domain for the given username
        :param password: Password to login to sharepoint
        :param username: Username to login to sharepoint
        :returns: NTLM auth object to make REST requests
        """
        login_user = domain + "\\" + username
        return HttpNtlmAuth(login_user, password)

    def save_sites_list_to_file(self, site_objs, file_path, file_append):
        """Write the given list of sharepoint sites to the specified file
        :param site_objs: List of Sharepoint site objects
        :param file_path: Path to the file that will store the list of sites
        :param file_append: Boolean, if true append sites to end of file otherwise overwrite it
        """
        if not file_path:
            raise 'output_file path must be specified to save output to file.'

        # If appending sites to the file then read in the file first before overwriting it
        if file_append:
            file = open(file_path, 'r')
            sites_list = json.loads(file.read())
            file.close()
            sites_list.extend(site_objs)
        else:
            sites_list = site_objs

        with open(file_path, 'w') as outfile:
            json.dump(sites_list, outfile)
            outfile.close()

        return 'Output saved to: ' + file_path

    # Need this method here because of the following error with unit tests
    # TypeError: Can't instantiate class with abstract methods run
    def run(self, **kwargs):
        raise RuntimeError("run() not implemented")
