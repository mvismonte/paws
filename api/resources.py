# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# API Resources
# This file contains the resources for the RESTful API using the
# django-tastypie.

import datetime
import json
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404, HttpResponse
from haystack.query import EmptySearchQuerySet, SearchQuerySet
from paws.main import models
from paws.main.utilities import bulk_import
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.http import HttpApplicationError, HttpUnauthorized, HttpBadRequest
from tastypie.resources import fields, ModelResource
from tastypie.utils import trailing_slash

# Custom Authentication
class CustomAuthentication(BasicAuthentication):

  def is_authenticated(self, request, **kwargs):
    return request.user.is_authenticated()


class AnimalObservationResource(ModelResource):
  """AnimalObservation Resource."""

  animal = fields.ToOneField(
      'paws.api.resources.AnimalResource','animal', full=True, related_name='animal_observations')
  observation = fields.ToOneField(
      'paws.api.resources.ObservationResource', 'observation', related_name='animal_observations')
  behavior = fields.ForeignKey(
      'paws.api.resources.BehaviorResource', 'behavior', full=True, null=True, blank=True)

  class Meta:
    authentication = CustomAuthentication()
    authorization = Authorization()
    queryset = models.AnimalObservation.objects.all()
    resource_name = 'animalObservation'
    list_allowed_methods = ['get','post','put', 'patch', 'delete']

  # A check to see if staff can modify this observation.
  def can_modify_observation(self, request, animalObservation_id):
    # Any superuser can modify an observation.
    if (request.user.is_superuser):
      return True

    try:
      observation = models.AnimalObservation.objects.get(
          id=animalObservation_id).observation
      return observation.staff.user == request.user
    except ObjectDoesNotExist:
      return True

  def obj_create(self, bundle, **kwargs):
    # Get the user of the observation by fully hydrating the bundle and then
    # check if the user is allowed to add to this observation.
    user = self.full_hydrate(bundle).obj.observation.staff.user
    if not bundle.request.user.is_superuser and user != bundle.request.user:
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot add other users' animal observations")
      )
    return super(AnimalObservationResource, self).obj_create(bundle, **kwargs)

  def obj_update(self, bundle, **kwargs):
    # Make sure that the user can modifty.
    ao_id = int(kwargs.pop('pk', None))
    if not self.can_modify_observation(bundle.request, ao_id):
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot edit other users' animal observations")
      )
    return super(AnimalObservationResource, self).obj_update(bundle, **kwargs)

  def obj_delete(self, bundle, **kwargs):
    # Make sure that the user can modifty.
    ao_id = int(kwargs.pop('pk', None))
    if not self.can_modify_observation(bundle.request, ao_id):
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot delete other users' animal observations")
      )
    return super(AnimalObservationResource, self).obj_delete(bundle, **kwargs)

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

  # Add useful numerical numbers for animal observation
  def dehydrate(self, bundle):
    # If there is no observation, set the rate equals to 0
    rate = 0
    if bundle.obj.interaction_time is not None and bundle.obj.observation_time is not None and bundle.obj.indirect_use is False and bundle.obj.observation_time != 0:
      # Add the rate of the interaction vs. total observation time
      # The rate = interaction time is divided by the total observation time
      rate = bundle.obj.interaction_time/float(bundle.obj.observation_time)

    # Add the rate into the API results
    bundle.data['rate'] = rate
    return bundle

  # override the url for a specific url path of searching
  def prepend_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/stats%s$"%
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('get_stats'), name="api_get_stats"),  
    ]

  # wraps the method 'get_seach' so that it can be called in a more functional way
  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(AnimalObservationResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  # Calculate interaction rate between one given enrichment with other given enrichments
  def get_stats(self, request, **kwargs):
    # get the animal_id from url
    animal_id= request.GET.get('animal_id', None)
    animal= models.Animal.objects.get (id=animal_id)
    q_set= self.get_object_list(request)
    # filter by animal_id if exists
    try:
      q_set.filter(animal=animal)
    except ObjectDoesNotExist:
      pass

    # list of different enrichment given to animal with id=animal_id
    enrichment_list=[]
    total_interaction=0.0
    for result in q_set:
      # updating the interaction time
      total_interaction +=result.interaction_time
      observation= models.Observation.objects.get(id=result.observation_id)
      # Make unique enrichment list
      if observation.enrichment in enrichment_list:
        pass
      else:
        enrichment_list.append(observation.enrichment)

    percent=[]
    # calculate the percentage of each enrichment's interaction time
    # over the total interaction time of animal with id=animal_id
    for e in enrichment_list:
      total_eachInteraction=0.0
      # behavior occurance
      positive=0
      NA=0
      negative=0
      avoid=0
      # total time of each occurance
      pos_interaction=0.0
      na_interaction=0.0
      neg_interaction=0.0
      avoid_interaction=0.0
      for result in q_set:
        if models.Observation.objects.get(id=result.observation_id).enrichment == e:
          behavior=models.Behavior.objects.get(id=result.behavior_id)
          total_eachInteraction += result.interaction_time
          if(behavior.reaction == 1):
            positive += 1
            pos_interaction+=result.interaction_time
          if(behavior.reaction == 0):
            NA += 1
            na_interaction+=result.interaction_time
          if(behavior.reaction == -1):
            negative += 1
            neg_interaction+=result.interaction_time
          if(behavior.reaction == -2):
            avoid += 1
            avoid_interaction+=result.interaction_time
        else:
          pass
      # Return 0 if the animal has never interacted with any enrichment
      if total_eachInteraction == 0.0:
        percentage=0.0
        pos_percentage=0.0
        na_percentage=0.0
        neg_percentage=0.0
        avoid_percentage=0.0
      else:
        percentage= total_eachInteraction/total_interaction
        pos_percentage= pos_interaction/total_eachInteraction
        na_percentage= na_interaction/total_eachInteraction
        neg_percentage= neg_interaction/total_eachInteraction
        avoid_percentage= avoid_interaction/total_eachInteraction
      # create bundle that stores the result object
      bundle = self.build_bundle(obj = e, request = request)
      # reformating the bundle
      # adding the enrichment name into the bundle
      bundle.data['Enrichment'] = e
      bundle.data['id']= e.id
      # adding the percentage into the bundle
      bundle.data['overall_percentage']=percentage
      bundle.data['positive_occurance']=positive
      bundle.data['positive_percentage']=pos_percentage
      bundle.data['na_occurance']=NA
      bundle.data['na_percentage']=na_percentage
      bundle.data['negative_interaction']=negative
      bundle.data['neg_occurance']=neg_percentage
      bundle.data['avoid_occuranve']=avoid
      bundle.data['avoid_percentage']=avoid_percentage
      # append the bundle into the list
      percent.append(bundle)


    # Specifiy the format of json output
    object_list = {
      'objects': percent,
    }

    # Return the search results in json format
    return self.create_response(request, object_list)


class AnimalResource(ModelResource):
  """Animal Resource."""

  animal_observations = fields.ToManyField(
      'paws.api.resources.AnimalObservationResource', 'animalobservation_set',
      related_name='animal', blank=True)
  species = fields.ForeignKey(
      'paws.api.resources.SpeciesResource', 'species', full=True)
  housing_group = fields.ForeignKey(
      'paws.api.resources.HousingGroupResource', 'housing_group',
      full=False, blank=True)

  class Meta:
    queryset = models.Animal.objects.all()
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    resource_name = 'animal'
    always_return_data = True
    list_allowed_methods = ['get','post','put','delete']

  # override the url for a specific url path of searching
  def prepend_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/search%s$" % 
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('get_search'), name="api_get_search"),
      url(r"^(?P<resource_name>%s)/bulk%s$" % 
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('bulk_add'), name="api_bulk_add"),
    ]

  # wraps the method 'get_seach' so that it can be called in a more functional way
  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(AnimalResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  # main function for searching
  def get_search(self, request, **kwargs):
    # checking user inputs' method
    self.method_check(request, allowed=['get'])
    self.is_authenticated(request)
    self.throttle_check(request)

    # Provide the results for a search query
    sqs = SearchQuerySet().models(models.Animal).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)
    try:
      page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
      raise Http404("Sorry, no results on that page.")

    # Create a list of objects that contains the search results
    objects = []
    for result in page.object_list:
      # create bundle that stores the result object
      bundle = self.build_bundle(obj = result.object, request = request)
      # reformating the bundle
      bundle = self.full_dehydrate(bundle)
      # adding the bundle into a list of objects
      objects.append(bundle)
    
    # Specifiy the format of json output
    object_list = {
      'objects': objects,
    }
    # Handle the recording of the user's access for throttling purposes.
    self.log_throttled_access(request)
    # Return the search results in json format
    return self.create_response(request, object_list)

  # Redefine get_object_list to filter for species_id and/or housingGroup_id
  def get_object_list(self, request):
    species_id = request.GET.get('species_id', None)
    housingGroup_id = request.GET.get('housing_id', None)
    q_set = super(AnimalResource, self).get_object_list(request)
     # Try filtering by species if it exists.
    try:
      species = models.Species.objects.get(id=species_id)
      q_set = q_set.filter(species=species)
    except ObjectDoesNotExist:
      pass
     # Try filtering by housingGroup if it exists.
    try:
      housinggroup = models.HousingGroup.objects.get(id=housingGroup_id)
      q_set = q_set.filter(housing_group=housinggroup)
    except ObjectDoesNotExist:
      pass
    return q_set

  # Bulk add view.
  def bulk_add(self, request, **kwargs):
    self.method_check(request, allowed=['post'])
    self.is_authenticated(request)
    self.throttle_check(request)

    # Make sure user is superuser
    if not request.user.is_superuser:
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot edit other users' observations")
      )

    # try to load the json file
    try:
      animal_list = json.loads(request.raw_post_data)
    except ValueError, e:
      raise ValueError('Bad JSON: %s' % e)
    print animal_list
    # import the data into the database
    import_animal= bulk_import.importAnimals(animal_list)
    # build imported animals bundles
    objects = []
    for result in import_animal:
      # create bundle that stores the result object
      bundle = self.build_bundle(obj = result, request = request)
      # reformating the bundle
      bundle = self.full_dehydrate(bundle)
      # adding the bundle into a list of objects
      objects.append(bundle)
    
    # Specifiy the format of json output
    object_list = {
      'objects': objects,
    }
    return self.create_response(request, object_list)


class BehaviorResource(ModelResource):
  """Behavior Resource."""

  enrichment = fields.ForeignKey(
      'paws.api.resources.EnrichmentResource','enrichment')

  class Meta:
    authentication = CustomAuthentication()
    authorization = Authorization()
    queryset = models.Behavior.objects.all()
    resource_name = 'behavior'
    list_allowed_methods = ['get','post','put','delete']
    always_return_data = True
  
  # Redefine get_object_list to filter for enrichment_id
  def get_object_list(self, request):
    enrichment_id = request.GET.get('enrichment_id', None)
    q_set = super(BehaviorResource, self).get_object_list(request)

    # Try filtering by enrichment if it exists.
    try:
      enrichment = models.Enrichment.objects.get(id=enrichment_id)
      q_set = q_set.filter(enrichment=enrichment)
    except ObjectDoesNotExist:
      pass

    return q_set


class CategoryResource(ModelResource):
  """Category Resource."""

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.Category.objects.all()
    resource_name = 'category'
    list_allowed_methods = ['get','post','put','delete']


class EnrichmentNoteResource(ModelResource):
  """Enrichment Note Resource."""

  species = fields.ForeignKey(
      'paws.api.resources.SpeciesResource', 'species', full=True)
  enrichment = fields.ForeignKey(
      'paws.api.resources.EnrichmentResource','enrichment', full=True)

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.EnrichmentNote.objects.all()
    resource_name = 'enrichmentNote'
    list_allowed_methods = ['get','post','put','delete']

  # Redefine get_object_list to filter for enrichment_id and species_id.
  def get_object_list(self, request):
    species_id = request.GET.get('species_id', None)
    enrichment_id = request.GET.get('enrichment_id', None)
    q_set = super(EnrichmentNoteResource, self).get_object_list(request)

    # Could filter by multiple species: split species_id by comma
    species_id_list = []
    if species_id != None:
      for s in species_id.split(','):
        if s != '':
          species_id_list.append(int(s))

    # Try filtering by species first.
    if species_id != None:
      try:
        species_list = models.Species.objects.filter(id__in=species_id_list)
        q_set = q_set.filter(species__in=species_list)
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


class EnrichmentResource(ModelResource):
  """Enrichment Resource."""

  subcategory = fields.ForeignKey(
    'paws.api.resources.SubcategoryResource','subcategory', full=True)

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.Enrichment.objects.all()
    resource_name = 'enrichment'
    list_allowed_methods = ['get','post','put','delete']

  # override the url for a specific url path of searching
  def prepend_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/search%s$" % 
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('get_search'), name="api_get_search"),
      url(r"^(?P<resource_name>%s)/bulk%s$" % 
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('bulk_add'), name="api_bulk_add"),
    ]

  # wraps the method 'get_seach' so that it can be called in a more functional way
  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(EnrichmentResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  # main function for searching
  def get_search(self, request, **kwargs):
    # checking user inputs' method
    self.method_check(request, allowed=['get'])
    # checking if the user is authenticated
    self.is_authenticated(request)  
    # checking if the user should be throttled 
    self.throttle_check(request)

    # Provide the results for a search query
    sqs = SearchQuerySet().models(models.Enrichment).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)
    try:
      page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
      raise Http404("Sorry, no results on that page.")

    # Create a list of objects that contains the search results
    objects = []
    for result in page.object_list:
      # create bundle that stores the result object
      bundle = self.build_bundle(obj = result.object, request = request)
      # reformating the bundle
      bundle = self.full_dehydrate(bundle)
      # adding the bundle into a list of objects
      objects.append(bundle)
    
    # Specifiy the format of json output
    object_list = {
      'objects': objects,
    }

    # Handle the recording of the user's access for throttling purposes.
    self.log_throttled_access(request)
    # Return the search results in json format
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

  # Bulk add view.
  def bulk_add(self, request, **kwargs):
    self.method_check(request, allowed=['post'])
    self.is_authenticated(request)
    self.throttle_check(request)

    # Make sure user is superuser.
    if not request.user.is_superuser:
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot bulk add")
      )

    # try loading the json
    try:
      enrichment_list = json.loads(request.raw_post_data)
    except ValueError, e:
      raise ValueError('Bad JSON: %s' % e)
    print enrichment_list
    # importing the new enrichment into the database
    import_enrichment=bulk_import.importEnrichments(enrichment_list)
    # build new enrichments bundles
    objects = []
    for result in import_enrichment:
      # create bundle that stores the result object
      bundle = self.build_bundle(obj = result, request = request)
      # reformating the bundle
      bundle = self.full_dehydrate(bundle)
      # adding the bundle into a list of objects
      objects.append(bundle)
    
    # Specifiy the format of json output
    object_list = {
      'objects': objects,
    }
    return self.create_response(request, object_list)


class ExhibitResource(ModelResource):
  """Exhibit Resource."""

  housing_groups = fields.ToManyField(
      'paws.api.resources.HousingGroupResource', 'housinggroup_set',
      full=True, blank=True)

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.Exhibit.objects.all()
    resource_name = 'exhibit'
    always_return_data = True
    list_allowed_methods = ['get','post','put','delete']


class HousingGroupResource(ModelResource):
  """HousingGroup Resource"""

  # exhibit = fields.ToOneField('paws.api.resources.ExhibitResource', 'exhibit')
  staff = fields.ToManyField(
      'paws.api.resources.StaffResource', 'staff', blank=True)
  animals = fields.ToManyField(
      'paws.api.resources.AnimalResource', 'animal_set', full=True, blank=True)
  exhibit = fields.ToOneField('paws.api.resources.ExhibitResource', 'exhibit')

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.HousingGroup.objects.all()
    resource_name = 'housingGroup'
    always_return_data = True
    list_allowed_methods = ['get','post','put','patch','delete']

  # Redefine get_object_list to filter for exhibit_id and staff_id.
  def get_object_list(self, request):
    staff_id = request.GET.get('staff_id', None)
    exhibit_id = request.GET.get('exhibit_id', None)
    animal_id = request.GET.get('animal_id', None)
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

    # Try filtering by animal if it exists
    try:
      animal = models.Animal.objects.get(id=animal_id)
      print animal.housing_group
      q_set = q_set.filter(id=animal.housing_group.id)
    except ObjectDoesNotExist:
      pass

    return q_set


class ObservationResource(ModelResource):
  """Observation Resource."""

  animal_observations = fields.ToManyField(
      'paws.api.resources.AnimalObservationResource','animalobservation_set', full=True, null=True, related_name='observation')
  enrichment = fields.ForeignKey(
      'paws.api.resources.EnrichmentResource','enrichment', full=True)
  staff = fields.ForeignKey(
      'paws.api.resources.StaffResource','staff')

  class Meta:
    authentication = CustomAuthentication()
    authorization = Authorization()
    queryset = models.Observation.objects.all()
    resource_name = 'observation'
    list_allowed_methods = ['get','post','put','delete']

  # A check to see if staff can modify this observation.
  def can_modify_observation(self, request, observation_id):
    # Any superuser can modify an observation.
    if (request.user.is_superuser):
      return True

    try:
      observation = models.Observation.objects.get(id=observation_id)
      return observation.staff.user == request.user
    except ObjectDoesNotExist:
      return True

  # update observation's information in the database
  def obj_update(self, bundle, **kwargs):
    # Make sure that the user can modifty.
    observation_id = int(kwargs.pop('pk', None))
    if not self.can_modify_observation(bundle.request, observation_id):
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot edit other users' observations")
      )
    return super(ObservationResource, self).obj_update(bundle, **kwargs)

  # delete observation from the database
  def obj_delete(self, bundle, **kwargs):
    # Make sure that the user can modifty.
    observation_id = int(kwargs.pop('pk', None))
    if not self.can_modify_observation(bundle.request, observation_id):
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot edit other users' observations")
      )
    return super(ObservationResource, self).obj_delete(bundle, **kwargs)

  # Redefine get_object_list to filter for enrichment_id and staff_id.
  def get_object_list(self, request):
    show_completed = request.GET.get('show_completed', None)
    staff_id = request.GET.get('staff_id', None)
    enrichment_id = request.GET.get('enrichment_id', None)
    q_set = super(ObservationResource, self).get_object_list(request)

    # Filter completed observations
    if not show_completed:
      q_set = q_set.filter(date_finished__isnull=True)

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


class SpeciesResource(ModelResource):
  """Species Resource."""

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.Species.objects.all()
    resource_name = 'species'
    always_return_data = True
    list_allowed_methods = ['get','post','put','delete']


class StaffResource(ModelResource):
  """Staff Resource."""

  user = fields.ToOneField(
      'paws.api.resources.UserResource', 'user', full=True)
  housing_group = fields.ToManyField('paws.api.resources.HousingGroupResource', 'housinggroup_set')

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.Staff.objects.all()
    resource_name = 'staff'
    list_allowed_methods = ['get','post','put','patch','delete']

  # override the url for a specific url path of searching
  def prepend_urls(self):
    return [
      url(r"^(?P<resource_name>%s)\.(?P<format>\w+)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
    ]

  # wraps the method 'get_seach' so that it can be called in a more functional way
  def wrap_view(self, view):
    def wrapper(request, *args, **kwargs):
      request.format = kwargs.pop('format', None)
      wrapped_view = super(StaffResource, self).wrap_view(view)
      return wrapped_view(request, *args, **kwargs)
    return wrapper

  # main function for searching
  def get_search(self, request, **kwargs):
    # checking user inputs' method
    self.method_check(request, allowed=['get'])
    # checking if the user is authenticated
    self.is_authenticated(request)  
    # checking if the user should be throttled 
    self.throttle_check(request)

    # Provide the results for a search query
    sqs = SearchQuerySet().models(models.Staff).load_all().auto_query(request.GET.get('q', ''))
    paginator = Paginator(sqs, 20)
    try:
      page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
      raise Http404("Sorry, no results on that page.")

    # Create a list of objects that contains the search results
    objects = []
    for result in page.object_list:
      # create bundle that stores the result object
      bundle = self.build_bundle(obj = result.object, request = request)
      # reformating the bundle
      bundle = self.full_dehydrate(bundle)
      # adding the bundle into a list of objects
      objects.append(bundle)
    
    # Specifiy the format of json output
    object_list = {
      'objects': objects,
    }

    # Handle the recording of the user's access for throttling purposes.
    self.log_throttled_access(request)
    # Return the search results in json format
    return self.create_response(request, object_list)

  # Redefine get_object_list to filter for animal_id.
  def get_object_list(self, request):
    animal_id = request.GET.get('animal_id', None)
    q_set = super(StaffResource, self).get_object_list(request)

    #Filtering by animals
    try:
      animal = models.Animal.objects.get(id=animal_id)
      housing_group = animal.housing_group
      q_set = housing_group.staff.all()
    except ObjectDoesNotExist:
      pass

    return q_set


class SubcategoryResource(ModelResource):
  """Subcategory Resource."""

  category = fields.ForeignKey(
      'paws.api.resources.CategoryResource', 'category', full=True)

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = models.Subcategory.objects.all()
    resource_name = 'subcategory'
    list_allowed_methods = ['get','post','put','delete']

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


class UserResource(ModelResource):
  """User Resource."""
  
  staff = fields.ToOneField(
      'paws.api.resources.StaffResource', 'staff', null=True)

  class Meta:
    authentication = CustomAuthentication()
    authorization = DjangoAuthorization()
    queryset = User.objects.all()
    resource_name = 'user'
    excludes = ['email','password']
    list_allowed_methods = ['get','post','put','delete']

  def prepend_urls(self):
    return [
        url(r"^(?P<resource_name>%s)/bulk%s$" % 
            (self._meta.resource_name, trailing_slash()), 
            self.wrap_view('bulk_add'), name="api_bulk_add"),
        url(r"^(?P<resource_name>%s)/add_user%s$" %
            (self._meta.resource_name, trailing_slash()),
            self.wrap_view('add_user'), name="api_add_user"),
    ]

  # Adding new user into the database
  def obj_create(self, bundle, **kwargs):
    try:
      bundle = super(UserResource,self).obj_create(bundle, **kwargs)
      bundle.obj.set_password(bundle.data.get('password'))
      bundle.obj.save()
    except IntegrityError:
      raise BadRequest('That username already exists')
    return bundle

  # Updating user's information
  def obj_update(self, bundle, **kwargs):
    try:
      bundle = super(UserResource,self).obj_update(bundle, **kwargs)
      bundle.obj.set_password(bundle.data.get('password'))
      bundle.obj.save()
    except IntegrityError:
      raise BadRequest('That username already exists')
    return bundle

  def add_user(self, request, **kwargs):
    self.method_check(request, allowed=['post'])
    self.is_authenticated(request)
    self.throttle_check(request)

    # Make sure user is superuser.
    if not request.user.is_superuser:
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot add user")
      )

    try:
      user = json.loads(request.raw_post_data)
      print user
      
      if user["first_name"] == "":
        return self.create_response(request, "Blank first name. Please fill in.", response_class=HttpBadRequest)
      if user["last_name"] == "":
        return self.create_response(request, "Blank last name. Please fill in.", response_class=HttpBadRequest)
      if user["password"] == "":
        return self.create_response(request, "Blank password. Please fill in.", response_class=HttpBadRequest)
      
      import_user = bulk_import.addUser(
          first_name = user["first_name"], 
          last_name = user["last_name"],
          password = user["password"],
          is_superuser = user["is_superuser"])
      object = self.build_bundle(obj=import_user, request=request)
      object = self.full_dehydrate(object)
      ret_user = {
        'object': object,
      }
      
      return self.create_response(request, ret_user)
    except ValueError:
      return self.create_response(request, "Invalid JSON", response_class=HttpApplicationError)

  # Bulk add view.
  def bulk_add(self, request, **kwargs):
    self.method_check(request, allowed=['post'])
    self.is_authenticated(request)
    self.throttle_check(request)

    # Make sure user is superuser.
    if not request.user.is_superuser:
      raise ImmediateHttpResponse(
          HttpUnauthorized("Cannot bulk add")
      )
 
    # Try making a new user
    try:
      user_list = json.loads(request.raw_post_data)
      print user_list
      import_users = bulk_import.importUsers(user_list)
      objects = []
      for result in import_users:
        bundle = self.build_bundle(obj=result, request=request)
        bundle = self.full_dehydrate(bundle)
        objects.append(bundle)

      object_list = {
        'objects': objects,
      }

      return self.create_response(request, object_list)
    except ValueError:
      return self.create_response(request, "Invalid JSON", response_class=HttpApplicationError)
