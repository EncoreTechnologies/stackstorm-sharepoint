#!/usr/bin/python
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
        - base_url: URL of the base Sharepoint site
        - domain: Domain for the given username
        - password: Password to login to sharepoint
        - username: Username to login to sharepoint

        Returns:
        - List: List of Sharepoint sites and subsites
        """
        user_auth = self.create_auth_cred(domain, username, password)

        result = self.get_doc_libs(site_url, user_auth)

        return result
