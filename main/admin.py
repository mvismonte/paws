# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# Main Admin
# This file registers all of the models in models.py with Django admin.

from django.contrib import admin
from main import models

admin.site.register(models.Staff)
admin.site.register(models.Species)
admin.site.register(models.Animal)
admin.site.register(models.Category)
admin.site.register(models.Subcategory)
admin.site.register(models.Enrichment)
admin.site.register(models.EnrichmentNote)
admin.site.register(models.AnimalObservation)
admin.site.register(models.Observation)