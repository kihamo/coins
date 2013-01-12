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

# -------- Override --------
class CoinAbstractModelAdmin(admin.ModelAdmin):
    save_on_top = True
    formfield_overrides = {
        models.ImageField: {
            'widget': AdminImageFileWidget
        },
    }

# -------- Inline --------
class CountryInline(admin.TabularInline):
    model = Country
    extra = 1
    readonly_fields = ('name', 'iso')

class MintMarkInline(admin.TabularInline):
    model = MintMark
    extra = 1

class IssueMintInline(admin.TabularInline):
    model = IssueMint
    extra = 1

class CoinInline(admin.StackedInline):
    model = Coin
    extra = 1
    readonly_fields = ('barcode','qr_code')

    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('barcode', 'qr_code', 'collection', 'mint', 'mint_mark', 'grade', 'in_album', 'packaged', 'booked')
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

# -------- General --------
class CollectionAdmin(CoinAbstractModelAdmin):
    list_display = ('name', 'coins_count')
    list_display_links = ('name',)

class CountryAdmin(CoinAbstractModelAdmin):
    list_display = ('iso', 'name', 'currency')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']

class CurrencyAdmin(CoinAbstractModelAdmin):
    list_display = ('iso', 'name')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']
    ordering = ['iso']
    inlines = (CountryInline,)

class MintAdmin(CoinAbstractModelAdmin):
    list_display = ('show_country', 'name')
    list_display_links = ('name',)
    inlines = (MintMarkInline,)

    def show_country(self, model):
        if model.country:
            return model.country.iso

        return ''
    show_country.short_description = _('Country')

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

class IssueAdmin(CoinAbstractModelAdmin):
    list_display = ('show_image_reverse', 'name', 'show_nominal', 'year', 'coins_count', 'coins_booked_count')
    list_display_links = ('name',)
    search_fields = ('name', 'catalog_number')
    inlines = (IssueMintInline, CoinInline)
    form = IssueAdminForm
    list_filter = ('type', 'year')
    actions = (print_boxes_not_packed, print_boxes_all)
    readonly_fields = ('catalog_number',)

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
            'fields': ('alloy', 'diameter', 'thickness', 'weight', 'mintage')
        }),
        (_('Description'), {
            'classes': ('wide',),
            'fields': ('desc', 'image_obverse', 'desc_obverse', 'image_reverse', 'desc_reverse', 'desc_edge')
        }),
    )

    def show_nominal(self, model):
        if model.currency.sign:
           return '%g %s' % (model.nominal, model.currency.sign)
        elif model.currency.iso:
           return '%g %s' % (model.nominal, model.currency.iso)

        return model.nominal
    show_nominal.short_description = _('Nominal')

    def show_image_reverse(self, model):
        if model.image_reverse:
            return '<img src="%s" alt="%s" />' % (model.image_reverse.get_url(100, 100), model)

        return ''
    show_image_reverse.allow_tags = True
    show_image_reverse.short_description = _('Reverse')

    def get_urls(self):
        """
        Добавляем URL на свой View в даминке, который в свою очередь подключается
        из фронта coins.views.barcode_view. Таким образом прозрачно заставляем
        работать одну вьюху и на фронт и на админку

        http://127.0.0.1:8000/admin/coins/coin/barcode/1.qr.png
        """

        return super(IssueAdmin, self).get_urls() + patterns('',
            url(
                r'^barcode\/(\d+)[.](?:(qr|code128))[.]png$',
                barcode_view
            ),
        )


class CoinAdmin(CoinAbstractModelAdmin):
    list_display = ('issue', 'show_mint', 'in_album', 'packaged', 'booked')
    list_editable = ('in_album', 'packaged', 'booked')
    list_filter = ('in_album', 'packaged', 'booked')
    search_fields = ('issue__name',)
    actions = (print_boxes_not_packed, print_boxes_all)

    formfield_overrides = {
        models.ImageField: {
            'widget': AdminImageFileWidget
        },
    }

    def show_mint(self, model):
        if model.mint_mark:
            return '%s (%s)' % (model.mint_mark.mark, model.mint_mark.mint)

        return model.mint
    show_mint.short_description = _('Mint')

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Mint, MintAdmin)
admin.site.register(Coin, CoinAdmin)

admin.site.register(MintMark)
admin.site.register(Series)