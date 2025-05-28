from __future__ import print_function
import cherrypy
import os
import threading
import webbrowser
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import requests

class OAuth2Server(object):
    def __init__(self, client_id, client_secret, redirect_uri="http://127.0.0.1:8080/"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.client = WebApplicationClient(client_id)

    def browser_authorize(self):
        authorization_url = self.client.prepare_request_uri(
            "https://www.fitbit.com/oauth2/authorize",
            redirect_uri=self.redirect_uri,
            scope=["activity", "heartrate", "sleep", "profile"],
        )
        webbrowser.open(authorization_url)
        cherrypy.config.update({"server.socket_port": 8080})
        cherrypy.quickstart(self)
    
    def get_tokens(self, authorization_code):
        """Exchange the authorization code for access and refresh tokens."""
        token_url = "https://api.fitbit.com/oauth2/token"
        data = {
            'client_id': self.client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': authorization_code,
        }
        auth = HTTPBasicAuth(self.client_id, self.client_secret)

        response = requests.post(token_url, data=data, auth=auth, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve tokens: {response.status_code}, {response.text}")

    @cherrypy.expose
    def index(self, code):
        cherrypy.engine.exit()
        return code
