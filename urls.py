# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# urls.py - Main django urls file for the PAWS project.

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from paws.api import resources
from tastypie.api import Api

api = Api(api_name='v1')
api.register(resources.SpeciesResource())

# Discover admin.
admin.autodiscover()

urlpatterns = patterns('',
  # Set up admin pages.
  url(r'^admin/', include(admin.site.urls)),

  # Main pages.
  url(r'^$', 'paws.main.views.home'),

  # API calls.
  url(r'^api/', include(api.urls)),

  # Debugging templates
  url(r'^templates/(?P<templ>[^/]+)$', 'paws.main.views.template_debug'),
)
