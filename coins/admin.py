# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse

from django.contrib import admin
from django.forms import ModelForm

from utils.widgets import AdminImageFileWidget
from views import barcode as barcode_view
from models import *

# -------- Actions --------

# TODO:
def print_boxes_not_packed(modeladmin, request, queryset):
    pass
print_boxes_not_packed.short_description = _('Print coin boxes only not packed coins')

# TODO:
def print_boxes_all(modeladmin, request, queryset):
    pass
print_boxes_all.short_description = _('Print coin boxes for all coins')

# -------- Inline --------
class CountryInline(admin.TabularInline):
    model = Country
    extra = 1
    readonly_fields = ('name', 'iso')

class MintMarkInline(admin.TabularInline):
    model = MintMark
    extra = 1

class CoinInline(admin.StackedInline):
    model = Coin
    extra = 1
    readonly_fields = ('barcode','qr_code')

    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('barcode', 'qr_code', 'collection', 'mint', 'mint_mark', 'grade', 'in_album', 'packaged')
        }),
        (None, {
            'classes': ('wide',),
            'fields': ('image_obverse', 'image_reverse')
        }),
        (None, {
            'classes': ('wide',),
            'fields': ('features',)
        })
    )

    formfield_overrides = {
        models.ImageField: {
            'widget': AdminImageFileWidget
        },
    }

    def _show_barcode_image(self, model, type):
        if not model.id or not model.issue:
            return ''

        url = reverse(barcode_view, args=[model.id, type])
        return '<img src="%s" alt="%s"/>' % (url, ugettext('Coin barcode'))

    def barcode(self, coin):
        return self._show_barcode_image(coin, 'code128')
    barcode.allow_tags = True

    def qr_code(self, coin):
        return self._show_barcode_image(coin, 'qr')
    qr_code.allow_tags = True

class CoinCollectionInline(CoinInline):
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('barcode', 'qr_code', 'issue', 'collection', 'mint', 'mint_mark', 'grade', 'in_album', 'packaged')
        }),
        (None, {
            'classes': ('wide',),
            'fields': ('image_obverse', 'image_reverse')
        }),
        (None, {
            'classes': ('wide',),
            'fields': ('features',)
        })
    )

# -------- General --------
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'coins_count')
    list_display_links = ('name',)
    inlines = (CoinCollectionInline,)

class CountryAdmin(admin.ModelAdmin):
    list_display = ('iso', 'name', 'currency')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('iso', 'name')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']
    ordering = ['iso']
    inlines = (CountryInline,)

class MintAdmin(admin.ModelAdmin):
    inlines = (MintMarkInline,)

class IssueAdminForm(ModelForm):
    class Meta:
        model = Issue

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs and not kwargs['initial']:
            kwargs['initial'] = {
                'country': Country.objects.filter(iso='RUS')[0].id,
                'currency': Currency.objects.filter(iso='RUB')[0].id,
            }

        super(IssueAdminForm, self).__init__(*args, **kwargs)

class IssueAdmin(admin.ModelAdmin):
    list_display = ('series', 'name', 'show_nominal', 'year', 'coins_count')
    list_display_links = ('name',)
    search_fields = ['name']
    inlines = (CoinInline,)
    form = IssueAdminForm
    list_filter = ('year',)
    actions = (print_boxes_not_packed, print_boxes_all)

    fieldsets = (
        (_('Main information'), {
            'classes': ('wide',),
            'fields': (
                'name', 'type', 'nominal', 'currency', 'year', 'date_issue', 'country'
            )
        }),
        (_('Catalog information'), {
            'classes': ('wide',),
            'fields': ('catalog_number', 'series')
        }),
        (_('Physical parameters'), {
            'classes': ('wide',),
            'fields': ('diameter', 'thickness', 'weight', 'mintage')
        }),
        (_('Description'), {
            'classes': ('wide',),
            'fields': ('desc_obverse', 'desc_reverse', 'desc_edge')
        }),
    )

    def show_nominal(self, model):
        if model.currency.sign:
           return '%g %s' % (model.nominal, model.currency.sign)
        elif model.currency.iso:
           return '%g %s' % (model.nominal, model.currency.iso)

        return model.nominal
    show_nominal.short_description = _('Nominal')

    def get_urls(self):
        '''
        Добавляем URL на свой View в даминке, который в свою очередь подключается
        из фронта coins.views.barcode_view. Таким образом прозрачно заставляем
        работать одну вьюху и на фронт и на админку

        http://127.0.0.1:8000/admin/coins/coin/barcode/1.qr.png
        '''

        return super(IssueAdmin, self).get_urls() + patterns('',
            url(
                r'^barcode\/(\d+)[.](?:(qr|code128))[.]png$',
                barcode_view
            ),
        )


class CoinAdmin(admin.ModelAdmin):
    list_display = ('issue', 'mint', 'in_album', 'packaged')
    list_editable = ('in_album', 'packaged')

    formfield_overrides = {
        models.ImageField: {
            'widget': AdminImageFileWidget
        },
    }

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Mint, MintAdmin)
admin.site.register(Coin, CoinAdmin)

admin.site.register(MintMark)
admin.site.register(Series)