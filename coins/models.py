# django-tastypie REST Django
# http://www.falshivok.net/numismatics/Benin/35 coins params


from hashlib import md5

from django.db import models
from django.db.models.fields.files import ImageFieldFile

from django.utils.translation import ugettext_lazy as _

# -------- Service models --------
class CoinAbstract(models.Model):
    class Meta:
        abstract = True

    def __unicode__(self):
        if hasattr(self, 'name'):
            return self.name

        return '%s object' % self.__class__.__name__

class Image(CoinAbstract):
    filename = models.CharField(max_length=256)

    data = models.TextField()
    size = models.PositiveIntegerField(
        editable=False
    )

    #mimetype = models.CharField(
    #    null=True,
    #    blank=True,
    #    editable=False,
    #    max_length=50
    #)
    #hash = models.CharField(editable=False,max_length=32)

    def resize(self, width=None, height=None):
        pass

class CoinImageFieldFile(ImageFieldFile):

    def save(self, name, content, save=True):
        position = content.tell()
        content.seek(0)

        name = md5(content.read()).hexdigest()

        content.seek(position)

        super(CoinImageFieldFile, self).save(name, content, save)

class CoinImageField(models.ImageField):
    attr_class = CoinImageFieldFile

    def __init__(self, *args, **kwargs):
        from coins.utils.storage import DatabaseStorage

        kwargs['upload_to'] = 'coins'
        kwargs['blank'] = True
        kwargs['null'] = True
        kwargs['storage'] = DatabaseStorage()

        super(CoinImageField, self).__init__(*args, **kwargs)

    def generate_filename(self, instance, name):
        return name

# -------- Models --------

# http://www.currency-iso.org/isocy/global/en/home/tables/table-a1.html
# http://www.currency-iso.org/dam/isocy/downloads/dl_iso_table_a1.xls
# http://www.currency-iso.org/dam/isocy/downloads/dl_iso_table_a1.xml
class Currency(CoinAbstract):
    iso = models.CharField(
        _('ISO code'),
        help_text=_('Currency ISO 3 code'),
        max_length=3,
        blank=True,
        null=True
    )
    name = models.CharField(
        _('Name'),
        help_text=_('Currency name'),
        max_length=100
    )
    sign = models.CharField(
        _('Sign'),
        help_text=_('Currency sign'),
        max_length=10,
        blank=True,
        null=True
    )

    class Meta(CoinAbstract.Meta):
        ordering = ['name']
        verbose_name = _('currency')
        verbose_name_plural = _('currencies')

class Country(CoinAbstract):
    iso = models.CharField(
        _('ISO code'),
        help_text=_('Country ISO 3 code'),
        max_length=3,
        blank=True,
        null=True
    )
    name = models.CharField(
        _('Name'),
        help_text=_('Country name'),
        max_length=100
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name=_('Current currency'),
        blank=True,
        null=True
    )

    class Meta(CoinAbstract.Meta):
        ordering = ['iso']
        verbose_name = _('country')
        verbose_name_plural = _('countries')

class Collection(CoinAbstract):
    name = models.CharField(
        _('Name'),
        max_length=100,
        help_text=_('Collection name')
    )

    class Meta(CoinAbstract.Meta):
        verbose_name = _('collection')
        verbose_name_plural = _('collections')

    def coins_count(self):
        return self.coin_set.count()
    coins_count.short_description = _('Coins count')

class Mint(CoinAbstract):
    name = models.CharField(
        _('Name'),
        help_text=_('Mint name'),
        max_length=100
    )

    class Meta(CoinAbstract.Meta):
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
        verbose_name = _('mark mint')
        verbose_name_plural = _('marks mints')

    def __unicode__(self):
        return self.mark

class Series(CoinAbstract):
    name = models.CharField(
        _('Name'),
        help_text=_('Series name'),
        max_length=100
    )

    class Meta(CoinAbstract.Meta):
        verbose_name = _('series')
        verbose_name_plural = _('series')

class Issue(CoinAbstract):
    TYPES_CHOICES = (
        (1, _('Commemorative')),
        (2, _('Regular')),
    )

    name = models.CharField(
        _('Name'),
        max_length=100,
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
        max_digits=5,
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
        null=True
    )
    diameter = models.IntegerField(
        _('Diameter'),
        help_text=_('Diameter in millimeters'),
        blank=True,
        null=True
    )
    thickness = models.FloatField(
        _('Thickness'),
        help_text=_('Thickness in millimeters'),
        blank=True,
        null=True
    )
    weight = models.IntegerField(
        _('Weight'),
        help_text=_('Weight in grams'),
        blank=True,
        null=True
    )
    mintage = models.IntegerField(
        _('Mintage'),
        help_text=_('Mintage in pieces'),
        blank=True,
        null=True
    )
    desc_obverse = models.TextField(
        _('Obverse'),
        help_text=_('Obverse description'),
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
        verbose_name = _('issue')
        verbose_name_plural = _('issues')

    def coins_count(self):
        return self.coin_set.count()
    coins_count.short_description = _('Coins count')

class Coin(CoinAbstract):
    issue = models.ForeignKey(
        Issue,
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
        _('Obverse')
    )
    image_reverse = CoinImageField(
        _('Reverse')
    )
    in_album = models.BooleanField(
        _('In albums'),
        help_text=_('Exists in albums')
    )
    packaged = models.BooleanField(
        _('Packaged'),
        help_text=_('Labeled and packaged')
    )
    features = models.TextField(
        _('Features'),
        blank=True,
        null=True
    )

    class Meta(CoinAbstract.Meta):
        verbose_name = _('coin')
        verbose_name_plural = _('coins')

    def get_absolute_url(self):
        return "/coin/%i/" % self.id

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