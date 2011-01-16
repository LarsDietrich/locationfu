import adapters.basic_adapter
from lib import oauth
from django.utils import simplejson
import urllib

adapter_details = {
    'SERVICE_NAME': 'foursquare',
    'CONSUMER_KEY': "",
    'CONSUMER_SECRET': "",
    'REQUEST_TOKEN_URL': "http://foursquare.com/oauth/request_token",
    'ACCESS_TOKEN_URL': "http://foursquare.com/oauth/access_token",
    'AUTHORIZATION_URL': "http://foursquare.com/oauth/authorize",
}

class FoursquareAdapter(adapters.basic_adapter.BasicAdapter):
    def post(self, place, message, lat, long):
        params = urllib.urlencode({
            'q': place,
            'geolat': lat,
            'geolong': long
        })
        
        url = "http://api.foursquare.com/v1/venues.json?%s" % params
        response = simplejson.loads(self.communicate(url, None, "GET"))
        
        try:
            params = {
                'vid': response['groups'][0]['venues'][0]['id']
            }
        except:
            params = {
                'venue': place
            }
        
        post_url = "http://api.foursquare.com/v1/checkin.json"
        params['shout'] = message
        params['geolat'] = lat
        params['geolong'] = long
        response = simplejson.loads(self.communicate(post_url, params))
        
        return True, response['checkin']['message']

foursquare_adapter = FoursquareAdapter(adapter_details)