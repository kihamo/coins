# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

import re

from urllib import urlencode
import urllib2

from coins.models import Country, Currency, CurrencyHistory
from datetime import datetime

from lxml.etree import parse, HTMLParser

# www.globalfinancialdata.com/news/GHC_Histories.xls
# manage.py dumpdata --format=json coins.Country coins.Currency coins.CurrencyHistory > coins/fixtures/country_currency.json

class Command(BaseCommand):
    help = 'Import countries and currency'

    _base_url = 'http://www.unicode.org/repos/cldr/trunk/common'
    _ignore_regions = ['XX', '150']

    def __init__(self):
        super(Command, self).__init__()

        opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=0))
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1490.2 Safari/537.36')
        ]
        urllib2.install_opener(opener)

    def _load_url(self, url, data=None):
        self.stdout.write(self.style.HTTP_INFO('Load page %s' % url))

        try:
            if data:
                data = urlencode(data)

            content = urllib2.urlopen(url, data)
        except Exception as e:
            raise CommandError('Error "%s" load page %s' % (e, url))

        root = parse(content, HTMLParser(encoding='utf-8'))
        if not root:
            raise CommandError('Error parse page %s' % url)

        return root.getroot()

    def handle(self, year = None, *args, **options):
        doc_main = self._load_url('%s/main/ru.xml' % self._base_url)

        # currency
        entities = doc_main.xpath('.//ldml/numbers/currencies/currency')
        for entity in entities:
            currency, created = Currency.objects.get_or_create(
                name = re.sub('\(.*\)', '', entity.xpath('.//displayname/text()')[0]).strip(),
                iso = entity.attrib['type']
            )

            if created:
                self.stdout.write('Add currency "%s" (%s)' % (currency.name, currency.iso))

        # currency symbols
        doc_symbols = self._load_url('http://www.xe.com/symbols.php')
        entities = doc_symbols.xpath('.//table[@class="cSymbl_tbl"]/tr[@class="row1" or @class="row2"]')
        for entity in entities:
            sign = entity.xpath('.//td[@class="cSmbl_Fnt_C2000"]/text()')
            if sign:
                iso = entity.xpath('.//td[2]/text()')[0]
                try:
                    object = Currency.objects.get(iso = iso)
                    sign = sign[0]

                    if not object.sign:
                        object.sign = sign
                        object.save()
                        self.stdout.write('Set sign for currency "%s"' % object.iso)
                except Currency.DoesNotExist:
                    self.stderr.write('Currency %s not found' % iso)

        # country
        doc_data = self._load_url('%s/supplemental/supplementalData.xml' % self._base_url)
        entities = doc_main.xpath('.//ldml/localedisplaynames/territories/territory[not(@alt)]')
        for entity in entities:
            iso = entity.attrib['type']

            if iso in self._ignore_regions:
                self.stdout.write('Ignore country "%s"' % iso)
            elif len(iso) == 2:
                country_entity = doc_data.xpath('.//supplementaldata/codemappings/territorycodes[@type="%s"][@alpha3]' % iso)

                if country_entity:
                    country, created = Country.objects.get_or_create(
                        name = re.sub('\(.*\)', '', entity.text).strip(),
                        iso = country_entity[0].attrib['alpha3']
                    )

                    if created:
                        self.stdout.write('Add country "%s" (%s)' % (country.name, country.iso))
                else:
                    self.stderr.write('Not found country by iso 2 "%s"' % iso)

        # relations
        entities = doc_data.xpath('.//supplementaldata/currencydata/region')

        for entity in entities:
            iso = entity.attrib['iso3166']

            if iso in self._ignore_regions:
                self.stderr.write('Ignore currency country "%s"' % iso)
            else:
                country_entity = doc_data.xpath('.//supplementaldata/codemappings/territorycodes[@type="%s"][@alpha3]' % entity.attrib['iso3166'])

                if country_entity:
                    currency_entities = entity.xpath('.//currency[not(@tender="false")]')

                    try:
                        country_iso = country_entity[0].attrib['alpha3']
                        country = Country.objects.get(iso = country_iso)
                    except:
                        self.stderr.write('Not found country by iso "%s"' % country_iso)
                    else:
                        for currency_entity in currency_entities:
                            currency_iso = currency_entity.attrib['iso4217']

                            try:
                                currency = Currency.objects.get(iso = currency_iso)
                            except:
                                self.stderr.write('Not found currency by iso "%s"' % currency_iso)
                            else:
                                # current currency
                                if not 'to' in currency_entity.attrib and 'from' in currency_entity.attrib and (not country.current_currency or not country.current_currency.iso == currency.iso):
                                    if country.current_currency:
                                        self.stderr.write(
                                            'Double current currency "%s" [%s] for country "%s" [%s]' %
                                            (currency.name, currency.iso, country.name, country.iso)
                                        )
                                    else:
                                        country.current_currency = currency
                                        country.save()

                                        self.stdout.write(
                                            'Import current country "%s" [%s] currency "%s" [%s]' %
                                            (country.name, country.iso, currency.name, currency.iso)
                                        )

                                # currency history
                                if not currency.countries.filter(id=country.id).exists():
                                    history = CurrencyHistory(country = country, currency = currency)

                                    if 'to' in currency_entity.attrib:
                                        history.date_to = datetime.strptime(currency_entity.attrib['to'], '%Y-%m-%d')

                                    if 'from' in currency_entity.attrib:
                                        history.date_from = datetime.strptime(currency_entity.attrib['from'], '%Y-%m-%d')

                                    history.save()

                                    self.stdout.write(
                                        'Import history currency "%s" [%s] country "%s" [%s]' %
                                        (currency.name, currency.iso, country.name, country.iso)
                                    )
                            currency.save()
                else:
                    self.stderr.write('Not found region country by iso 2 "%s"' % entity.attrib['iso3166'])