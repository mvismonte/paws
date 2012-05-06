# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# urls.py - Main django urls file for the PAWS project.

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from paws.api import resources
from tastypie.api import Api

api = Api(api_name='v1')
api.register(resources.UserResource())
api.register(resources.StaffResource())
api.register(resources.SpeciesResource())
api.register(resources.CategoryResource())
api.register(resources.SubcategoryResource())
api.register(resources.AnimalResource())
api.register(resources.EnrichmentResource())
api.register(resources.EnrichmentNoteResource())
api.register(resources.AnimalObservationResource())
api.register(resources.ObservationResource())


# Discover admin.
admin.autodiscover()

urlpatterns = patterns('',
  # Set up admin pages.
  url(r'^admin/', include(admin.site.urls)),

  # Main pages.

  # API calls.
  (r'^api/', include(api.urls)),
)
