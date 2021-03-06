# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# Main Models
# This file contains the main models for the PAWS project.

from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Animal Model
class Animal(models.Model):
  count = models.PositiveIntegerField(default=1)
  housing_group = models.ForeignKey('HousingGroup')
  name = models.CharField(max_length=100, null=False, blank=False)
  species = models.ForeignKey('Species')
  def __unicode__(self):
    return self.name

# AnimalObservation Model
class AnimalObservation(models.Model):
  # Fields
  animal = models.ForeignKey('Animal')
  observation = models.ForeignKey('Observation')
  interaction_time = models.PositiveIntegerField(null=True, blank=True)
  observation_time= models.PositiveIntegerField(null=True,blank=True)
  behavior = models.ForeignKey('Behavior', null=True, blank=True)
  indirect_use = models.BooleanField(default=False)
  def __unicode__(self):
    r = ''
    try:
      r = "%s for %s" % (self.observation.enrichment.name, self.animal.name)
    except ObjectDoesNotExist:
      r = "Animal Observation"
    return r

# BehaviorModel
class Behavior(models.Model):
  BEHAVIOR_CHOICES = (
    (-2, 'Avoid'),
    (-1, 'Negative'),
    (0, 'N/A'),
    (1, 'Positive'),
  )
  reaction = models.SmallIntegerField(choices=BEHAVIOR_CHOICES, null=True, default='0')
  enrichment = models.ForeignKey('Enrichment')
  description = models.TextField(blank=True)
  def __unicode__(self):
    name='Positive'
    if self.reaction == 0 :
      name='N/A'
    if self.reaction == -1 :
      name='Negative'
    if self.reaction == -2 :
      name='Avoid'
    return "%s for %s with description: %s" % (name,self.enrichment, self.description)

# Category Model
class Category(models.Model):
  name = models.CharField(max_length=100, null=False, blank=False)
  def __unicode__(self):
    return self.name

# Enrichment Model
class Enrichment(models.Model):
  subcategory = models.ForeignKey('Subcategory')
  name = models.CharField(max_length=100, null=False, blank=False)
  def __unicode__(self):
    return self.name

# EnrichmentNote Model
class EnrichmentNote(models.Model):
  species = models.ForeignKey('Species')
  enrichment = models.ForeignKey('Enrichment')
  limitations = models.TextField()
  instructions = models.TextField()
  def __unicode__(self):
    return "%s for %s" % (self.enrichment.name, self.species.common_name)

# Exhibit Model
class Exhibit(models.Model):
  code = models.CharField(max_length=100)
  def __unicode__(self):
    return self.code

# HousingGroup Model
class HousingGroup(models.Model):
  name = models.CharField(max_length=100, null=False, blank=True)
  staff = models.ManyToManyField('Staff')
  exhibit = models.ForeignKey('Exhibit')
  def __unicode__(self):
    return self.name

# Observation Model
class Observation(models.Model):
  enrichment = models.ForeignKey('Enrichment')
  staff = models.ForeignKey('Staff')
  date_created = models.DateTimeField(default=datetime.now())
  date_finished = models.DateTimeField(null=True, blank=True)
  def __unicode__(self):
    return "%s by %s on %s" % (self.enrichment.name,
        self.staff.user.username, unicode(self.date_created))

# Species Model
class Species(models.Model):
  common_name = models.CharField(max_length=100, null=False, blank=False)
  scientific_name = models.CharField(max_length=200, null=False, blank=False)
  def __unicode__(self):
    return "%s (%s)" % (self.common_name, self.scientific_name)

# Staff Model
class Staff(models.Model):
  user = models.OneToOneField(User)
  def __unicode__(self):
    return self.user.username

# Subcategory Model
class Subcategory(models.Model):
  category = models.ForeignKey('Category')
  name = models.CharField(max_length=100, null=False, blank=False)
  def __unicode__(self):
    return self.name 
