#!/usr/bin/python
from requests_ntlm import HttpNtlmAuth
import urlparse
from lib.base_action import SharepointBaseAction


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
    def get_sites_list(self, base_url, ntlm_auth):
        endpoint_uri = '/_api/search/query?querytext=\'contentclass:STS_Site\''

        result = self.rest_request(urlparse.urljoin(base_url, endpoint_uri), ntlm_auth)
        parents = (result.json()['d']['query']['PrimaryQueryResult']['RelevantResults']
                   ['Table']['Rows']['results'])

        # Parse the response to get a list of the base site URLs
        site_urls = []
        for site in parents:
            # Save the name of the site from the SiteName key
            for cell in site['Cells']['results']:
                if cell['Key'] == 'SiteName':
                    site_urls.append(cell['Value'])

        return site_urls

    def run(self, base_url, domain, password, username):
        """
        Return a list of subsites on the given base site

        Args:
        - base_url: URL of the base Sharepoint site
        - domain: Domain for the given username
        - password: Password to login to sharepoint
        - username: Username to login to sharepoint

        Returns:
        - List: List of Sharepoint sites and subsites
        """
        login_user = domain + "\\" + username
        user_auth = HttpNtlmAuth(login_user, password)
        sites_list = self.get_sites_list(base_url, user_auth)
        site_objs = self.get_site_objects(base_url, user_auth, sites_list)

        return site_objs
