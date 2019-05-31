import cgi
import os
import socket
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from venv import logger

import requests


class LoginError(Exception):
    pass


class MyHandler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.addCORSHeaders()
        self.end_headers()
        self.wfile.write("fsd".encode())

    def do_POST(self):
        ctype, pdict = cgi.parse_header(
            self.headers['content-type'])

        # boundary data needs to be encoded in a binary format

        if ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                self.rfile.read(length).decode('utf8'),
                keep_blank_values=1)
            saml_response_ = postvars['SAMLResponse'][0]
            logger.debug("Saml Response : " + saml_response_)
            self.server.saml_response = saml_response_

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.addCORSHeaders()
        self.end_headers()

        output = "{'succes':'true'}"
        self.wfile.write(output.encode())

    def addCORSHeaders(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,Content-Length,bla")


class MyServer(HTTPServer):
    allow_reuse_address = False

    saml_response = ''


class IdentityProvider(object):
    def __init__(self, cfg):
        self.host_url = cfg.get('idp', 'host_url')
        self.local_port_param_name = cfg.get('idp', 'local_port_param_name')
        self.entry_url = cfg.get('idp', 'entry_url')
        self.session = requests.Session()

    def get_saml_assertion(self):
        saml_assertion = self._login_workflow()
        return saml_assertion

    def _login_workflow(self):

        port_number = 8080

        while True:
            try:
                saml_receiver_server = MyServer(("localhost", port_number), MyHandler)

                threading.Thread(target=saml_receiver_server.serve_forever).start()

                print("Trying to open server on port  %d" % port_number)
            except socket.error:
                print("Failed to open server on port  %d" % port_number)

                if port_number > 8080 + 100:
                    success = False
                    break
                port_number += 1
            else:
                success = True
                break

        if success:

            # open or show url
            authorize_url = "%s%d" % (self.entry_url, port_number)

            print("Open a browser at %s" % authorize_url)

            # Without this, Chrome on MacOS will not launch unless Chrome
            # is already open. This is due to an bug in webbbrowser.py that tries to
            # open web browsers by app name using i.e. 'Chrome' but the actual app
            # name is 'Google Chrome' on Mac.
            if isMacOS():
                try:
                    webbrowser.register('Google Chrome', None,
                                        webbrowser.MacOSXOSAScript('Google Chrome'), -1)
                except AttributeError:
                    pass  # proceed with default behavior
            webbrowser.open(authorize_url, new=1, autoraise=True)

            while True:
                if saml_receiver_server.saml_response:
                    print("Received SAML token")
                    logger.debug(saml_receiver_server.saml_response)
                    saml_response = saml_receiver_server.saml_response
                    saml_receiver_server.server_close()
                    break

            return saml_response
        else:
            raise Exception('failed to open port')


def isMacOS():
    if os.name == 'darwin':
        return True

    return False
