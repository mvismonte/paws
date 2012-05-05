# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# urls.py - Main django urls file for the PAWS project.

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Discover admin.
admin.autodiscover()

urlpatterns = patterns('',
  # Set up admin pages.
  url(r'^admin/', include(admin.site.urls)),

  # Main pages.

  # API calls.
)
