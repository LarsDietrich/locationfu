from google.appengine.ext import db

class ActiveUser(db.Model):
    uid = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)