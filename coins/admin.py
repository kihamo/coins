# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _, ugettext

from django.core.urlresolvers import reverse
from django.db.models.query import EmptyQuerySet

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from django.contrib import admin
from django.forms import ModelForm

from utils.widgets import AdminImageFileWidget
from models import *

from constance import config

# -------- Actions --------


# TODO:
def print_boxes_not_packed(modeladmin, request, queryset):
    pass
print_boxes_not_packed.short_description = \
    _('Print coin boxes only not packed coins')


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
    readonly_fields = ('barcode', 'qr_code')

    def _show_barcode_image(self, model, type):
        if not model.id or not model.issue:
            return ''

        url = reverse('barcode', args=[
            model.__class__.__name__.lower(),
            model.id,
            type
        ])
        return '<img src="%s" alt="%s"/>' % (url, ugettext('Barcode'))

    def barcode(self, model):
        return self._show_barcode_image(model, 'code128')
    barcode.allow_tags = True

    def qr_code(self, model):
        return self._show_barcode_image(model, 'qr')
    qr_code.allow_tags = True


class CoinInline(CopyInline):
    model = Coin
    fields = (
        ('barcode', 'qr_code'),
        'collection', 'mint', 'grade',
        ('packaged', 'booked'),
        ('album', 'page', 'division'),
        ('image_obverse', 'image_reverse'),
        'features'
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(CoinInline, self).get_formset(request, obj, **kwargs)
        mint_field = formset.form.base_fields['mint']

        if obj:
            mint_field.queryset = IssueMint.objects.filter(issue=obj)

            if mint_field.queryset.count():
                mint_field.initial = mint_field.queryset[0].id
        else:
            mint_field.queryset = EmptyQuerySet()

        return formset


class BanknoteInline(CopyInline):
    model = Banknote
    fields = (
        ('barcode', 'qr_code'),
        'collection', 'grade',
        ('packaged', 'booked'),
        ('album', 'page', 'division'),
        ('image_obverse', 'image_reverse'),
        'features'
    )


# -------- General --------
class CollectionAdmin(CoinAbstractModelAdmin):
    list_display = ('name', 'coins_count_link', 'banknotes_count_link')
    list_display_links = ('name',)

    def coins_count_link(self, model):
        url = reverse('admin:coins_coin_changelist')
        return '<a href="%s?collection=%s">%s</a>'\
               % (url, model.id, model.coins_count())
    coins_count_link.allow_tags = True
    coins_count_link.short_description = _('Coins count')

    def banknotes_count_link(self, model):
        url = reverse('admin:coins_banknote_changelist')
        return '<a href="%s?collection=%s">%s</a>'\
               % (url, model.id, model.banknotes_count())
    banknotes_count_link.allow_tags = True
    banknotes_count_link.short_description = _('Banknotes count')


class MintAdmin(CoinAbstractModelAdmin):
    list_display = ('show_country', 'name')
    list_display_links = ('name',)
    inlines = (MintMarkInline,)

    def show_country(self, model):
        if model.country:
            return model.country.iso

        return ''
    show_country.short_description = _('Country')


class MintMarkAdmin(CoinAbstractModelAdmin):
    list_display = ('mark', 'mint')
    list_display_links = ('mark',)


class CountryAdmin(CoinAbstractModelAdmin):
    list_display = ('iso', 'name', 'current_currency')
    list_display_links = ('name',)
    search_fields = ['iso', 'name']
    inlines = (CurrencyHistoryInline,)


class CurrencyAdmin(CoinAbstractModelAdmin):
    list_display = ('iso', 'name', 'sign')
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

            countries = Country.objects.filter(
                iso=config.DEFAULT_ISSUE_COUNTRY.upper())
            if countries:
                kwargs['initial']['country'] = countries[0].id

            currencies = Currency.objects.filter(
                iso=config.DEFAULT_ISSUE_CURRENCY.upper())
            if currencies:
                kwargs['initial']['currency'] = currencies[0].id

        super(CopyIssueAdminForm, self).__init__(*args, **kwargs)


class CopyIssueAdminAbstract(CoinAbstractModelAdmin):
    list_display = ('show_image', 'name', 'show_nominal',
                    'year', 'copy_count', 'copy_booked_count')
    list_display_links = ('name',)
    list_filter = ('type', 'year')
    search_fields = ('name', 'catalog_number')
    readonly_fields = ('show_catalog_number',)

    def show_nominal(self, model):
        if model.currency.sign:
            return '%g %s' % (model.nominal, model.currency.sign)
        elif model.currency.iso:
            return '%g %s' % (model.nominal, model.currency.iso)

        return model.nominal
    show_nominal.short_description = _('Nominal')

    def show_image(self, model):
        image = model.image_reverse or model.image_obverse
        if image:
            return '<img src="%s" alt="%s" />'\
                   % (image.get_url(100, 100), model)

        return ''
    show_image.allow_tags = True
    show_image.short_description = _('Image')

    def show_catalog_number(self, model):
        if (model.catalog_number and model.currency and
           model.currency.iso == 'RUB'):
            return '<a href="http://cbr.ru/bank-notes_coins/' \
                   'Base_of_memorable_coins/ShowCoins.aspx' \
                   '?cat_num=%s" target="_blank" />%s</a>'\
                   % (model.catalog_number, model.catalog_number)

        return model.catalog_number
    show_catalog_number.allow_tags = True
    show_catalog_number.short_description = _('Catalog number')


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
                ('series', 'show_catalog_number'),
                ('mintage')
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
                ('desc_obverse', 'desc_reverse'),
                'desc',
                ('painter', 'sculptor')
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
                ('series', 'show_catalog_number'),
                ('mintage')
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
    list_display = (
        'show_image', 'issue', 'nominal', 'year', 'packaged', 'booked',
        'in_album', 'album', 'page', 'division'
    )
    list_display_links = ('issue',)
    list_editable = ('packaged', 'booked', 'album', 'page', 'division')
    list_filter = ('packaged', 'booked', 'album')
    search_fields = ('issue__name',)

    def show_image(self, model):
        image = (model.image_reverse or model.image_obverse
                 or model.issue.image_reverse or model.issue.image_obverse)
        if image:
            return '<img src="%s" alt="%s" />'\
                   % (image.get_url(100, 100), model)

        return ''
    show_image.allow_tags = True
    show_image.short_description = _('Image')

    def nominal(self, model):
        model = model.issue
        if model.currency.sign:
            return '%g %s' % (model.nominal, model.currency.sign)
        elif model.currency.iso:
            return '%g %s' % (model.nominal, model.currency.iso)

        return model.nominal
    nominal.short_description = _('Nominal')

    def year(self, model):
        return model.issue.year
    year.short_description = _('Year')


class CoinAdmin(CopyAdminAbstract):
    actions = (print_boxes_not_packed, print_boxes_all)
    fields = (
        'collection', 'grade', 'mint',
        ('packaged', 'booked'),
        ('album', 'page', 'division'),
        ('image_obverse', 'image_reverse'),
        'features'
    )


class BanknoteAdmin(CopyAdminAbstract):
    fields = (
        'collection', 'grade',
        ('packaged', 'booked'),
        ('image_obverse', 'image_reverse'),
        'features'
    )


class DeviceTokenInline(admin.TabularInline):
    model = DeviceToken
    extra = 0
    max_num = 0
    readonly_fields = ('token', )
    verbose_name = _('Device token')
    verbose_name_plural = _('Device tokens')


class UserAdmin(UserAdmin):
    class Media:
        css = {
            "all": ("admin/css/coins.css",)
        }

    inlines = (DeviceTokenInline,)


admin.site.register(CoinIssue, CoinIssueAdmin)
admin.site.register(Coin, CoinAdmin)
admin.site.register(Mint, MintAdmin)
admin.site.register(MintMark, MintMarkAdmin)

admin.site.register(BanknoteIssue, BanknoteIssueAdmin)
admin.site.register(Banknote, BanknoteAdmin)

admin.site.register(Country, CountryAdmin)
admin.site.register(Currency, CurrencyAdmin)

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Series)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
