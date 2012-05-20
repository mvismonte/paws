# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Exhibit'
        db.create_table('main_exhibit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('main', ['Exhibit'])

        # Adding model 'HousingGroup'
        db.create_table('main_housinggroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('exhibit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Exhibit'])),
        ))
        db.send_create_signal('main', ['HousingGroup'])

        # Adding M2M table for field staff on 'HousingGroup'
        db.create_table('main_housinggroup_staff', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('housinggroup', models.ForeignKey(orm['main.housinggroup'], null=False)),
            ('staff', models.ForeignKey(orm['main.staff'], null=False))
        ))
        db.create_unique('main_housinggroup_staff', ['housinggroup_id', 'staff_id'])

        # Adding field 'Animal.count'
        db.add_column('main_animal', 'count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Animal.housing_group'
        db.add_column('main_animal', 'housing_group',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=-1, to=orm['main.HousingGroup']),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'Exhibit'
        db.delete_table('main_exhibit')

        # Deleting model 'HousingGroup'
        db.delete_table('main_housinggroup')

        # Removing M2M table for field staff on 'HousingGroup'
        db.delete_table('main_housinggroup_staff')

        # Deleting field 'Animal.count'
        db.delete_column('main_animal', 'count')

        # Deleting field 'Animal.housing_group'
        db.delete_column('main_animal', 'housing_group_id')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'housing_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.HousingGroup']"}),
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
        'main.exhibit': {
            'Meta': {'object_name': 'Exhibit'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.housinggroup': {
            'Meta': {'object_name': 'HousingGroup'},
            'exhibit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Exhibit']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'staff': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Staff']", 'symmetrical': 'False'})
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