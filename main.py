#!/usr/bin/env python

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users

from django.utils import simplejson
import traceback
from helpers import config
import adapters
import logging

webapp.template.register_template_library('helpers.template_functions')

response_vars = {}

class HomeHandler(webapp.RequestHandler):
    def get(self):
        response_vars = init_response_vars()
        if response_vars['logged_in']:
            self.redirect('/checkin')
            return
        
        import models.news
        posts = models.news.News.all().order('-created')
        posts = posts.fetch(5)
        response_vars['news'] = []
        for post in posts:
            response_vars['news'].append(post)
        
        self.response.out.write(template.render(get_template_path(self.request.headers.get('user_agent'))+'home.html', response_vars))

class CheckinHandler(webapp.RequestHandler):
    '''
    Page to allow the user to define a place to checkin
    '''
    def get(self):
        response_vars = init_response_vars()
        import models.connection
        user = users.get_current_user()
        stored_services = models.connection.Connection.all().filter('uid =', user.user_id()).order('service')
        services = []
        for service in stored_services:
            services.append({
                'friendly_name': adapters.get_friendly_name(service.service),
                'service': service.service
            })
        
        response_vars['services'] = services
        
        self.response.out.write(template.render(get_template_path(self.request.headers.get('user_agent'))+'checkin.html', response_vars))

class ServiceAddHandler(webapp.RequestHandler):
    '''
    Get a request token and redirect to the authorize page for a given service
    '''
    def get(self):
        service = self.request.get('service')
        if adapters.verify(service):
            try:
                adapter = adapters.get_adapter(service)
                token = adapter.get_request_token()
            except:
                response_vars = init_response_vars()
                self.error(500)
                logging.error(traceback.print_exc())
                self.response.out.write(template.render(get_template_path(self.request.headers.get('user_agent'))+'error_oauth.html', response_vars))
                return
            
            import models.request_token
            rqt = models.request_token.RequestToken(
                uid = users.get_current_user().user_id(),
                token=token.key,
                secret=token.secret,
                service=service
            )
            rqt.put()
            
            try:
                auth_url = adapter.get_authorize_url(token)
            except:
                response_vars = init_response_vars()
                self.error(500)
                logging.error(traceback.print_exc())
                self.response.out.write(template.render(get_template_path(self.request.headers.get('user_agent'))+'error_oauth.html', response_vars))
                return
            
            self.redirect(auth_url)
        else:
            self.error(500)

class ServiceRemoveHandler(webapp.RequestHandler):
    '''
    Remove the passed service from a user's account, if present
    '''
    def get(self):
        service = self.request.get('service')
        if adapters.verify(service):
            import models.connection
            current_conn = models.connection.Connection.gql(
                "WHERE uid = :1 AND service = :2",
                users.get_current_user().user_id(),
                service
            );
            result = current_conn.fetch(1)
            if result:
                result[0].delete()
        return

class OAuthCallbackHandler(webapp.RequestHandler):
    '''
    Handle the callback from an OAuth registration. Requests an access token
    from the stored request token and store it
    '''
    def get(self):
        service = self.request.get('service')
        if not service:
            service = 'brightkite'
        
        if adapters.verify(service):
            adapter = adapters.get_adapter(service)
            request_token = self.request.get('oauth_token')
            verifier = self.request.get('oauth_verifier', None)
            if verifier:
                parameters = {
                    'oauth_verifier': verifier
                }
            else:
                parameters = None
            
            import models.request_token
            query = models.request_token.RequestToken.gql(
                "WHERE service = :1 AND uid = :2",
                service, users.get_current_user().user_id()
            )
            
            # Try all tokens in the datastore to null previous failed attempts
            valid_key = False
            for stored_token_details in query:
                try:
                    key, secret = adapter.get_access_key(request_token, stored_token_details.secret, parameters)
                    valid_key = True
                    break
                except:
                    continue
            
            if not valid_key:
                response_vars = init_response_vars()
                self.error(500)
                logging.error(traceback.print_exc())
                self.response.out.write(template.render(get_template_path(self.request.headers.get('user_agent'))+'error_oauth.html', response_vars))
                return
            
            # Clean up all outstanding tokens
            query = models.request_token.RequestToken.all().filter("uid =", users.get_current_user().user_id())
            for rqtoken in query:
                rqtoken.delete()
                    
            adapter.store_token(key, secret)
            
            self.redirect("/checkin")
        else:
            self.error(500)

class PostHandler(webapp.RequestHandler):
    '''
    Take in the details of a checkin and loop over each registered service
    for the current user, calling the associated adapter's post method
    '''
    def get(self, service=False):
        place = self.request.get('place', False)
        message = self.request.get('message', False)
        lat = self.request.get('lat', False)
        long = self.request.get('lng', False)
        
        response = {}
        
        if not place or not lat or not long:
            response['status'] = 1
        else:
            import models.connection
            connections = models.connection.Connection.all().filter("uid =", users.get_current_user().user_id())
            
            if service and adapters.verify(service): # Are we requesting to check into a single service?
                connections.filter("service =", service)
            
            return_messages = []
            for connection in connections:
                adapter = adapters.get_adapter(connection.service)
                status, message = adapter.post(place, message, lat, long)
                return_messages.append({
                    'status': status,
                    'service': adapters.get_friendly_name(connection.service),
                    'message': message
                })
            response['status'] = 0
            response['services'] = return_messages
        
        self.response.out.write(simplejson.dumps(response))

def get_template_path(uastring):
    if "iPhone" in uastring or ("Safari" in uastring and "Android" in uastring):
        return "templates/mobile/"
    else:
        return "templates/web/"

def init_response_vars():
    ''' Set up the default variables for all templates '''
    
    response_vars = {}
    
    try:
        current_user = users.User()
        response_vars['name'] = current_user.nickname()
        response_vars['email'] = current_user.email()
        response_vars['logged_in'] = True
        response_vars['logout_url'] = users.create_logout_url('/')
        
        import models.active_users
        current = models.active_users.ActiveUser.all().filter("uid =", current_user.user_id()).fetch(1)
        if not len(current):
            new_user = models.active_users.ActiveUser(
                uid=current_user.user_id(),
                email=current_user.email()
            )
            new_user.put()
        
    except users.UserNotFoundError:
        response_vars['logged_in'] = False
        response_vars['login_url'] = users.create_login_url('/checkin')
    
    adapter_keys = adapters.all.keys()
    adapter_keys.sort()
    view_adapters = [adapters.all[key] for key in adapter_keys]
    response_vars['adapters'] = view_adapters
    
    return response_vars

class NewsHandler(webapp.RequestHandler):
    def get(self):
        if self.request.get('message'):
            import models.news
            newpost = models.news.News(message=self.request.get('message'))
            newpost.put()
        
        self.response.out.write(template.render('templates/web/admin_news.html', None))
        return

def main():
    application = webapp.WSGIApplication([
        ('/', HomeHandler),
        ('/checkin', CheckinHandler),
        ('/service/add', ServiceAddHandler),
        ('/service/remove', ServiceRemoveHandler),
        ('/post', PostHandler),
        (r'/post/(\w+)', PostHandler),
        ('/oauth/callback', OAuthCallbackHandler),
        ('/admin/news', NewsHandler)
    ], debug=False)
    
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
