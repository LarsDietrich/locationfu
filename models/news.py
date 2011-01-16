from google.appengine.ext import db

class News(db.Model):
    message = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)