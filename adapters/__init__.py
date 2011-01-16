# To add a new adapter, add it's module here and add it to the all list below
import foursquare, brightkite, fireeagle, twitter

all = {
    'brightkite': {
        'service': 'brightkite',
        'friendly_name': 'BrightKite'
    },
    'foursquare': {
        'service': 'foursquare',
        'friendly_name': 'Foursquare'
    },
    'fireeagle': {
        'service': 'fireeagle',
        'friendly_name': 'Fire Eagle'
    },
    'twitter': {
        'service': 'twitter',
        'friendly_name': 'Twitter'
    }
}

__all__ = ['BasicAdapter']
for x in all.keys(): __all__.append(x)

def verify(name):
    if name not in __all__:
        return False
    return True

def get_friendly_name(service):
    return all[service]['friendly_name']

def get_adapter(service):
    return getattr(globals()[service], service+"_adapter")