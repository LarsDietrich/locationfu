About
=====

This is the code that powers multi-service location checkins at http://locationfu.com.

With LocationFu, you can post to any OAuth-enabled location based service using any HTML5
geolocation supporting desktop or mobile web browser. The system will attempt to
disambiguate your location from Google Maps and post to any enabled service.

Requirements
============

LocationFu runs on Google App Engine, and everything else is either built-in or
loaded on demand (jQuery, for example).

Running
=======

 1. Set up a Google App Engine app
 2. Configure the application in the app.yaml file
 3. Add your developer credentials to each adapter you want to use
 4. Push the app to App Engine

Adding Services
===============

LocationFu uses a simple adapter system for posting to location based services that
use OAuth for user authentication. To add a new service, you need only create a new
adapter that inherits off the base adapter, give it the specifics of the service,
and implement a `post` method.

Example adapters for Foursquare, FireEagle, Twitter, and BrightKite are included.

Notes
=====

Yeah, there are no comments in the code. This was just to bang around with OAuth and
because I got sick of checking in to lots of different services (this was pre Brightkite's
Check.in).
