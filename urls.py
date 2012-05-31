# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# urls.py - Main django urls file for the PAWS project.

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from paws.api import resources
from tastypie.api import Api

# Create the API and register Resources.
api = Api(api_name='v1')
api.register(resources.AnimalObservationResource())
api.register(resources.AnimalResource())
api.register(resources.CategoryResource())
api.register(resources.EnrichmentNoteResource())
api.register(resources.EnrichmentResource())
api.register(resources.ObservationResource())
api.register(resources.SpeciesResource())
api.register(resources.StaffResource())
api.register(resources.SubcategoryResource())
api.register(resources.UserResource())
api.register(resources.ExhibitResource())
api.register(resources.HousingGroupResource())

# Discover admin.
admin.autodiscover()

urlpatterns = patterns('',
  # Set up admin pages.
  url(r'^admin/', include(admin.site.urls)),

  # API calls.
  url(r'^api/', include(api.urls)),

  # Authentication views.
  url(r'^auth/login/$', 'django.contrib.auth.views.login',
      { 'template_name': 'login.html', 'redirect_field_name':'next'}),
  url(r'^auth/logout/', 'paws.main.views.logout'),

  # Main pages.
  url(r'^$', 'paws.main.views.home'),
  url(r'^animals$', 'paws.main.views.animals'),
  url(r'^enrichments$', 'paws.main.views.enrichments'),
  url(r'^observe$', 'paws.main.views.observe'),
  url(r'^staff$', 'paws.main.views.staff'),


  # Debugging templates.
  url(r'^templates/(?P<templ>[^/]+)$', 'paws.main.views.template_debug'),

  # Haystack
  url(r'^search/', include('haystack.urls')),
)
