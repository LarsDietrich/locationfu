import adapters.basic_adapter
from lib import oauth
from django.utils import simplejson
import urllib

adapter_details = {
    'SERVICE_NAME': 'brightkite',
    'CONSUMER_KEY': "",
    'CONSUMER_SECRET': "",
    'REQUEST_TOKEN_URL': "http://brightkite.com/oauth/request_token",
    'ACCESS_TOKEN_URL': "http://brightkite.com/oauth/access_token",
    'AUTHORIZATION_URL': "http://brightkite.com/oauth/authorize",
}

class BrightkiteAdapter(adapters.basic_adapter.BasicAdapter):
    def post(self, place, message, lat, long):
        search_string = urllib.urlencode({'q': "%s near %s, %s" %(place, lat, long) })
        url = "http://brightkite.com/places/search.json?%s" % search_string
        places = simplejson.loads(self.communicate(url, None, "GET"))
        
        if len(places):
            try:
                object_id = places[0]['id']
            except KeyError:
                object_id = places['id']
            
            post_url = "http://brightkite.com/places/%s/checkins.json" % object_id
            response = simplejson.loads(self.communicate(post_url, None))
            
            if len(message):
                params = {
                    "note[body]": message
                }
                post_url = "http://brightkite.com/places/%s/notes.json" % object_id
                res = self.communicate(post_url, params)
            
            return True, "Checked in at " + response['place']['name']
        
        return False, "Could not fine that location"

brightkite_adapter = BrightkiteAdapter(adapter_details)