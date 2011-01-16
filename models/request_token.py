from google.appengine.ext import db

class RequestToken(db.Model):
    uid = db.StringProperty(required=True)
    token = db.StringProperty(required=True)
    secret = db.StringProperty(required=True)
    service = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)