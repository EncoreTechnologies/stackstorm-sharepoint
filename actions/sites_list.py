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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SitesList(SharepointBaseAction):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(SitesList, self).__init__(config)

    # Return a list of SharePoint top level site objects from the
    # given list of URLs
    def get_site_objects(self, base_url, ntlm_auth, site_urls):
        # Make another API call with the site url to get the site object
        site_objs = []
        for site in site_urls:
            base = self.rest_request(site + '/_api/site/rootweb',
                                     ntlm_auth).json()['d']

            # Add some additional properties that may be useful
            base['DocLibs'] = self.get_doc_libs(site, ntlm_auth)
            base['SiteUrl'] = site
            base['Endpoint'] = '' if site == base_url else site.split(base_url)[1]
            base['ParentId'] = None

            site_objs.append(base)

        return site_objs

    # Return a list of SharePoint top level site URLs
    def get_sites_list(self, base_url, ntlm_auth, sites_filter):
        endpoint_uri = '/_api/search/query?querytext=\'contentclass:STS_Site\''

        result = self.rest_request(urljoin(base_url, endpoint_uri), ntlm_auth)
        row_count = result.json()['d']['query']['PrimaryQueryResult']['RelevantResults']['TotalRows']
        start_row = 0
        site_urls = []
        while(start_row < row_count):
            endpoint_page = endpoint_uri + '&rowlimit=500&startrow=' + str(start_row)

            result = self.rest_request(urljoin(base_url, endpoint_page), ntlm_auth)
            parents = (result.json()['d']['query']['PrimaryQueryResult']['RelevantResults']
                       ['Table']['Rows']['results'])

            # Parse the response to get a list of the base site URLs
            for site in parents:
                # Save the name of the site from the SiteName key
                for cell in site['Cells']['results']:
                    if cell['Key'] == 'SiteName':
                        if cell['Value'].lower() in sites_filter:
                            site_urls.append(cell['Value'])

            start_row += 500

        return site_urls

    def run(self, base_url, domain, output_file, output_file_append,
            output_type, password, username, token_auth, rsa_private_key,
            cert_thumbprint, tenent_id, client_id, sites_filter):
        """
        Return a list of subsites on the given base site

        Args:
        - base_url: URL of the base Sharepoint site
        - domain: Domain for the given username
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

        # Convert to a set to remove dulicates
        my_set = set(sites_filter)
        sites_filter = list(my_set)
        sites_filter = [site.lower() for site in sites_filter]

        sites_list = self.get_sites_list(base_url, user_auth, sites_filter)
        site_objs = self.get_site_objects(base_url, user_auth, sites_list)

        # If the output type is file then return a string with the path to the file
        if output_type == 'file':
            self.save_sites_list_to_file(site_objs, output_file,
                                         output_file_append)

        return site_objs
