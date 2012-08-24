import os
import sys

# Fix path
path = 'c:/wamp/www/'
if path not in sys.path:
  sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'paws.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
