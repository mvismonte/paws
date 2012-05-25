# Copyright 2012 PAWS. All rights reserved.
# Date: 5/5/2012
# Main Utility Bulk importer
# This is utility script used to import enrichments and animals into the
# database.

from paws.main import models

# A function that takes in a file name and tries to import the database.
# Example usage:
# >> from main.utilities import bulk_import
# >> bulk_import.importEnrichments('/home/mark/paws/main/utilities/list_enrichments.csv')
# TODO(Mark): Change this function so that it takes in a string instead.
def importEnrichments(file):
  try:
    f = open(file, 'r+')
  except IOError:
    # Return false if the file does not exist.
    print "File does not exist: %s" % (file)
    return False

  # Iterate through the file and add populate the database.
  # Lines are in the following format:
  #   <Unique ID>, <Common Name>, <Scientific Name>, <Category>,
  #   <Sub Category>, <Enrichment Item>, <Limitations>, <Presentation>
  for line in f:
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

  # Don't forget to close the file!
  f.close()
  return True

# A function that takes in a file name and tries to import the database.
# Example usage:
# >> from main.utilities import bulk_import
# >> bulk_import.importEnrichments('/home/mark/paws/main/utilities/list_enrichments.csv')
def importAnimals(data):
  # The data should be a list of strings where each string a line of the csv.

  lastExhibit = None
  lastGroup = None
  for line in data:
    fields = line.split(',')

    # Extract fields.
    scientific_name = fields[0]
    common_name = fields[1]
    house_name = fields[2]
    new_group = fields[3] != ''
    exhibit_code = fields[4]

    # Use get_or_create to create all models from the one line of the csv.
    species, create = models.Species.objects.get_or_create(
        common_name=common_name, scientific_name=scientific_name)
    exhibit, create = models.Exhibit.objects.get_or_create(code=exhibit_code)

    housing_group = None
    if (new_group):
      housing_group, create = models.HousingGroup.objects.get_or_create(
          exhibit=exhibit, name='')
    else:
      housing_group = lastGroup

    animal, create = models.Animal.objects.get_or_create(
        name=house_name, species=species, housing_group=housing_group)

    lastGroup = housing_group
    lastExhibit = exhibit

