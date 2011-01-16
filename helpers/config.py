import os

server = os.environ['SERVER_NAME']
port = int(os.environ['SERVER_PORT'])

if port != 80:
    str_port = ":"+str(os.environ['SERVER_PORT'])
else:
    str_port = ""

host = "http://%s%s" % (server, str_port)
oauth_callback_url = host+"/oauth/callback"