# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# API Resources
# This file contains the resources for the RESTful API using the
# django rest framework.

from tastypie.resources import ModelResource,fields
from paws.main import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

class UserResource(ModelResource):
	class Meta:
		queryset=User.objects.all()
		resource_name='user'
		excludes=['email','password','is_superuser']

class StaffResource(ModelResource):
	user=fields.ForeignKey(UserResource,'user', full= True)
	class Meta:
		queryset=models.Staff.objects.all()
		resource_name='staff'

class SpeciesResource(ModelResource):
  class Meta:
    queryset = models.Species.objects.all()
    resource_name = 'species'

 # def dehydrate(self, bundle):
  #	animals= models.Animal.objects.filter(species=bundle.data['id'])
  #	bundle.data['animals'] =[model_to_dict(c) for c in animals]
  #	return bundle

class CategoryResource(ModelResource):
	class Meta:
		queryset = models.Category.objects.all()
		resource_name = 'category'

class SubcategoryResource(ModelResource):
	category=fields.ForeignKey(CategoryResource, 'category', full = True)
	class Meta:
		queryset=models.Subcategory.objects.all()
		resource_name = 'subcategory'
	def get_object_list(self, request):
		category_id=request.GET.get('category_id', None)
		q_set=super(SubcategoryResource, self).get_object_list(request)
		try:
			category=models.Category.objects.get(id=category_id)
			q_set=q_set.filter(category=category)
		except ObjectDoesNotExist:
			pass
		return q_set

class AnimalResource(ModelResource):
	species=fields.ForeignKey(SpeciesResource, 'species', full = True)
	class Meta:
		queryset=models.Animal.objects.all()
		resource_name='animal'
	def get_object_list(self, request):
		species_id=request.GET.get('species_id', None)
		q_set=super(AnimalResource, self).get_object_list(request)
		try:
			species=models.Species.objects.get(id=species_id)
			q_set=q_set.filter(species=species)
		except ObjectDoesNotExist:
			pass
		return q_set


class EnrichmentResource(ModelResource):
	subcategory=fields.ForeignKey(SubcategoryResource,'subcategory', full = True)
	class Meta:
		queryset = models.Enrichment.objects.all()
		resource_name='enrichment'
	def get_object_list(self, request):
		subcategory_id=request.GET.get('subcategory_id', None)
		q_set=super(EnrichmentResource, self).get_object_list(request)
		try:
			subcategory=models.Subcategory.objects.get(id=subcategory_id)
			q_set=q_set.filter(subcategory=subcategory)
		except ObjectDoesNotExist:
			pass
		
		return q_set

class EnrichmentNoteResource(ModelResource):
	species = fields.ForeignKey(SpeciesResource, 'species', full= True)
	enrichment = fields.ForeignKey(EnrichmentResource,'enrichment', full = True)
	class Meta:
		queryset= models.EnrichmentNote.objects.all()
		resource_name='enrichmentNote'

class ObservationResource(ModelResource):
	enrichment=fields.ForeignKey(EnrichmentResource,'enrichment')
	staff=fields.ForeignKey(StaffResource,'staff')
	class Meta:
		queryset=models.Observation.objects.all()
		resource_name='observation'

class AnimalObservationResource(ModelResource):
	animal=fields.ForeignKey(AnimalResource,'animal', full = True)
	observation=fields.ForeignKey(ObservationResource,'observation')
	class Meta:
		queryset=models.AnimalObservation.objects.all()
		resource_name='animalObservation'