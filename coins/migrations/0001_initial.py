# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table(u'coins_image', (
            ('hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('mime_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'coins', ['Image'])

        # Adding model 'Country'
        db.create_table('coins_countries', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('current_currency', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='current_currency', null=True, to=orm['coins.Currency'])),
        ))
        db.send_create_signal(u'coins', ['Country'])

        # Adding model 'Currency'
        db.create_table('coins_currencies', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sign', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal(u'coins', ['Currency'])

        # Adding M2M table for field countries on 'Currency'
        m2m_table_name = db.shorten_name('coins_currencies_countries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('currency', models.ForeignKey(orm[u'coins.currency'], null=False)),
            ('country', models.ForeignKey(orm[u'coins.country'], null=False))
        ))
        db.create_unique(m2m_table_name, ['currency_id', 'country_id'])

        # Adding model 'Collection'
        db.create_table('coins_collections', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'coins', ['Collection'])

        # Adding model 'Mint'
        db.create_table('coins_mints', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Country'])),
        ))
        db.send_create_signal(u'coins', ['Mint'])

        # Adding model 'MintMark'
        db.create_table('coins_mint_marks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('mint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Mint'])),
        ))
        db.send_create_signal(u'coins', ['MintMark'])

        # Adding model 'Series'
        db.create_table('coins_series', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'coins', ['Series'])

        # Adding model 'CoinIssue'
        db.create_table('coins_coin_issues', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, max_length=1)),
            ('nominal', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Country'])),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Currency'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('date_issue', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Series'], null=True, blank=True)),
            ('catalog_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('mintage', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image_obverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('desc_obverse', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image_reverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('desc_reverse', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('diameter', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('alloy', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('thickness', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('desc_edge', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'coins', ['CoinIssue'])

        # Adding model 'BanknoteIssue'
        db.create_table('coins_banknote_issues', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, max_length=1)),
            ('nominal', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Country'])),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Currency'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('date_issue', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Series'], null=True, blank=True)),
            ('catalog_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('mintage', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image_obverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('desc_obverse', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image_reverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('desc_reverse', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('height', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'coins', ['BanknoteIssue'])

        # Adding model 'IssueMint'
        db.create_table('coins_issue_mints', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.CoinIssue'])),
            ('mint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.Mint'])),
            ('mint_mark', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.MintMark'], null=True, blank=True)),
            ('mintage', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'coins', ['IssueMint'])

        # Adding model 'Coin'
        db.create_table('coins_coins', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['coins.Collection'])),
            ('grade', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('image_obverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('image_reverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('packaged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('booked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('features', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('album', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('page', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('division', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.CoinIssue'])),
            ('mint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.IssueMint'], null=True, blank=True)),
        ))
        db.send_create_signal(u'coins', ['Coin'])

        # Adding unique constraint on 'Coin', fields ['album', 'page', 'division']
        db.create_unique('coins_coins', ['album', 'page', 'division'])

        # Adding model 'Banknote'
        db.create_table('coins_banknotes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['coins.Collection'])),
            ('grade', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('image_obverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('image_reverse', self.gf('coins.utils.fields.CoinImageField')(max_length=100, null=True, blank=True)),
            ('packaged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('booked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('features', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('album', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('page', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('division', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coins.BanknoteIssue'])),
        ))
        db.send_create_signal(u'coins', ['Banknote'])

        # Adding unique constraint on 'Banknote', fields ['album', 'page', 'division']
        db.create_unique('coins_banknotes', ['album', 'page', 'division'])


    def backwards(self, orm):
        # Removing unique constraint on 'Banknote', fields ['album', 'page', 'division']
        db.delete_unique('coins_banknotes', ['album', 'page', 'division'])

        # Removing unique constraint on 'Coin', fields ['album', 'page', 'division']
        db.delete_unique('coins_coins', ['album', 'page', 'division'])

        # Deleting model 'Image'
        db.delete_table(u'coins_image')

        # Deleting model 'Country'
        db.delete_table('coins_countries')

        # Deleting model 'Currency'
        db.delete_table('coins_currencies')

        # Removing M2M table for field countries on 'Currency'
        db.delete_table(db.shorten_name('coins_currencies_countries'))

        # Deleting model 'Collection'
        db.delete_table('coins_collections')

        # Deleting model 'Mint'
        db.delete_table('coins_mints')

        # Deleting model 'MintMark'
        db.delete_table('coins_mint_marks')

        # Deleting model 'Series'
        db.delete_table('coins_series')

        # Deleting model 'CoinIssue'
        db.delete_table('coins_coin_issues')

        # Deleting model 'BanknoteIssue'
        db.delete_table('coins_banknote_issues')

        # Deleting model 'IssueMint'
        db.delete_table('coins_issue_mints')

        # Deleting model 'Coin'
        db.delete_table('coins_coins')

        # Deleting model 'Banknote'
        db.delete_table('coins_banknotes')


    models = {
        u'coins.banknote': {
            'Meta': {'unique_together': "(('album', 'page', 'division'),)", 'object_name': 'Banknote', 'db_table': "'coins_banknotes'"},
            'album': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'booked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['coins.Collection']"}),
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
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['coins.Collection']"}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'mint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['coins.Mint']"})
        },
        u'coins.series': {
            'Meta': {'ordering': "['name']", 'object_name': 'Series'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['coins']