# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# API Resources
# This file contains the resources for the RESTful API using the
# django-tastypie.

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls.defaults import *
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.http import Http404
from django.http import HttpResponse
from paws.main import models
from tastypie.resources import fields
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.utils import trailing_slash
from tastypie.exceptions import BadRequest
from haystack.query import SearchQuerySet
from haystack.query import EmptySearchQuerySet

#Custom Authentication
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
    authorization=Authorization()
    queryset = models.AnimalObservation.objects.all()
    resource_name = 'animalObservation'
    #allowed actions towards database
    #get = getting animalObservation's information from the database
    #post = adding new animalObservation into the database
    #put = updating animalObservation's information in the database
    #delete = delete animalObservation from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new animalObservation into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(SpeciesResource, self).obj_create(bundle, request, **kwargs)
    
  #update animalObservation's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(SpeciesResource, self).obj_update(bundle, request, **kwargs)

  #delete animalObervation from the database
  def obj_delete(self, request=None, **kwargs):
    return super(AnimalObservationResource, self).obj_delete( request, **kwargs)

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

  #change the url format
  def override_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/calculation%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_calculation'), name="api_get_calculation"),
    ]

  def determine_format(self, request):
    if (hasattr(request,'format') and request.format in self._meta.serializer.formats):
      return self._meta.serializer.get_mime_for_format(request.format)
    return super(AnimalObservationResource, self).determine_format(request)

  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(AnimalObservationResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

 
# Animal Resource.
class AnimalResource(ModelResource):
  # Define foreign keys.
  species = fields.ForeignKey(
      'paws.api.resources.SpeciesResource', 'species', full=True)

  class Meta:
    #authenticate the user
    queryset = models.Animal.objects.all()
    resource_name = 'animal'
    #allowed actions towards database
    #get = getting animal's information from the database
    #post = adding new animal into the database
    #put = updating animal's information in the database
    #delete = delete animal from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new animal into database
  def obj_create(self, bundle, request=None, **kwargs):
    if self._meta.authorization.is_authorized(request):
      return super(AnimalResource, self).obj_create(bundle, request, **kwargs)
    
  #update animal's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(AnimalResource, self).obj_update(bundle, request, **kwargs)

  #delete animal from the database
  def obj_delete(self, request=None, **kwargs):
    return super(AnimalResource, self).obj_delete( request, **kwargs)

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

  # Redefine get_object_list to filter for species_id and/or housingGroup_id
  def get_object_list(self, request):
    species_id = request.GET.get('species_id', None)
    housingGroup_id=request.GET.get('housing_id', None)
    q_set = super(AnimalResource, self).get_object_list(request)
     # Try filtering by species if it exists.
    try:
      species = models.Species.objects.get(id=species_id)
      q_set = q_set.filter(species=species)
    except ObjectDoesNotExist:
      pass
     # Try filtering by housingGroup if it exists.
    try:
      housinggroup=models.HousingGroup.objects.get(id=housingGroup_id)
      q_set=q_set.filter(housing_group=housinggroup)
    except ObjectDoesNotExist:
      pass
    return q_set

# Category Resource.
class CategoryResource(ModelResource):
  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=Authorization()
    queryset = models.Category.objects.all()
    resource_name = 'category'
    #allowed actions towards database
    #get = getting category's information from the database
    #post = adding new category into the database
    #put = updating category's information in the database
    #delete = delete category from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new category into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(CategoryResource, self).obj_create(bundle, request, **kwargs)
    
  #update category's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(CategoryResource, self).obj_update(bundle, request, **kwargs)

  #delete category from the database
  def obj_delete(self, request=None, **kwargs):
    return super(CategoryResource, self).obj_delete( request, **kwargs)

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
    authorization=Authorization()
    queryset = models.EnrichmentNote.objects.all()
    resource_name = 'enrichmentNote'
    #allowed actions towards database
    #get = getting enrichmentNote's information from the database
    #post = adding new enrichmentNote into the database
    #put = updating enrichmentNote's information in the database
    #delete = delete enrichmentNote from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new enrichmentNote into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(EnrichmentNoteResource, self).obj_create(bundle, request, **kwargs)
    
  #update enrichmentNote's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(EnrichmentNoteResource, self).obj_update(bundle, request, **kwargs)

  #delete enrichmentNote from the database
  def obj_delete(self, request=None, **kwargs):
    return super(EnrichmentNoteResource, self).obj_delete( request, **kwargs)

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
    authorization=Authorization()
    queryset = models.Enrichment.objects.all()
    resource_name = 'enrichment'
    #allowed actions towards database
    #get = getting enrichment's information from the database
    #post = adding new enrichment into the database
    #put = updating enrichment's information in the database
    #delete = delete enrichment from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new enrichment into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(EnrichmentResource, self).obj_create(bundle, request, **kwargs)
    
  #update enrichment's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(EnrichmentResource, self).obj_update(bundle, request, **kwargs)

  #delete enrichment from the database
  def obj_delete(self, request=None, **kwargs):
    return super(EnrichmentResource, self).obj_delete( request, **kwargs)

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
    authorization=Authorization()
    queryset = models.Observation.objects.all()
    resource_name = 'observation'
    #allowed actions towards database
    #get = getting observation's information from the database
    #post = adding new observation into the database
    #put = updating observation's information in the database
    #delete = delete observation from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new observation into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(ObservationResource, self).obj_create(bundle, request, **kwargs)
    
  #update observation's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(ObservationResource, self).obj_update(bundle, request, **kwargs)

  #delete observation from the database
  def obj_delete(self, request=None, **kwargs):
    return super(ObservationResource, self).obj_delete( request, **kwargs)

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

# Exhibit Resource.
class ExhibitResource(ModelResource):
  housing_groups = fields.ToManyField('paws.api.resources.HousingGroupResource', 'housinggroup_set', full=True)
  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=Authorization()
    queryset = models.Exhibit.objects.all()
    resource_name = 'exhibit'
    #allowed actions towards database
    #get = getting exhibit's information from the database
    #post = adding new exhibit into the database
    #put = updating exhibit' information in the database
    #delete = delete exhibit from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new species into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(ExhibitResource, self).obj_create(bundle, request, **kwargs)
    
  #update exhibit's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(ExhibitResource, self).obj_update(bundle, request, **kwargs)

  #delete exhibit from the database
  def obj_delete(self, request=None, **kwargs):
    return super(ExhibitResource, self).obj_delete(request, **kwargs)

# Species Resource.
class SpeciesResource(ModelResource):
  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=Authorization()
    queryset = models.Species.objects.all()
    resource_name = 'species'
    #allowed actions towards database
    #get = getting species' information from the database
    #post = adding new species into the database
    #put = updating species' information in the database
    #delete = delete species from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new species into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(SpeciesResource, self).obj_create(bundle, request, **kwargs)
    
  #update species' information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(SpeciesResource, self).obj_update(bundle, request, **kwargs)

  #delete species from the database
  def obj_delete(self, request=None, **kwargs):
    return super(SpeciesResource, self).obj_delete(request, **kwargs)

#housingGroup Resource
class HousingGroupResource(ModelResource):
  #exhibit = fields.ToOneField('paws.api.resources.ExhibitResource', 'exhibit')
  staff = fields.ToManyField(
      'paws.api.resources.StaffResource', 'staff', related_name = 'housingGroup')
  animals = fields.ToManyField('paws.api.resources.AnimalResource', 'animal_set', full=True)
  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=Authorization()
    queryset = models.HousingGroup.objects.all()
    resource_name = 'housingGroup'
    #allowed actions towards database
    #get = getting HousingGroup's information from the database
    #post = adding new HousingGroup into the database
    #put = updating HousingGroup's information in the database
    #delete = delete HousingGroup from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new HousingGroup into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(HousingGroupResource, self).obj_create(bundle, request, **kwargs)
    
  #update HousingGroup's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(HousingGroupResource, self).obj_update(bundle, request, **kwargs)

  #delete HousingGroup from the database
  def obj_delete(self, request=None, **kwargs):
    return super(HousingGroupResource, self).obj_delete( request, **kwargs)

# Redefine get_object_list to filter for exhibit_id and staff_id.
  def get_object_list(self, request):
    staff_id = request.GET.get('staff_id', None)
    exhibit_id = request.GET.get('exhibit_id', None)
    q_set = super(HousingGroupResource, self).get_object_list(request)

    # Try filtering by staff_id if it exists.
    try:
      staff = models.Staff.objects.get(id=staff_id)
      q_set = q_set.filter(staff=staff)
    except ObjectDoesNotExist:
      pass

    # Try filtering by exhibit if it exists.
    try:
      exhibit = models.Exhibit.objects.get(id=exhibit_id)
      q_set = q_set.filter(exhibit=exhibit)
    except ObjectDoesNotExist:
      pass

    return q_set
# Staff Resource.
class StaffResource(ModelResource):
  user = fields.ToOneField(
      'paws.api.resources.UserResource', 'user', full=True)
  animals = fields.ToManyField(
      'paws.api.resources.AnimalResource', 'animals', related_name= 'animal')  
  class Meta:
    #authenticate the user
    authentication= customAuthentication()
    authorization=Authorization()
    queryset = models.Staff.objects.all()
    resource_name = 'staff'
    #allowed actions towards database
    #get = getting staff's information from the database
    #post = adding new staff into the database
    #put = updating staff's information in the database
    #delete = delete staff from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new staff into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(StaffResource, self).obj_create(bundle, request, **kwargs)
    
  #update staff's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(StaffResource, self).obj_update(bundle, request, **kwargs)

  #delete staff from the database
  def obj_delete(self, request=None, **kwargs):
    return super(StaffResource, self).obj_delete( request, **kwargs)

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

# Redefine get_object_list to filter for animal_id.
  def get_object_list(self, request):
    animal_id = request.GET.get('animal_id', None)
    q_set = super(StaffResource, self).get_object_list(request)
    try:
      animal = models.Animal.objects.get(id=animal_id)
      q_set = q_set.filter(animals=animal)
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
    authorization=Authorization()
    queryset = models.Subcategory.objects.all()
    resource_name = 'subcategory'
    #allowed actions towards database
    #get = getting subcategory information from the database
    #post = adding new subcategory into the database
    #put = update subcategory's information in the database
    #delete = delete subcategory from the database
    list_allowed_methods= ['get','post','put','delete']

  #creating new subcategory into database
  def obj_create(self, bundle, request=None, **kwargs):
    return super(SubcategoryResource, self).obj_create(bundle, request, **kwargs)
    
  #update subcategory's information in the database
  def obj_update(self, bundle, request=None, **kwargs):
    return super(SubcategoryResource, self).obj_update(bundle, request, **kwargs)

  #delete subcategory from the database
  def obj_delete(self, request=None, **kwargs):
    return super(SubcategoryResource, self).obj_delete( request, **kwargs)

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
    authorization=Authorization()
    queryset = User.objects.all()
    resource_name = 'user'
    excludes = ['email','password']
    #list of allowed actions towards the database
    # get = get the user from the database
    # post = adding new user into the database
    # put = updating user's information in the database
    # delete = delete the user from the database
    list_allowed_methods=['get','post','put','delete']

  #adding new user into the database
  def obj_create(self, bundle, request=None, **kwargs):
    try:
      bundle=super(UserResource,self).obj_create(bundle, request, **kwargs)
      bundle.obj.set_password(bundle.data.get('password'))
      bundle.obj.save()
    except IntegrityError:
      raise BadRequest('That username already exists')
    return bundle

  #updating user's information
  def obj_update(self, bundle, request=None, **kwards):
    try:
      bundle=super(UserResource,self).obj_update(bundle, request, **kwargs)
      bundle.obj.set_password(bundle.data.get('password'))
      bundle.obj.save()
    except IntegrityError:
      raise BadRequest('That username already exists')
    return bundle

  #deleting user from the database
  def obj_delete(self, request=None, **kwargs):
    return super(UserResource, self).obj_delete( request, **kwargs)
