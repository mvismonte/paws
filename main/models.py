# Copyright 2012 PAWS. All rights reserved.
# Date: 4/30/2012
# Main Models
# This file contains the main models for the PAWS project.

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

# Staff Model
class Staff(models.Model):
  user = models.OneToOneField(User)
  animals = models.ManyToManyField('Animal')

# Species Model
class Species(models.Model):
  common_name = models.CharField(max_length=100, null=False, blank=False)
  scientific_name = models.CharField(max_length=200, null=False, blank=False)

# Animal Model
class Animal(models.Model):
  species = models.ForeignKey('Species')
  name = models.CharField(max_length=100, null=False, blank=False)

# Category Model
class Category(models.Model):
  name = models.CharField(max_length=100, null=False, blank=False)

# Subcategory Model
class Subcategory(models.Model):
  category = models.ForeignKey('Category')
  name = models.CharField(max_length=100, null=False, blank=False)

# Enrichment Model
class Enrichment(models.Model):
  subcategory = models.ForeignKey('Subcategory')
  name = models.CharField(max_length=100, null=False, blank=False)

# EnrichmentNote Model
class EnrichmentNote(models.Model):
  species = models.ForeignKey('Species')
  enrichment = models.ForeignKey('Enrichment')
  limitations = models.TextField()
  instructions = models.TextField()

# AnimalObservation Model
class AnimalObservation(models.Model):
  BEHAVIOR_CHOICES = (
    (-2, 'Avoid'),
    (-1, 'Negative'),
    (0, 'N/A'),
    (1, 'Positive'),
  )

  # Fields
  animal = models.ForeignKey('Animal')
  observation = models.ForeignKey('Observation')
  interaction_time = models.PositiveIntegerField(null=True, blank=True)
  behavior = models.SmallIntegerField(choices=BEHAVIOR_CHOICES)
  description = models.TextField()
  indirect_use = models.BooleanField()

# Observation Model
class Observation(models.Model):
  enrichment = models.ForeignKey('Enrichment')
  staff = models.ForeignKey('Staff')
  date_created = models.DateTimeField()
  date_finished = models.DateTimeField()
