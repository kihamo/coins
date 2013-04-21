# -*- coding: utf-8 -*-

from django.core.management import base
from django.utils.termcolors import make_style
from coins.models import Country, Currency, CurrencyHistory
from lxml.html import parse
import dateutil.parser

import re

# www.globalfinancialdata.com/news/GHC_Histories.xls
# manage.py dumpdata --format=json coins.Country coins.Currency coins.CurrencyHistory > coins/fixtures/country_currency.json

class Command(base.BaseCommand):
    help = 'Import countries and currency'

    _base_url = 'http://www.unicode.org/repos/cldr/trunk/common'
    _ignore_regions = ['XX', '150']

    def __init__(self):
        super(Command, self).__init__()
        self.style.IMPORT_VALUE = make_style(fg='cyan', opts=('bold',))

    def handle(self, year = None, *args, **options):
        doc_main = parse('%s/main/ru.xml' % self._base_url)
        doc_data = parse('%s/supplemental/supplementalData.xml' % self._base_url)

        # currency
        entities = doc_main.xpath('.//ldml/numbers/currencies/currency')
        for entity in entities:
            iso = entity.attrib['type']
            name = re.sub('\(.*\)', '', entity.xpath('.//displayname/text()')[0]).strip()

            if self._save_model(Currency, iso, name):
                self._print_message('Import currency "%s" [%s]', (name, iso))

        # country
        entities = doc_main.xpath('.//ldml/localedisplaynames/territories/territory[not(@alt)]')
        for entity in entities:
            iso = entity.attrib['type']

            if iso in self._ignore_regions:
                self._print_message('Ignore country "%s"', (iso,), 'error')
            elif len(iso) == 2:
                country_entity = doc_data.xpath('.//supplementaldata/codemappings/territorycodes[@type="%s"][@alpha3]' % iso)

                if country_entity:
                    country_iso = country_entity[0].attrib['alpha3']
                    name = re.sub('\(.*\)', '', entity.text).strip()

                    if self._save_model(Country, country_iso, name):
                        self._print_message('Import country "%s" [%s]', (name, country_iso))
                else:
                    self._print_message('Not found country by iso 2 "%s"', (iso,), 'error')

        # relations
        entities = doc_data.xpath('.//supplementaldata/currencydata/region')

        for entity in entities:
            iso = entity.attrib['iso3166']

            if iso in self._ignore_regions:
                self._print_message('Ignore currency country "%s"', (iso,), 'error')
            else:
                country_entity = doc_data.xpath('.//supplementaldata/codemappings/territorycodes[@type="%s"][@alpha3]' % entity.attrib['iso3166'])

                if country_entity:
                    currency_entities = entity.xpath('.//currency[not(@tender="false")]')

                    try:
                        country_iso = country_entity[0].attrib['alpha3']
                        country = Country.objects.get(iso=country_iso)
                    except:
                        self._print_message('Not found country by iso "%s"', (country_iso,), 'error')
                    else:
                        for currency_entity in currency_entities:
                            currency_iso = currency_entity.attrib['iso4217']

                            try:
                                currency = Currency.objects.get(iso=currency_iso)
                            except:
                                self._print_message('Not found currency by iso "%s"', (currency_iso,), 'error')
                            else:
                                # current currency
                                if not 'to' in currency_entity.attrib and 'from' in currency_entity.attrib and (not country.current_currency or not country.current_currency.iso == currency.iso):
                                    if country.current_currency:
                                        self._print_message(
                                            'Double current currency "%s" [%s] for country "%s" [%s]',
                                            (currency, currency.iso, country, country.iso),
                                            'error'
                                        )
                                    else:
                                        country.current_currency = currency
                                        country.save()
                                        self._print_message(
                                            'Import current country "%s" [%s] currency "%s" [%s]',
                                            (country, country.iso, currency, currency.iso)
                                        )

                                # currency history
                                if not currency.countries.filter(id=country.id).exists():
                                    history = CurrencyHistory(country = country, currency = currency)

                                    if 'to' in currency_entity.attrib:
                                        history.date_to = dateutil.parser.parse(currency_entity.attrib['to']).date()

                                    if 'from' in currency_entity.attrib:
                                        history.date_from = dateutil.parser.parse(currency_entity.attrib['from']).date()

                                    history.save()
                                    self._print_message(
                                        'Import history currency "%s" [%s] currency "%s" [%s]',
                                        (country, country.iso, currency, currency.iso)
                                    )
                            currency.save()
                else:
                    self._print_message('Not found region country by iso 2 "%s"', (entity.attrib['iso3166'],), 'error')

    def _save_model(self, model, iso, name):
        try:
            object = model.objects.get(iso=iso)

            if not object.name == name:
                object.name = name
                object.save()
                return True

        except model.DoesNotExist:
            model.objects.create(iso=iso, name=name)
            return True

        return False

    def _print_message(self, template, args, type = 'message'):
        print_args = []
        for arg in args:
            print_args.append(self.style.IMPORT_VALUE(u'%s' % arg))

        out = type == 'error' and self.stderr or self.stdout
        out.write(template % tuple(print_args))