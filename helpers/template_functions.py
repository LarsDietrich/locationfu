from google.appengine.ext import webapp
import os, random
register = webapp.template.create_template_register()

cur_version = os.environ["CURRENT_VERSION_ID"].replace(".", "")

def minify(path):
    if not os.environ["SERVER_SOFTWARE"].startswith("Development"):
        path = path.split(".")
        path.insert(len(path)-1, "min")
        path = ".".join(path)
        path = path + "?" + cur_version
    else:
        path = path + "?" + str(random.randint(1000, 9999))
    return path

register.filter(minify)
