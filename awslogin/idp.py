import requests
import os
from bs4 import BeautifulSoup
from getpass import getpass


class LoginError(Exception):
    pass


class IdentityProvider(object):
    def __init__(self, cfg):
        self.idp_entry_url = cfg.get('idp', 'entry_url')
        self.ssl_verify = cfg.getboolean('idp', 'ssl_verify')
	self.username = cfg.get('idp', 'username')
        self.password = cfg.get('idp', 'password')
        self.saml_assertion = None
        self.session = requests.Session()

    def get_saml_assertion(self):
        if not (self.username and self.password):
            self._set_userpass()
	response = self.session.get(self.idp_entry_url, verify=self.ssl_verify)
        self._login_workflow(response)
	self._unset_userpass()
	return self.saml_assertion

    def _set_userpass(self):
        if self.username:
            print "Username: %s" % self.username
        else:
            print "Username:",
            self.username = raw_input()
        self.password = getpass()
        print ''

    def _unset_userpass(self):
        self.username = '##############################################'
        self.password = '##############################################'
        del self.username
        del self.password

    def _detect_login_error(self, soup):
        try:
            error = soup.find_all('font', color='#FF0000')[0]  # Hmm
            raise LoginError(error.text)
        except IndexError:
            pass

    def _login_workflow(self, response):
        soup = BeautifulSoup(response.text.decode('utf8'), 'html.parser')

        # Login error short-circuits the workflow
        self._detect_login_error(soup)

	params = {}
	for input_tag in soup.find_all('input'):
	    name = input_tag.get('name','')
	    value = input_tag.get('value','')
            if 'samlresponse' == name.lower():
                self.saml_assertion = value
                return
            elif 'user' == name.lower():
		params[name] = self.username
	    elif 'pass' == name.lower():
		params[name] = self.password
	    else:
		params[name] = value

        try:
    	    url = soup.find_all('form')[0].get('action')
        except IndexError as err:
            # Not a form, and not a SAML assertion 
            raise LoginError('Response did not contain a valid SAML assertion')

	response = self.session.post(url, data=params, verify=self.ssl_verify)
        self._login_workflow(response)
