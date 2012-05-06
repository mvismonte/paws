# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# API Resources
# This file contains the resources for the RESTful API using the
# django rest framework.

from tastypie.resources import ModelResource
from paws.main import models

class SpeciesResource(ModelResource):
  class Meta:
    queryset = models.Species.objects.all()
    resource_name = 'species'
