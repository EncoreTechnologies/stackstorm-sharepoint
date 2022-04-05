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
from lib.base_action import SharepointBaseAction


class DocLibList(SharepointBaseAction):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(DocLibList, self).__init__(config)

    def run(self, domain, output_file, output_file_append, output_type,
            password, site_url, username):
        """
        Return a list of document libraries on the given site or subsite

        Args:
        - domain: Domain for the given username
        - output_file: (Optional) file to save sites output to
        - output_file_append: Boolean, whether to append the sites list to the
            given file or overwrite it
        - output_type: "console" or "file" specifies whether to send output to
            console or save it in a specified file
        - password: Password to login to sharepoint
        - site_url: URL of the base Sharepoint site
        - username: Username to login to sharepoint

        Returns:
        - List: List of Sharepoint sites and subsites
        """
        user_auth = self.create_auth_cred(domain, username, password)

        doc_libs = self.get_doc_libs(site_url, user_auth)

        if output_type == 'file':
            return self.save_sites_list_to_file(doc_libs, output_file,
                                                output_file_append)

        return doc_libs
