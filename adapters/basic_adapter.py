from helpers import config
from lib import oauth
from lib.oauth_client import SimpleOAuthClient
from google.appengine.api import users
import time

class BasicAdapter():
    def __init__(self, details):
        self.CONSUMER_KEY = details['CONSUMER_KEY']
        self.CONSUMER_SECRET = details['CONSUMER_SECRET']
        self.REQUEST_TOKEN_URL = details['REQUEST_TOKEN_URL']
        self.ACCESS_TOKEN_URL = details['ACCESS_TOKEN_URL']
        self.AUTHORIZATION_URL = details['AUTHORIZATION_URL']
        self.SERVICE_NAME = details['SERVICE_NAME']
        
        self.SIGNATURE_METHOD = oauth.OAuthSignatureMethod_HMAC_SHA1()
    
    def init_client(self):
        client = SimpleOAuthClient(config.server, config.port, self.REQUEST_TOKEN_URL, self.ACCESS_TOKEN_URL, self.AUTHORIZATION_URL)
        consumer = oauth.OAuthConsumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        return client, consumer
    
    # Stub, should be defined by the subclass for post to the service
    def post(self, place, message, lat, long):
        return
    
    def communicate(self, url, data, method="POST"):
        client, consumer = self.init_client()
        token = self.get_token()
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_method=method, http_url=url, parameters=data)
        oauth_request.sign_request(self.SIGNATURE_METHOD, consumer, token)
        return client.access_resource(oauth_request)
    
    def get_request_token(self):
        client, consumer = self.init_client()
        if not self.SERVICE_NAME == "brightkite":
            url_extra = "?service=" + self.SERVICE_NAME
        else:
            url_extra = ""
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, callback=config.oauth_callback_url + url_extra, http_url=client.request_token_url)
        oauth_request.sign_request(self.SIGNATURE_METHOD, consumer, None)
        token = client.fetch_request_token(oauth_request)
        return token
    
    def get_authorize_url(self, token):
        return self.AUTHORIZATION_URL+"?"+str(token)
    
    def authorize_token(self, token, secret):
        client, consumer = self.init_client()
        token = oauth.OAuthToken(token, secret)
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token=token, http_url=client.authorization_url)
        oauth_request.sign_request(self.SIGNATURE_METHOD, consumer, token)
        response = client.authorize_token(oauth_request)
        return True
    
    def get_access_key(self, token, secret, parameters):
        client, consumer = self.init_client()
        token = oauth.OAuthToken(token, secret)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, token=token, http_url=client.access_token_url, parameters=parameters)
        oauth_request.sign_request(self.SIGNATURE_METHOD, consumer, token)
        token = client.fetch_access_token(oauth_request)
        return token.key, token.secret
    
    def store_token(self, token, secret):
        import models.connection
        query = models.connection.Connection.gql(
            "WHERE uid = :1 AND service = :2",
            users.get_current_user().user_id(),
            self.SERVICE_NAME
        )
        res = query.fetch(1)
        if len(res):
            res[0].token = token
            res[0].secret = secret
            res[0].put()
        else:
            conn = models.connection.Connection(
                uid = users.get_current_user().user_id(),
                token = token,
                secret = secret,
                service = self.SERVICE_NAME
            )
            conn.put()
    
    def get_token(self):
        import models.connection
        query = models.connection.Connection.gql(
            "WHERE uid = :1 AND service = :2",
            users.get_current_user().user_id(),
            self.SERVICE_NAME
        )
        res = query.fetch(1)
        return oauth.OAuthToken(res[0].token, res[0].secret)
        
            