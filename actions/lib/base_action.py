import requests
from requests_ntlm import HttpNtlmAuth
from st2common.runners.base_action import Action


class SharepointBaseAction(Action):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        Also stores the Terraform class from python_terraform in a class variable
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(SharepointBaseAction, self).__init__(config)

    def get_doc_libs(self, base_url, ntlm_auth):
        # Endpoint to return lists filtered for document libraries
        # The base template 101 is for document libraries
        # https://docs.microsoft.com/en-us/previous-versions/office/
        # sharepoint-server/ee541191(v=office.15)
        endpoint_uri = '/_api/web/lists?$filter=BaseTemplate eq ' \
                       '101&$select=Title,Id,DocumentTemplateUrl'
        result = self.rest_request(base_url + endpoint_uri, ntlm_auth)

        return result.json()['d']['results']

    def rest_request(self, endpoint, ntlm_auth, method='GET',
                     payload=None, ssl_verify=False):
        """Establish a connection with the sharepoint url and return the results
        :param endpoint: Sharepooint endpoint to connect to
        :param ntlm_auth: NTLM auth objectto make the request
        :returns: result from the rest request
        """
        headers = {
            'accept': 'application/json;odata=verbose',
            'content-type': 'application/json;odata=verbose',
            'odata': 'verbose',
            'X-RequestForceAuthentication': 'true'
        }

        result = requests.request(method, endpoint, auth=ntlm_auth, data=payload,
                                  headers=headers, verify=ssl_verify)

        return result

    def create_auth_cred(self, domain, username, password):
        """Create and return an NTLM auth object which will be used to make REST requests
        :param domain: Domain for the given username
        :param password: Password to login to sharepoint
        :param username: Username to login to sharepoint
        :returns: NTLM auth object to make REST requests
        """
        login_user = domain + "\\" + username
        return HttpNtlmAuth(login_user, password)

    # Need this method here because of the following error with unit tests
    # TypeError: Can't instantiate class with abstract methods run
    def run(self, **kwargs):
        raise RuntimeError("run() not implemented")
