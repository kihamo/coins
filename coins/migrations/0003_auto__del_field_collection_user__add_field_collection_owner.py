# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Collection.user'
        db.delete_column('coins_collections', 'user_id')

        # Adding field 'Collection.owner'
        db.add_column('coins_collections', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Collection.user'
        db.add_column('coins_collections', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Collection.owner'
        db.delete_column('coins_collections', 'owner_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'coins.banknote': {
            'Meta': {'unique_together': "(('album', 'page', 'division'),)", 'object_name': 'Banknote', 'db_table': "'coins_banknotes'"},
            'album': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'booked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Collection']"}),
            'division': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'features': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_obverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_reverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.BanknoteIssue']"}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'coins.banknoteissue': {
            'Meta': {'object_name': 'BanknoteIssue', 'db_table': "'coins_banknote_issues'"},
            'catalog_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Country']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Currency']"}),
            'date_issue': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_obverse': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_reverse': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_obverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_reverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mintage': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'nominal': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Series']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'max_length': '1'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'coins.coin': {
            'Meta': {'unique_together': "(('album', 'page', 'division'),)", 'object_name': 'Coin', 'db_table': "'coins_coins'"},
            'album': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'booked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Collection']"}),
            'division': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'features': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'grade': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_obverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_reverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.CoinIssue']"}),
            'mint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.IssueMint']", 'null': 'True', 'blank': 'True'}),
            'packaged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'coins.coinissue': {
            'Meta': {'object_name': 'CoinIssue', 'db_table': "'coins_coin_issues'"},
            'alloy': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'catalog_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Country']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Currency']"}),
            'date_issue': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_edge': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_obverse': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_reverse': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'diameter': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_obverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_reverse': ('coins.utils.fields.CoinImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mintage': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mints': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['coins.Mint']", 'through': u"orm['coins.IssueMint']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'nominal': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Series']", 'null': 'True', 'blank': 'True'}),
            'thickness': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'max_length': '1'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'coins.collection': {
            'Meta': {'object_name': 'Collection', 'db_table': "'coins_collections'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'coins.country': {
            'Meta': {'ordering': "['iso']", 'object_name': 'Country', 'db_table': "'coins_countries'"},
            'current_currency': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'current_currency'", 'null': 'True', 'to': u"orm['coins.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'coins.currency': {
            'Meta': {'ordering': "['name']", 'object_name': 'Currency', 'db_table': "'coins_currencies'"},
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['coins.Country']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sign': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'coins.image': {
            'Meta': {'object_name': 'Image'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'coins.issuemint': {
            'Meta': {'object_name': 'IssueMint', 'db_table': "'coins_issue_mints'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.CoinIssue']"}),
            'mint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Mint']"}),
            'mint_mark': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.MintMark']", 'null': 'True', 'blank': 'True'}),
            'mintage': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'coins.mint': {
            'Meta': {'ordering': "['name']", 'object_name': 'Mint', 'db_table': "'coins_mints'"},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'coins.mintmark': {
            'Meta': {'ordering': "['mark']", 'object_name': 'MintMark', 'db_table': "'coins_mint_marks'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'marks'", 'to': u"orm['coins.Mint']"})
        },
        u'coins.series': {
            'Meta': {'ordering': "['name']", 'object_name': 'Series'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['coins']