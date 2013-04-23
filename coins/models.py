# django-tastypie REST Django
# http://www.falshivok.net/numismatics/Benin/35 coins params

from django.db import models
from django.utils.translation import ugettext_lazy as _

from coins.utils.models import CoinImageField

class CoinAbstract(models.Model):
    class Meta:
        abstract = True

    def __unicode__(self):
        if hasattr(self, 'name'):
            return self.name

        return '%s object' % self.__class__.__name__

class Image(CoinAbstract):
    hash = models.CharField(
        editable = False,
        max_length = 32,
        primary_key = True,
        unique = True
    )
    filename = models.CharField(
        max_length=256
    )
    data = models.TextField(
        editable=False
    )
    size = models.PositiveIntegerField(
        editable=False
    )
    mime_type = models.CharField(
        null=True,
        blank=True,
        editable=False,
        max_length=50
    )

# country & currency
class IsoAbstract(CoinAbstract):
    iso = models.CharField(
        _('ISO code'),
        max_length=3,
        blank=True,
        null=True
    )
    name = models.CharField(
        _('Name'),
        max_length=100
    )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        self.iso = self.iso.upper()
        super(IsoAbstract, self).save(**kwargs)

class Country(IsoAbstract):
    current_currency = models.ForeignKey(
        'coins.Currency',
        related_name='current_currency',
        verbose_name=_('Current currency'),
        blank=True,
        null=True
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_countries'
        ordering = ['iso']
        verbose_name = _('country')
        verbose_name_plural = _('countries')

    def __init__(self, *args, **kwargs):
        IsoAbstract.__init__(self, *args, **kwargs)
        self._meta.get_field_by_name('iso')[0].help_text = _('Country ISO 3 code')
        self._meta.get_field_by_name('name')[0].help_text = _('Country name')

class Currency(IsoAbstract):
    sign = models.CharField(
        _('Sign'),
        help_text=_('Currency sign'),
        max_length=10,
        blank=True,
        null=True
    )
    countries = models.ManyToManyField(
        Country,
        through='CurrencyHistory',
        verbose_name=_('Country'),
        null=True,
        blank=True
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_currencies'
        ordering = ['name']
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')

    def __init__(self, *args, **kwargs):
        IsoAbstract.__init__(self, *args, **kwargs)
        self._meta.get_field_by_name('iso')[0].help_text = _('Currency ISO 3 code')
        self._meta.get_field_by_name('name')[0].help_text = _('Currency name')

    def __unicode__(self):
        if self.sign and len(self.sign):
            return '%s (%s)' % (self.name, self.sign)

        return self.name

class CurrencyHistory(CoinAbstract):
    country = models.ForeignKey(
        Country,
        verbose_name=_('Country')
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_('Currency')
    )
    date_from = models.DateField(
        _('Date from'),
        help_text=_('Date from'),
        blank=True,
        null=True
    )
    date_to = models.DateField(
        _('Date to'),
        help_text=_('Date to'),
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'coins_currencies_history'
        auto_created = Currency
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')

class Collection(CoinAbstract):
    name = models.CharField(
        _('Name'),
        max_length=100,
        help_text=_('Collection name')
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_collections'
        verbose_name = _('collection')
        verbose_name_plural = _('collections')

    def coins_count(self):
        return self.coin_set.count()
    coins_count.short_description = _('Coins count')

# coin
class Mint(CoinAbstract):
    name = models.CharField(
        _('Name'),
        help_text=_('Mint name'),
        max_length=100
    )
    country = models.ForeignKey(
        Country,
        verbose_name=_('Country')
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_mints'
        verbose_name = _('mint')
        verbose_name_plural = _('mints')

class MintMark(CoinAbstract):
    mark = models.CharField(
        _('Mark'),
        help_text=_('Mint mark'),
        max_length=50
    )
    mint = models.ForeignKey(
        Mint,
        verbose_name=_('Mint')
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_mint_marks'
        verbose_name = _('mark mint')
        verbose_name_plural = _('marks mints')

    def save(self, **kwargs):
        self.mark = self.mark.upper()
        super(MintMark, self).save(**kwargs)

    def __unicode__(self):
        return self.mark

class Series(CoinAbstract):
    name = models.CharField(
        _('Name'),
        help_text=_('Series name'),
        max_length=200
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_series'
        verbose_name = _('series')
        verbose_name_plural = _('series')

class CoinIssue(CoinAbstract):
    TYPES_CHOICES = (
        (1, _('Commemorative')),
        (2, _('Regular')),
    )

    name = models.CharField(
        _('Name'),
        max_length=200,
        help_text=_('Issue name')
    )
    type = models.PositiveSmallIntegerField(
        _('Type'),
        help_text=_('Type coin'),
        max_length=1,
        choices=TYPES_CHOICES,
        default=1
    )
    nominal = models.DecimalField(
        _('Nominal'),
        max_digits=10,
        decimal_places=2
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_('Currency')
    )
    year = models.IntegerField(
        _('Year'),
        help_text=_('Year of issue')
    )
    date_issue = models.DateField(
        _('Date'),
        help_text=_('Date of issue'),
        blank=True,
        null=True
    )
    country = models.ForeignKey(
        Country,
        verbose_name=_('Country'),
        blank=True,
        null=True
    )
    mint = models.ManyToManyField(
        Mint,
        through='IssueMint',
        verbose_name=_('Mint'),
        null=True,
        blank=True
    )
    series = models.ForeignKey(
        Series,
        verbose_name=_('Series'),
        blank=True,
        null=True
    )
    catalog_number = models.CharField(
        _('Catalog number'),
        max_length=100,
        blank=True,
        null=True,
        editable=False
    )
    diameter = models.DecimalField(
        _('Diameter'),
        help_text=_('Diameter in millimeters'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    alloy = models.CharField(
        _('Alloy'),
        max_length=200,
        blank=True,
        null=True
    )
    thickness = models.DecimalField(
        _('Thickness'),
        help_text=_('Thickness in millimeters'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight = models.DecimalField(
        _('Weight'),
        help_text=_('Weight in grams'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    mintage = models.IntegerField(
        _('Total mintage'),
        help_text=_('Total mintage in pieces'),
        blank=True,
        null=True
    )
    desc = models.TextField(
        _('Description'),
        help_text=_('Coin description'),
        blank=True,
        null=True
    )
    image_obverse = CoinImageField(
        _('Obverse'),
        blank=True,
        null=True
    )
    desc_obverse = models.TextField(
        _('Obverse'),
        help_text=_('Obverse description'),
        blank=True,
        null=True
    )
    image_reverse = CoinImageField(
        _('Reverse'),
        blank=True,
        null=True
    )
    desc_reverse = models.TextField(
        _('Reverse'),
        help_text=_('Reverse description'),
        blank=True,
        null=True
    )
    desc_edge = models.TextField(
        _('Edge'),
        help_text=_('Edge description'),
        blank=True,
        null=True
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_coin_issues'
        verbose_name = _('issue')
        verbose_name_plural = _('issues')

    def coins_count(self):
        return self.coin_set.count()
    coins_count.short_description = _('Coins count')

    def coins_booked_count(self):
        return self.coin_set.filter(booked=True).count()
    coins_booked_count.short_description = _('Booked coins count')

class IssueMint(CoinAbstract):
    issue = models.ForeignKey(
        CoinIssue,
        verbose_name=_('Issue')
    )
    mint = models.ForeignKey(
        Mint,
        verbose_name=_('Mint')
    )
    mint_mark = models.ForeignKey(
        MintMark,
        verbose_name=_('Mint mark'),
        blank=True,
        null=True
    )
    mintage = models.IntegerField(
        _('Mintage'),
        help_text=_('Mintage in pieces'),
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'coins_issue_mints'
        auto_created = CoinIssue
        verbose_name = _('mint')
        verbose_name_plural = _('mints')

class Coin(CoinAbstract):
    issue = models.ForeignKey(
        CoinIssue,
        verbose_name=_('Issue')
    )
    mint = models.ForeignKey(
        Mint,
        verbose_name=_('Mint'),
        blank=True,
        null=True
    )
    mint_mark = models.ForeignKey(
        MintMark,
        verbose_name=_('Mint mark'),
        blank=True,
        null=True
    )
    collection = models.ForeignKey(
        Collection,
        verbose_name=_('Collection')
    )
    grade = models.PositiveSmallIntegerField(
        _('Grade'),
        help_text=_('Grade value between 1 and 70'),
        blank=True,
        null=True
    )
    image_obverse = CoinImageField(
        _('Obverse'),
        blank=True,
        null=True
    )
    image_reverse = CoinImageField(
        _('Reverse'),
        blank=True,
        null=True
    )
    in_album = models.BooleanField(
        _('In albums'),
        help_text=_('Exists in albums')
    )
    packaged = models.BooleanField(
        _('Packaged'),
        help_text=_('Labeled and packaged')
    )
    booked = models.BooleanField(
        _('Booked'),
        help_text=_('Coin is booked')
    )
    features = models.TextField(
        _('Features'),
        blank=True,
        null=True
    )

    class Meta(CoinAbstract.Meta):
        db_table = 'coins_coins'
        verbose_name = _('coin')
        verbose_name_plural = _('coins')

    def get_absolute_url(self):
        return "/coin/%s/" % self.barcode

    @property
    def barcode(self):
        if not self.id:
            return ''

        issue = self.issue

        return '%s-%d-%06d' % (
            issue.currency.iso,
            issue.year,
            self.id
        )

    @property
    def qr_code(self):
        if not self.id:
            return ''

        issue = self.issue

        country_iso = ''
        if issue.country:
            country_iso = issue.country.iso

        return 'Nominal: %g %s Year: %d Country: %s Url: %s' % (
            issue.nominal,
            issue.currency.iso,
            issue.year,
            country_iso,
            self.get_absolute_url()
        )

    def __unicode__(self):
        return self.issue.name

    def save(self, *args, **kwargs):
        if self.in_album and not self.packaged:
            self.packaged = True

        super(Coin, self).save(*args, **kwargs)