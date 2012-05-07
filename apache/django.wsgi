import os
import sys

# Fix path
path = '/paws/'
if path not in sys.path:
  sys.path.insert(1,path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'paws.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
