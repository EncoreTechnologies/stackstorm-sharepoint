#!/usr/bin/python
from requests_ntlm import HttpNtlmAuth
from lib.base_action import SharepointBaseAction


class DocLibList(SharepointBaseAction):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(DocLibList, self).__init__(config)

    def run(self, domain, password, site_url, username):
        """
        Return a list of document libraries on the given site or subsite

        Args:
        - domain: Domain for the given username
        - password: Password to login to sharepoint
        - site_url: URL of the base Sharepoint site
        - username: Username to login to sharepoint

        Returns:
        - List: List of Sharepoint Document Libraries
        """
        login_user = domain + "\\" + username
        user_auth = HttpNtlmAuth(login_user, password)

        result = self.get_doc_libs(site_url, user_auth)

        return result
