# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Staff'
        db.create_table('main_staff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('main', ['Staff'])

        # Adding M2M table for field animals on 'Staff'
        db.create_table('main_staff_animals', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('staff', models.ForeignKey(orm['main.staff'], null=False)),
            ('animal', models.ForeignKey(orm['main.animal'], null=False))
        ))
        db.create_unique('main_staff_animals', ['staff_id', 'animal_id'])

        # Adding model 'Species'
        db.create_table('main_species', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('common_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('scientific_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('main', ['Species'])

        # Adding model 'Animal'
        db.create_table('main_animal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Species'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Animal'])

        # Adding model 'Category'
        db.create_table('main_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Category'])

        # Adding model 'Subcategory'
        db.create_table('main_subcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Subcategory'])

        # Adding model 'Enrichment'
        db.create_table('main_enrichment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Subcategory'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Enrichment'])

        # Adding model 'EnrichmentNote'
        db.create_table('main_enrichmentnote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('species', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Species'])),
            ('enrichment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Enrichment'])),
            ('limitations', self.gf('django.db.models.fields.TextField')()),
            ('instructions', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('main', ['EnrichmentNote'])

        # Adding model 'AnimalObservation'
        db.create_table('main_animalobservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('animal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Animal'])),
            ('observation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Observation'])),
            ('interaction_time', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('behavior', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('indirect_use', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('main', ['AnimalObservation'])

        # Adding model 'Observation'
        db.create_table('main_observation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('enrichment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Enrichment'])),
            ('staff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Staff'])),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_finished', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('main', ['Observation'])


    def backwards(self, orm):
        
        # Deleting model 'Staff'
        db.delete_table('main_staff')

        # Removing M2M table for field animals on 'Staff'
        db.delete_table('main_staff_animals')

        # Deleting model 'Species'
        db.delete_table('main_species')

        # Deleting model 'Animal'
        db.delete_table('main_animal')

        # Deleting model 'Category'
        db.delete_table('main_category')

        # Deleting model 'Subcategory'
        db.delete_table('main_subcategory')

        # Deleting model 'Enrichment'
        db.delete_table('main_enrichment')

        # Deleting model 'EnrichmentNote'
        db.delete_table('main_enrichmentnote')

        # Deleting model 'AnimalObservation'
        db.delete_table('main_animalobservation')

        # Deleting model 'Observation'
        db.delete_table('main_observation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('codename',)", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.animal': {
            'Meta': {'object_name': 'Animal'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Species']"})
        },
        'main.animalobservation': {
            'Meta': {'object_name': 'AnimalObservation'},
            'animal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Animal']"}),
            'behavior': ('django.db.models.fields.SmallIntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indirect_use': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'interaction_time': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Observation']"})
        },
        'main.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.enrichment': {
            'Meta': {'object_name': 'Enrichment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Subcategory']"})
        },
        'main.enrichmentnote': {
            'Meta': {'object_name': 'EnrichmentNote'},
            'enrichment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Enrichment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'limitations': ('django.db.models.fields.TextField', [], {}),
            'species': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Species']"})
        },
        'main.observation': {
            'Meta': {'object_name': 'Observation'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_finished': ('django.db.models.fields.DateTimeField', [], {}),
            'enrichment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Enrichment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Staff']"})
        },
        'main.species': {
            'Meta': {'object_name': 'Species'},
            'common_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scientific_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'main.staff': {
            'Meta': {'object_name': 'Staff'},
            'animals': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Animal']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'main.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['main']
