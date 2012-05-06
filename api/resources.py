# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# API Resources
# This file contains the resources for the RESTful API using the
# django-tastypie.

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from paws.main import models
from tastypie.resources import ModelResource,fields

# AnimalObservation Resource.
class AnimalObservationResource(ModelResource):
  # Define foreign keys.
  animal = fields.ForeignKey(
      'paws.api.resources.AnimalResource','animal', full=True)
  observation = fields.ForeignKey(
      'paws.api.resources.ObservationResource', 'observation')

  class Meta:
    queryset = models.AnimalObservation.objects.all()
    resource_name = 'animalObservation'

  # Redefine get_object_list to filter for observation_id and animal_id.
  def get_object_list(self, request):
    animal_id = request.GET.get('animal_id', None)
    observation_id = request.GET.get('observation_id', None)
    q_set = super(AnimalObservationResource, self).get_object_list(request)

    # Try filtering by animal if it exists.
    try:
      animal = models.Animal.objects.get(id=animal_id)
      q_set = q_set.filter(animal=animal)
    except ObjectDoesNotExist:
      pass

    # Try filtering by observation if it exists.
    try:
      observation = models.Observation.objects.get(id=observation_id)
      q_set = q_set.filter(observation=observation)
    except ObjectDoesNotExist:
        pass

    return q_set

# Animal Resource.
class AnimalResource(ModelResource):
  # Define foreign keys.
  species = fields.ForeignKey(
      'paws.api.resources.SpeciesResource', 'species', full=True)

  class Meta:
    queryset = models.Animal.objects.all()
    resource_name = 'animal'

  # Redefine get_object_list to filter for species_id.
  def get_object_list(self, request):
    species_id = request.GET.get('species_id', None)
    q_set = super(AnimalResource, self).get_object_list(request)
    try:
      species = models.Species.objects.get(id=species_id)
      q_set = q_set.filter(species=species)
    except ObjectDoesNotExist:
      pass
    return q_set

# Category Resource.
class CategoryResource(ModelResource):
  class Meta:
    queryset = models.Category.objects.all()
    resource_name = 'category'

# Enrichment Note Resource.
class EnrichmentNoteResource(ModelResource):
  # Define foreign keys.
  species = fields.ForeignKey(
      'paws.api.resources.SpeciesResource', 'species', full=True)
  enrichment = fields.ForeignKey(
      'paws.api.resources.EnrichmentResource','enrichment', full=True)

  class Meta:
    queryset = models.EnrichmentNote.objects.all()
    resource_name = 'enrichmentNote'

  # Redefine get_object_list to filter for enrichment_id and species_id.
  def get_object_list(self, request):
    species_id = request.GET.get('species_id', None)
    enrichment_id = request.GET.get('enrichment_id', None)
    q_set = super(EnrichmentNoteResource, self).get_object_list(request)

    # Try filtering by species first.
    try:
      species = models.Species.objects.get(id=species_id)
      q_set = q_set.filter(species=species)
    except ObjectDoesNotExist:
      pass

    # Try filtering by enrichment next.
    try:
      enrichment=models.Enrichment.objects.get(id=enrichment_id)
      q_set = q_set.filter(enrichment=enrichment)
      return q_set
    except ObjectDoesNotExist:
      pass

    return q_set

# Enrichment Resource.
class EnrichmentResource(ModelResource):
  # Define foreign keys.
  subcategory = fields.ForeignKey(
    'paws.api.resources.SubcategoryResource','subcategory', full=True)

  class Meta:
    queryset = models.Enrichment.objects.all()
    resource_name = 'enrichment'

  # Redefine get_object_list to filter for subcategory_id.
  def get_object_list(self, request):
    subcategory_id = request.GET.get('subcategory_id', None)
    q_set = super(EnrichmentResource, self).get_object_list(request)

    # Try filtering by subcategory if it exists.
    try:
      subcategory = models.Subcategory.objects.get(id=subcategory_id)
      q_set = q_set.filter(subcategory=subcategory)
    except ObjectDoesNotExist:
      pass
    return q_set

# Observation Resource.
class ObservationResource(ModelResource):
  # Define foreign keys.
  enrichment = fields.ForeignKey(
      'paws.api.resources.EnrichmentResource','enrichment')
  staff = fields.ForeignKey(
      'paws.api.resources.StaffResource','staff')

  class Meta:
    queryset = models.Observation.objects.all()
    resource_name = 'observation'

  # Redefine get_object_list to filter for enrichment_id and staff_id.
  def get_object_list(self, request):
    staff_id = request.GET.get('staff_id', None)
    enrichment_id = request.GET.get('enrichment_id', None)
    q_set = super(ObservationResource, self).get_object_list(request)

    # Try filtering by staff_id if it exists.
    try:
      staff = models.Staff.objects.get(id=staff_id)
      q_set = q_set.filter(staff=staff)
    except ObjectDoesNotExist:
      pass

    # Try filtering by enrichment if it exists.
    try:
      enrichment = models.Enrichment.objects.get(id=enrichment_id)
      q_set = q_set.filter(enrichment=enrichment)
    except ObjectDoesNotExist:
      pass

    return q_set

# Species Resource.
class SpeciesResource(ModelResource):
  class Meta:
    queryset = models.Species.objects.all()
    resource_name = 'species'

# Staff Resource.
class StaffResource(ModelResource):
  user = fields.ToOneField(
      'paws.api.resources.UserResource', 'user', full=True)
  class Meta:
    queryset = models.Staff.objects.all()
    resource_name = 'staff'

# Subcategory Resource.
class SubcategoryResource(ModelResource):
  # Define foreign keys.
  category = fields.ForeignKey(
      'paws.api.resources.CategoryResource', 'category', full=True)

  class Meta:
    queryset = models.Subcategory.objects.all()
    resource_name = 'subcategory'

  # Redefine get_object_list to filter for category_id.
  def get_object_list(self, request):
    category_id = request.GET.get('category_id', None)
    q_set = super(SubcategoryResource, self).get_object_list(request)
    try:
      category = models.Category.objects.get(id=category_id)
      q_set = q_set.filter(category=category)
    except ObjectDoesNotExist:
      pass
    return q_set

# User Resource.
class UserResource(ModelResource):
  class Meta:
    queryset = User.objects.all()
    resource_name = 'user'
    excludes = ['email','password','is_superuser']
