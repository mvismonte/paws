from haystack.indexes import * 
from haystack.sites import site
from paws.main import models

class AnimalIndex(SearchIndex):
	text = CharField(document = True, use_template = True)
	species = CharField(model_attr = 'species')
	name = CharField(model_attr = 'name')

class EnrichmentIndex(SearchIndex):
	text = CharField(document = True, use_template = True)
	subcategory = CharField(model_attr = 'subcategory')
	name = CharField(model_attr = 'name')

site.register(models.Animal, AnimalIndex)
site.register(models.Enrichment, EnrichmentIndex)