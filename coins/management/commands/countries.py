# -*- coding: utf-8 -*-

# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

from django.core.management import base, color
from django.utils.termcolors import make_style

from coins.models import Country, Currency

from lxml.html import parse
import re

class Command(base.BaseCommand):
    help = 'Import countries and currency'

    def __init__(self):
        super(Command, self).__init__()

        self.style.IMPORT_VALUE = make_style(fg='cyan', opts=('bold',))

    def handle(self, year = None, *args, **options):
        #self._import_russian_name_countries()
        #self._import_russian_name_currencies()

        self._import_countries_and_currencies_codes()

    def _import_countries_and_currencies_codes(self):
        doc = parse('http://unicode.org/repos/cldr/trunk/common/supplemental/supplementalData.xml')
        entities = doc.xpath('.//supplementaldata/currencydata/region')

        for entity in entities:
            country_entity = doc.xpath('.//supplementaldata/codemappings/territorycodes[@type="%s"][@alpha3]' % entity.attrib['iso3166'])
            currency_entity = entity.xpath('.//currency[not(@to)]')

            if currency_entity and country_entity:
                country_iso = country_entity[0].attrib['alpha3']
                currency_iso = currency_entity[0].attrib['iso4217']

                try:
                    country = Country.objects.get(iso=country_iso)
                    currency = Currency.objects.get(iso=currency_iso)
                except:
                    pass
                else:
                    if not country.currency or not country.currency.iso == currency.iso:
                        country.currency = currency
                        country.save()

                        self._print_message("Import current country %s currency %s", country, currency)

    def _import_russian_name_countries(self):
        doc = parse('http://www.artlebedev.ru/tools/country-list/xml/')
        entities = doc.xpath('.//country-list/country')

        for entity in entities:
            iso = entity.xpath('.//alpha3/text()')[0]
            name = entity.xpath('.//name/text()')[0].strip()

            if self._save_model(Country, iso, name):
                self._print_message("Import country %s iso %s", name, iso)

    def _import_russian_name_currencies(self):
        doc = parse('http://framework.zend.com/svn/framework/standard/trunk/library/Zend/Locale/Data/ru.xml')
        entities = doc.xpath('.//numbers/currencies/currency')

        for entity in entities:
            iso = entity.attrib['type']
            name = re.sub('\(.*\)', '', entity.xpath('.//displayname/text()')[0]).strip()

            if self._save_model(Currency, iso, name):
                self._print_message("Import currency %s iso %s", name, iso)

    def _save_model(self, model, iso, name):
        try:
            object = model.objects.get(iso=iso)

            if not object.name == name:
                object.name = name
                object.save()
                return True

        except model.DoesNotExist:
            object = model(iso=iso, name=name)
            object.save()
            return True

        return False

    def _print_message(self, template, *args):
        print_args = []
        for arg in args:
            print_args.append(self.style.IMPORT_VALUE(str(arg)))

        self.stdout.write(template % tuple(print_args))