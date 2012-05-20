# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# API Resources
# This file contains the resources for the RESTful API using the
# django-tastypie.

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from paws.main import models
from tastypie.resources import fields, ModelResource
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import Authorization, DjangoAuthorization

from django.conf.urls.defaults import *
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404, HttpResponse
from tastypie.resources import fields, ModelResource
from tastypie.utils import trailing_slash
from haystack.query import SearchQuerySet, EmptySearchQuerySet
from tastypie.exceptions import BadRequest

#custom authentication
class customAuthentication(BasicAuthentication):
  def __init__(self,*args,**kwargs):
    super(customAuthentication,self).__init__(*args,**kwargs)

  def is_authenticated(self, request, **kwargs):
    return request.user.is_authenticated()


# AnimalObservation Resource.
class AnimalObservationResource(ModelResource):
  # Define foreign keys.
  animal = fields.ForeignKey(
      'paws.api.resources.AnimalResource','animal', full=True)
  observation = fields.ForeignKey(
      'paws.api.resources.ObservationResource', 'observation')

  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
    queryset = models.Animal.objects.all()
    resource_name = 'animal'

  def override_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
    ]

  def determine_format(self, request):
    if (hasattr(request,'format') and request.format in self._meta.serializer.formats):
      return self._meta.serializer.get_mime_for_format(request.format)
    return super(AnimalResource, self).determine_format(request)

  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(AnimalResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  def get_search(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    self.is_authenticated(request)  
    self.throttle_check(request)

    #return HttpResponse("You are here")

    sqs = SearchQuerySet().models(models.Animal).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)

    try:
      page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
      raise Http404("Sorry, no results on that page.")

    objects = []
    for result in page.object_list:
      bundle = self.build_bundle(obj = result.object, request = request)
      bundle = self.full_dehydrate(bundle)
      objects.append(bundle)
    
    object_list = {
      'objects': objects,
    }
    self.log_throttled_access(request)
    return self.create_response(request, object_list)

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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
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
      enrichment = models.Enrichment.objects.get(id=enrichment_id)
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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
    queryset = models.Enrichment.objects.all()
    resource_name = 'enrichment'

  def override_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
    ]

  def determine_format(self, request):
    if (hasattr(request,'format') and request.format in self._meta.serializer.formats):
      return self._meta.serializer.get_mime_for_format(request.format)
    return super(EnrichmentResource, self).determine_format(request)

  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(EnrichmentResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  def get_search(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    self.is_authenticated(request)  
    self.throttle_check(request)

    #return HttpResponse("You are here")

    sqs = SearchQuerySet().models(models.Enrichment).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)

    try:
      page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
      raise Http404("Sorry, no results on that page.")

    objects = []
    for result in page.object_list:
      bundle = self.build_bundle(obj = result.object, request = request)
      bundle = self.full_dehydrate(bundle)
      objects.append(bundle)
    
    object_list = {
      'objects': objects,
    }
    self.log_throttled_access(request)
    return self.create_response(request, object_list)

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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
    queryset = models.Species.objects.all()
    resource_name = 'species'
  #determine user's authority
  def apply_authorization_limits(self,request,object_list):
    if request.user.is_superuser==False:
      return object_list.filter(id=request.user.id)
    return object_list.all()
# Staff Resource.
class StaffResource(ModelResource):
  user = fields.ToOneField(
      'paws.api.resources.UserResource', 'user', full=True)
  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
    queryset = models.Staff.objects.all()
    resource_name = 'staff'

  def override_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
    ]

  def determine_format(self, request):
    if (hasattr(request,'format') and request.format in self._meta.serializer.formats):
      return self._meta.serializer.get_mime_for_format(request.format)
    return super(StaffResource, self).determine_format(request)

  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(StaffResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  def get_search(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    self.is_authenticated(request)  
    self.throttle_check(request)

    #return HttpResponse("You are here")

    sqs = SearchQuerySet().models(models.Staff).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)

    try:
      page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
      raise Http404("Sorry, no results on that page.")

    objects = []
    for result in page.object_list:
      bundle = self.build_bundle(obj = result.object, request = request)
      bundle = self.full_dehydrate(bundle)
      objects.append(bundle)
    
    object_list = {
      'objects': objects,
    }
    self.log_throttled_access(request)
    return self.create_response(request, object_list)

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


# Subcategory Resource.
class SubcategoryResource(ModelResource):
  # Define foreign keys.
  category = fields.ForeignKey(
      'paws.api.resources.CategoryResource', 'category', full=True)

  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
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
    #authenticate the user
    authentication= customAuthentication()
    authorization=DjangoAuthorization()
    queryset = User.objects.all()
    resource_name = 'user'
    excludes = ['email','password']


