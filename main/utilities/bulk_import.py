# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# Main Utility Bulk importer
# This is utility script used to import enrichments and animals into the
# database.

from paws.main import models
from django.core.exceptions import ObjectDoesNotExist

# A function that takes in a file name and tries to import the database.
# Example usage:
# >> from main.utilities import bulk_import
# >> bulk_import.importEnrichments('/home/mark/paws/main/utilities/list_enrichments.csv')
# TODO(Mark): Change this function so that it takes in a string instead.
def importEnrichments(data):
  enrichment_list=[]
  # Iterate through the data array and tries to import to database.
  # Lines are in the following format:
  #   <Unique ID>, <Common Name>, <Scientific Name>, <Category>,
  #   <Sub Category>, <Enrichment Item>, <Limitations>, <Presentation>
  for line in data:
    fields = line.split(',')

    # Make sure that the line is properly formatted.
    if (len(fields) != 8):
      continue

    # Extract fields.
    common_name = fields[1]
    scientific_name = fields[2]
    category_name = fields[3]
    subcategory_name = fields[4]
    enrichment_name = fields[5]
    enrichment_limitations = fields[6]
    enrichment_presentation = fields[7]

    # Use get_or_create to create all models from the one line of the csv.
    species, create = models.Species.objects.get_or_create(
        common_name=common_name, scientific_name=scientific_name)
    category, create = models.Category.objects.get_or_create(
        name=category_name)
    subcategory, create = models.Subcategory.objects.get_or_create(
        name=subcategory_name, category=category)
    enrichment, create = models.Enrichment.objects.get_or_create(
        name=enrichment_name, subcategory=subcategory)
    if (len(enrichment_limitations) > 0 or len(enrichment_presentation) > 0):
      enrichment_note, create =  models.EnrichmentNote.objects.get_or_create(
        species=species, limitations=enrichment_limitations,
        enrichment=enrichment, instructions=enrichment_presentation)
    enrichment_list.append(enrichment)
  return enrichment_list

# A function that takes in a file name and tries to import the database.
# Example usage:
# >> from main.utilities import bulk_import
# >> bulk_import.importEnrichments('/home/mark/paws/main/utilities/list_enrichments.csv')
def importAnimals(data):
  animal_list=[]
  # The data should be a list of strings where each string a line of the csv.
  # <unique_id>, <common_name>, <scientific_name>
  # <exhibit>, <house_group>, <house_name>, <count>
  for line in data:
    fields = line.split(',')

    if (len(fields) != 7):
      continue

    # Extract fields.
    id=fields[0]
    common_name = fields[1]
    scientific_name = fields[2]
    exhibit_code = fields[3]
    group_name = fields[4] != ''
    house_name = fields[5]
    count=fields[6]

    # Use get_or_create to create all models from the one line of the csv.
    species, create = models.Species.objects.get_or_create(
        common_name=common_name, scientific_name=scientific_name)
    exhibit, create = models.Exhibit.objects.get_or_create(code=exhibit_code)
    housing_group, create = models.HousingGroup.objects.get_or_create(
      exhibit=exhibit, name=group_name)

    animal, create = models.Animal.objects.get_or_create(id=id,
        name=house_name, species=species, housing_group=housing_group, count=count)
    animal_list.append(animal)
  return animal_list

# Add a single user
def addUser(first_name, last_name, password, is_superuser):
  # Make username based on first and last name of user 
  username = first_name[0] + last_name
  username = username.lower()
  count = 0    

  original_username = username

  # Check if the username is already in the database
  unique = False

  # While User is still in the database
  while not unique:
    # Try to get the User with username username
    try:
      user = models.User.objects.get(username=username)

      # Append a number to the username if it already exists
      count += 1
      username = original_username + str(count)

    except ObjectDoesNotExist:
      # Username has not been used before, create new user
      user = models.User.objects.create_user(
          username=username,
          password=password,
          email=' ' )
      user.is_superuser = is_superuser=="1"
      user.first_name = first_name
      user.last_name = last_name
      user.save()

      # Add associated staff to user
      staff = models.Staff.objects.create(user=user)
      staff.save()

      user_list.append(user);

      # Now the user is unique
      unique = True


# Add a bulk of users
def importUsers(array):
  user_list = []

  # Gets an array of user data
  # Formatted as <first_name>, <first_name>, <password>, <is_superuser>
  for line in array:
    # The fields are divided by comma
    fields = line.split(',')

    # Check the line for proper format
    if len(fields) != 4:
      continue

    first_name = fields[0]
    last_name = fields[1]
    password = fields[2]
    is_superuser = fields[3]
    
    addUser(
        first_name=first_name,
        last_name=last_name,
        password=password,
        is_superuser=is_superuser)

  return user_list

