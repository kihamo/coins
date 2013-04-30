# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse

from django.contrib import admin
from django.forms import ModelForm

from utils.widgets import AdminImageFileWidget
from views import barcode as barcode_view
from models import *

from constance import config

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
class MintMarkInline(admin.TabularInline):
    model = MintMark
    extra = 1

class IssueMintInline(admin.TabularInline):
    model = IssueMint
    extra = 1

class CurrencyHistoryInline(admin.TabularInline):
    model = CurrencyHistory
    extra = 1

class CopyInline(admin.StackedInline):
    extra = 1
    readonly_fields = ('barcode','qr_code')

    def _show_barcode_image(self, model, type):
        if not model.id or not model.issue:
            return ''

        url = reverse(barcode_view, args=[model.id, type])
        return '<img src="%s" alt="%s"/>' % (url, ugettext('Barcode'))

    def barcode(self, coin):
        return self._show_barcode_image(coin, 'code128')
    barcode.allow_tags = True

    def qr_code(self, coin):
        return self._show_barcode_image(coin, 'qr')
    qr_code.allow_tags = True

class CoinInline(CopyInline):
    model = Coin
    fields = (
        ('barcode', 'qr_code'),
        'collection', 'grade',
        ('mint', 'mint_mark'),
        ('in_album', 'packaged', 'booked'),
        ('image_obverse', 'image_reverse'),
        'features'
    )

class BanknoteInline(CopyInline):
    model = Banknote
    fields = (
        ('barcode', 'qr_code'),
        'collection', 'grade',
        ('in_album', 'packaged', 'booked'),
        ('image_obverse', 'image_reverse'),
        'features'
    )

# -------- General --------
class CollectionAdmin(CoinAbstractModelAdmin):
    list_display = ('name', 'coins_count', 'banknotes_count')
    list_display_links = ('name',)

class MintAdmin(CoinAbstractModelAdmin):
    list_display = ('show_country', 'name')
    list_display_links = ('name',)
    inlines = (MintMarkInline,)

    def show_country(self, model):
        if model.country:
            return model.country.iso

        return ''
    show_country.short_description = _('Country')

class CountryAdmin(CoinAbstractModelAdmin):
    list_display = ('iso', 'name', 'current_currency')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']
    inlines = (CurrencyHistoryInline,)

class CurrencyAdmin(CoinAbstractModelAdmin):
    list_display = ('iso', 'name')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']
    ordering = ['iso']
    exclude = ('countries',)
    inlines = (CurrencyHistoryInline,)

class CopyIssueAdminForm(ModelForm):
    class Meta:
        model = CoinIssue

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs and not kwargs['initial']:
            kwargs['initial'] = {}

            countries = Country.objects.filter(iso=config.DEFAULT_ISSUE_COUNTRY.upper())
            if countries:
                kwargs['initial']['country'] = countries[0].id

            currencies = Currency.objects.filter(iso=config.DEFAULT_ISSUE_CURRENCY.upper())
            if currencies:
                kwargs['initial']['currency'] = currencies[0].id

        super(CopyIssueAdminForm, self).__init__(*args, **kwargs)

class CopyIssueAdminAbstract(CoinAbstractModelAdmin):
    list_display = ('show_image_reverse', 'name', 'show_nominal', 'year', 'copy_count', 'copy_booked_count')
    list_display_links = ('name',)
    list_filter = ('type', 'year')
    search_fields = ('name', 'catalog_number')
    readonly_fields = ('catalog_number',)

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

        return super(CopyIssueAdminAbstract, self).get_urls() + patterns('',
            url(
                r'^barcode\/(\d+)[.](?:(qr|code128))[.]png$',
                barcode_view
            ),
        )

class CoinIssueAdminForm(CopyIssueAdminForm):
    class Meta:
        model = CoinIssue

class CoinIssueAdmin(CopyIssueAdminAbstract):
    form = CoinIssueAdminForm
    inlines = (IssueMintInline, CoinInline)
    actions = (print_boxes_not_packed, print_boxes_all)
    fieldsets = (
        (_('Main information'), {
            'classes': ('wide',),
            'fields': (
                'name',
                ('nominal', 'type'),
                ('country', 'currency'),
                ('year', 'date_issue'),
                ('series', 'catalog_number')
            )
        }),
        (_('Physical parameters'), {
            'classes': ('wide',),
            'fields': (
                ('diameter', 'weight', 'thickness'),
                'desc_edge', 'alloy'
            )
        }),
        (_('Description'), {
            'classes': ('wide',),
            'fields': (
                ('image_obverse', 'image_reverse'),
                'desc', 'desc_obverse', 'desc_reverse'
            )
        })
    )

class BanknoteIssueAdminForm(CopyIssueAdminForm):
    class Meta:
        model = BanknoteIssue

class BanknoteIssueAdmin(CopyIssueAdminAbstract):
    form = BanknoteIssueAdminForm
    inlines = (BanknoteInline,)
    fieldsets = (
        (_('Main information'), {
            'classes': ('wide',),
            'fields': (
                'name',
                ('nominal', 'type'),
                ('country', 'currency'),
                ('year', 'date_issue'),
                ('series', 'catalog_number')
            )
        }),
        (_('Physical parameters'), {
            'classes': ('wide',),
            'fields': (
                ('height', 'weight'),
            )
        }),
        (_('Description'), {
            'classes': ('wide',),
            'fields': (
                ('image_obverse', 'image_reverse'),
                'desc', 'desc_obverse', 'desc_reverse'
            )
        })
    )

class CopyAdminAbstract(CoinAbstractModelAdmin):
    list_display = ('issue', 'in_album', 'packaged', 'booked')
    list_editable = ('in_album', 'packaged', 'booked')
    list_filter = ('in_album', 'packaged', 'booked')
    search_fields = ('issue__name',)

class CoinAdmin(CopyAdminAbstract):
    actions = (print_boxes_not_packed, print_boxes_all)
    fields = (
        'collection', 'grade',
        ('mint', 'mint_mark'),
        ('in_album', 'packaged', 'booked'),
        ('image_obverse', 'image_reverse'),
        'features'
    )

    def __init__(self, *args, **kwargs):
        super(CoinAdmin, self).__init__(*args, **kwargs)
        self.list_display += ('show_mint',)

    def show_mint(self, model):
        if model.mint_mark:
            return '%s (%s)' % (model.mint_mark.mark, model.mint_mark.mint)

        return model.mint
    show_mint.short_description = _('Mint')

class BanknoteAdmin(CopyAdminAbstract):
    fields = (
        'collection', 'grade',
        ('in_album', 'packaged', 'booked'),
        ('image_obverse', 'image_reverse'),
        'features'
    )

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Mint, MintAdmin)

admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)

admin.site.register(CoinIssue, CoinIssueAdmin)
admin.site.register(BanknoteIssue, BanknoteIssueAdmin)

admin.site.register(Coin, CoinAdmin)
admin.site.register(Banknote, BanknoteAdmin)

admin.site.register(MintMark)
admin.site.register(Series)