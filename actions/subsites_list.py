#!/usr/bin/python
from requests_ntlm import HttpNtlmAuth
import urlparse
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
        parent = self.rest_request(urlparse.urljoin(base_url, subsite + endpoint_uri), ntlm_auth)
        return parent.json()['d']['Id']

    def get_sites_list(self, base_url, ntlm_auth, endpoint=''):
        # Appending the following to the endpoint to get a list of subsites
        endpoint_uri = '/_api/web/getsubwebsfilteredforcurrentuser' \
                       '(nwebtemplatefilter=-1,nconfigurationfilter=0)'
        site_list = []

        result = self.rest_request(urlparse.urljoin(base_url, endpoint + endpoint_uri), ntlm_auth)
        for element in result.json()['d']['results']:
            subsite = element['ServerRelativeUrl']
            element['ParentId'] = self.get_parent_site(base_url, ntlm_auth, subsite)
            site_url = urlparse.urljoin(base_url, subsite).encode('utf-8')
            # Add a list of each sites Document Libraries
            element['DocLibs'] = self.get_doc_libs(site_url, ntlm_auth)
            element['SiteUrl'] = site_url

            site_list.append(element)
            # Check for any subsites and add them to the list
            site_list += self.get_sites_list(base_url, ntlm_auth, subsite)

        return site_list

    def run(self, base_url, endpoint, domain, password, username):
        """
        Return a list of subsites on the given base site

        Args:
        - base_url: URL of the base Sharepoint site
        - domain: Domain for the given username
        - endpoint: Endpoint to get the list of subsites for
        - password: Password to login to sharepoint
        - username: Username to login to sharepoint

        Returns:
        - List: List of Sharepoint subsites
        """
        login_user = domain + "\\" + username
        user_auth = HttpNtlmAuth(login_user, password)

        result = self.get_sites_list(base_url, user_auth, endpoint)

        return result
