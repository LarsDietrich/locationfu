import adapters.basic_adapter
from lib import oauth
from django.utils import simplejson
import urllib

adapter_details = {
    'SERVICE_NAME': 'twitter',
    'CONSUMER_KEY': "",
    'CONSUMER_SECRET': "",
    'REQUEST_TOKEN_URL': "http://twitter.com/oauth/request_token",
    'ACCESS_TOKEN_URL': "http://twitter.com/oauth/access_token",
    'AUTHORIZATION_URL': "http://twitter.com/oauth/authorize",
}

class TwitterAdapter(adapters.basic_adapter.BasicAdapter):
    def post(self, place, message, lat, long):
        post_url = "http://twitter.com/account/update_profile.json"
        
        location_string = place + " (" + lat + ", " + long + ")"
        if len(location_string) > 30:
            location_string = location_string[:27] + "..."
        
        params = {
            'location': location_string,
        }
        
        response = simplejson.loads(self.communicate(post_url, params))
        
        try:
            id = response['id'] # does the return contain any data?
            return True, "Your location has been updated"
        except:
            return False, "Oops! An error has occured. Please try again later"

twitter_adapter = TwitterAdapter(adapter_details)