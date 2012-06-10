# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# Main Admin
# This file registers all of the models in models.py with Django admin.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from paws.main import models

class AnimalObservationInline(admin.TabularInline):
  model = models.AnimalObservation

class ObservationAdmin(admin.ModelAdmin):
  inlines = [
    AnimalObservationInline
  ]

class AnimalAdmin(admin.ModelAdmin):
  inlines = [
    AnimalObservationInline
  ]
  list_filter = (
    'species',
  )

class EnrichmentAdmin(admin.ModelAdmin):
  list_filter = (
    'subcategory',
  )

admin.site.register(models.Animal, AnimalAdmin)
admin.site.register(models.AnimalObservation)
admin.site.register(models.Behavior)
admin.site.register(models.Category)
admin.site.register(models.Enrichment, EnrichmentAdmin)
admin.site.register(models.EnrichmentNote)
admin.site.register(models.Observation, ObservationAdmin)
admin.site.register(models.Species)
admin.site.register(models.Subcategory)
admin.site.register(models.Staff)
admin.site.register(models.Exhibit)
admin.site.register(models.HousingGroup)
