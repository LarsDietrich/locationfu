import adapters.basic_adapter
from lib import oauth
from django.utils import simplejson
import urllib

adapter_details = {
    'SERVICE_NAME': 'fireeagle',
    'CONSUMER_KEY': "",
    'CONSUMER_SECRET': "",
    'REQUEST_TOKEN_URL': "https://fireeagle.yahooapis.com/oauth/request_token",
    'ACCESS_TOKEN_URL': "https://fireeagle.yahooapis.com/oauth/access_token",
    'AUTHORIZATION_URL': "https://fireeagle.yahoo.net/oauth/authorize",
}

class FireeagleAdapter(adapters.basic_adapter.BasicAdapter):
    def post(self, place, message, lat, long):
        post_url = "https://fireeagle.yahooapis.com/api/0.1/update.json"
        
        params = {
            'label': place,
            'lat': lat,
            'lon': long
        }
        
        response = simplejson.loads(self.communicate(post_url, params))
        
        try:
            message = response['rsp']['message']
        except:
            message = "OK!"
        
        return True, message

fireeagle_adapter = FireeagleAdapter(adapter_details)