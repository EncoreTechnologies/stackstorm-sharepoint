#!/usr/bin/python
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
from urllib.parse import urljoin
from lib.base_action import SharepointBaseAction


class SubsitesList(SharepointBaseAction):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(SubsitesList, self).__init__(config)

    # Return the ID of the Parent site
    def get_parent_site(self, base_url, ntlm_auth, subsite=''):
        endpoint_uri = '/_api/web/parentweb'
        parent = self.rest_request(urljoin(base_url, subsite + endpoint_uri), ntlm_auth)
        return parent.json()['d']['Id']

    def get_sites_list(self, base_url, ntlm_auth, endpoint=''):
        # Appending the following to the endpoint to get a list of subsites
        endpoint_uri = '/_api/web/getsubwebsfilteredforcurrentuser' \
                       '(nwebtemplatefilter=-1,nconfigurationfilter=0)'
        site_list = []

        result = self.rest_request(urljoin(base_url, endpoint + endpoint_uri), ntlm_auth)
        for element in result.json()['d']['results']:
            subsite = element['ServerRelativeUrl']
            element['ParentId'] = self.get_parent_site(base_url, ntlm_auth, subsite)
            site_url = urljoin(base_url, subsite)
            # Add a list of each sites Document Libraries
            element['DocLibs'] = self.get_doc_libs(site_url, ntlm_auth)
            element['SiteUrl'] = site_url

            site_list.append(element)
            # Check for any subsites and add them to the list
            site_list += self.get_sites_list(base_url, ntlm_auth, subsite)

        return site_list

    def run(self, base_url, domain, endpoint, output_file, output_file_append,
            output_type, password, username, token_auth, rsa_private_key,
            cert_thumbprint, tenent_id, client_id):
        """
        Return a list of subsites on the given base site

        Args:
        - base_url: URL of the base Sharepoint site
        - domain: Domain for the given username
        - endpoint: Endpoint to get the list of subsites for
        - output_file: (Optional) file to save sites output to
        - output_file_append: Boolean, whether to append the sites list to the
            given file or overwrite it
        - output_type: "console" or "file" specifies whether to send output to
            console or save it in a specified file
        - password: Password to login to sharepoint
        - username: Username to login to sharepoint

        Returns:
        - List: List of Sharepoint sites and subsites if output_type is "console"
        - String: Path to the output file if output_type is "file"
        """
        self.token_auth = token_auth

        if self.token_auth:
            user_auth = self.create_token_auth_cred(rsa_private_key,
                                                    cert_thumbprint,
                                                    tenent_id,
                                                    client_id,
                                                    base_url)
        else:
            user_auth = self.create_ntlm_auth_cred(domain, username, password)

        site_objs = self.get_sites_list(base_url, user_auth, endpoint)

        # If the output type is file then return a string with the path to the file
        if output_type == 'file':
            return self.save_sites_list_to_file(site_objs, output_file,
                                                output_file_append)

        return site_objs
