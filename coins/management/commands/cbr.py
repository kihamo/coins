# -*- coding: utf-8 -*-

# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

import re
from django.core.management.base import BaseCommand, CommandError
from django.utils import termcolors

from optparse import make_option
from lxml.etree import parse, HTMLParser

import urllib2
from urlparse import urlparse

from coins.models import Issue, Country, Series, Mint, MintMark, IssueMint
from datetime import datetime

from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-y', '--year',
            type='int',
            help='Year parse'),
    )

    help = 'Scan cbr.ru site'

    site_url = 'http://cbr.ru'
    base_url = '%s/bank-notes_coins/base_of_memorable_coins/' % site_url

    year_url_template = '%smain.asp?IsDetal=0&Year=%d&s_cat=1&Coin_name=&Seria=&Ser_num=&nominal=0&Metall=0'
    coin_url_template = '%scoins1.asp?cat_num=%s'

    styles = {
        'load_url': termcolors.make_style(fg='blue'),
        'load_image': termcolors.make_style(fg='yellow'),
        'parse_column': termcolors.make_style(fg='cyan'),
        'import_item': termcolors.make_style(fg='green', opts=('bold',)),
        'warning': termcolors.make_style(fg='red', opts=('bold',)),
    }
    _column_names = []

    nominals = {
        '00': .005, '09': 1,   '18': 150,
        '01': .01,  '10': 2,   '19': 200,
        '02': .02,  '11': 3,   '20': 1000,
        '03': .03,  '12': 5,   '21': 10000,
        '04': .05,  '13': 0,   '22': 20,
        '05': .1,   '14': 10,  '23': 500,
        '06': .15,  '15': 25,  '24': 5000,
        '07': .2,   '16': 50,  '25': 25000,
        '08': .5,   '17': 100, '26': 50000
    }

    def _load_url(self, url):
        self.stdout.write(self.styles['load_url']("Load page %s\n" % url))

        try:
            content = urllib2.urlopen(url)
        except:
            raise CommandError('Error load page %s' % url)

        root = parse(content, HTMLParser())
        if not root:
            raise CommandError('Error parse page %s' % url)

        return root.getroot()

    def _load_image(self, url):
        image_url = '%s%s' % (self.site_url, url)
        self.stdout.write(self.styles['load_image']("Load image %s\n" % image_url))

        try:
            content = urllib2.urlopen(image_url)
        except:
            raise CommandError('Error load image %s' % image_url)

        image_tmp = NamedTemporaryFile(delete = True)
        image_tmp.write(content.read())
        image_tmp.flush()
        image_tmp.seek(0)

        return ImageFile(image_tmp)

    def handle(self, year = None, *args, **options):
        doc = self._load_url(self.base_url)

        years = doc.xpath('.//select[@name="Year"]/option')
        if not years:
            raise CommandError('Years list not found')

        if year:
            year = (year,)

        for element in years:
            if year and element.text not in year:
                continue

            year_value = int(element.text)
            year_id = int(element.get('value'))

            self.stdout.write(self.styles['import_item']("Parse year %d\n" % year_value))

            doc = self._load_url(self.year_url_template % (self.base_url, year_id))
            coins = doc.xpath('.//td[@class="content"]/table/tr/td/table/tr[@bgcolor="#ffffff"][count(td)=4]/td[2]/text()')

            if not coins:
                continue

            for catalog_number in coins:
                nominal_index = catalog_number[2:4]
                    
                if not self.nominals.has_key(nominal_index) or not self.nominals[nominal_index]:
                    raise CommandError('Nominal index error (catalog_number: %s)' % catalog_number)

                doc = self._load_url(self.coin_url_template % (self.base_url, catalog_number))
                info = {
                    'nominal': self.nominals[nominal_index],
                    'year': year_value,
                    'catalog_number': catalog_number
                }

                # main information
                text = ''
                index = ''

                for t in doc.xpath('.//table[2]/tr/td[2]/descendant-or-self::*/text()'):
                    t = t.strip()

                    if len(t):
                        strings = t.split("\n")

                        for string in strings:
                            string = string.strip()

                            if len(string):
                                match = re.match('(^[\w ]+):(.*)', string, re.UNICODE)

                                if match:
                                    if len(text):
                                        info[index] = text

                                    index = match.group(1).lower()
                                    text = match.group(2)
                                elif len(strings) == 1:
                                    info['name'] = string
                                else:
                                    text = '%s %s' % (text, string)

                                text = text.strip()

                    if len(text):
                        info[index] = text

                # params
                tag = doc.xpath('.//table[@bgcolor="#4B5B65"]/tr/td/table')[0]

                columns = []
                for font in tag.xpath('tr[1]/td/font'):
                    key = ' '.join([w.strip().lower() for w in font.xpath('text()')])

                    if not key in self._column_names:
                        self._column_names.append(key)
                        self.stdout.write(self.styles['parse_column'](key + "\n"))

                    columns.append(key)
                    info[key] = []

                for tr in tag.xpath('tr[position()>1]'):
                    i = 0
                    for font in tr.xpath('td/font'):
                        text = ' '.join([w.strip() for w in font.xpath('text()')])
                        info[columns[i]].append(text)
                        i += 1

                # descriptions
                tag = doc.xpath('.//table[5]')[0]

                for tr in tag.xpath('tr'):
                    text = ''
                    index = 'description'

                    for td in tr.xpath('td/descendant-or-self::*/text()'):
                        td = td.strip()

                        if len(td):
                            strings = td.split("\n")

                            for string in strings:
                                string = string.strip()

                                if len(string):
                                    match = re.match('(^[\w ]+):(.*)', string, re.UNICODE)

                                    if match:
                                        if len(text):
                                            info[index] = text

                                        index = match.group(1).lower()
                                        text = match.group(2)
                                    else:
                                        text = '%s %s' % (text, string)

                                    text = text.strip()

                    if len(text):
                        info[index] = text

                # images
                info['images'] = tag.xpath('.//img/@src')

                date_key = u'дата выпуска'
                if info.has_key(date_key):
                    info[date_key] = datetime.strptime(info[date_key], '%d.%m.%Y')
                    info['year'] = info[date_key].year

                self._save_coin(info)

    def _save_coin(self, data):
        self.stdout.write(self.styles['import_item']("Import coin number %s\n" % data['catalog_number']))

        if not hasattr(self, '_country'):
            try:
                self._country = Country.objects.get(iso = 'RUS')
            except:
                raise CommandError('RUS country not found')

        if not hasattr(self, '_mints'):
            self._mints = list(Mint.objects.filter(country = self._country))

        issue, created = Issue.objects.get_or_create(
            catalog_number = data['catalog_number'],
            defaults = {
                'year': data['year'],
                'nominal': data['nominal'],
                'currency': self._country.currency,
                'type': Issue.TYPES_CHOICES[0][0]
            }
        )

        issue.country = self._country

        if data['images']:
            images = {
                'image_obverse': data['images'][0]
            }

            if len(data['images']) > 1:
                images['image_reverse'] = data['images'][1]


            for model_key, image_src in images.items():
                try:
                    if not hasattr(issue, model_key) or not getattr(issue, model_key):
                        getattr(issue, model_key).save(
                            urlparse(image_src).path.split('/')[-1],
                            self._load_image(image_src)
                        )
                except:
                    self.stderr.write((self.styles['warning']('Error load %s file for coin id %d' % (model_key, issue.pk))))

        mapping = {
            'catalog_number'    : 'catalog_number',
            'name'              : 'name',

            u'дата выпуска'     : 'date_issue',
            u'серия'            : 'series',

            'description'       : 'desc',
            u'аверс'            : 'desc_obverse',
            u'реверс'           : 'desc_reverse',
            u'оформление гурта' : 'desc_edge',

            u'сплав'            : 'alloy',
            u'металл, проба'    : 'alloy',
            u'тираж, шт.'       : 'mintage',
            u'диаметр, мм'      : 'diameter',
            u'толщина, мм'      : 'thickness',
            u'масса общая, г'   : 'weight',
        }

        for data_key, model_key in mapping.items():
            if data.has_key(data_key):
                set_new_value = False
                new_value = data[data_key]

                if model_key == 'series':
                    new_value, created = Series.objects.get_or_create(name = new_value)
                    set_new_value = True
                elif model_key == 'mintage':
                    new_value = sum([int(i) for i in new_value])
                elif model_key in ['diameter', 'thickness', 'weight']:
                    match = re.match('(^[0-9]+[0-9,.]*[0-9]*).*', new_value[0], re.UNICODE)
                    if not match:
                        continue

                    new_value = float(match.group(1).replace(',', '.'))
                elif type(new_value) is list or type(new_value) is tuple:
                    new_value = new_value[0]

                last_value = None
                if hasattr(issue, model_key):
                    last_value = getattr(issue, model_key)

                if set_new_value or (last_value is None or last_value == ''):
                    issue.__setattr__(model_key, new_value)

        issue.save()

        # mints
        data_key = u'чеканка'
        if data.has_key(data_key) and not issue.mint.count():
            mints = data[data_key].split(';')
            for mint_data in mints:
                match = re.match(
                    r'^([^(]+?)\s*\((.+?)\)(?:\s*[^0-9\s]*\s*([0-9]+)\s*([^\s.]+))?',
                    mint_data.strip().lower(),
                    re.UNICODE
                )

                if match:
                    found = False
                    mint_name = match.group(1).replace('c', u'с')
                    mark_name = match.group(2)

                    for mint in self._mints:
                        if mint.__unicode__().lower() == mint_name:
                            kwargs = {
                                'issue': issue,
                                'mint': mint
                            }

                            mark_found = False
                            for mark in mint.mintmark_set.all():
                                if mark.__unicode__().lower() == mark_name:
                                    kwargs['mint_mark'] = mark
                                    mark_found = True
                                    break

                            if not mark_found:
                                mark = MintMark(mark = mark_name, mint = mint)
                                kwargs['mint_mark'] = mark

                                mark.save()
                                self.stderr.write((self.styles['import_item']("Add mint mark '%s'\n" % mark)))

                            if match.group(3):
                                kwargs['mintage'] = int(match.group(3))

                                if match.group(4):
                                    if match.group(4) == u'млн':
                                        kwargs['mintage'] *= 1000000
                                    else:
                                        self.stderr.write((self.styles['warning']("Unknown unit '%s'\n" % match.group(4))))
                            elif len(mints) == 1 and issue.mintage:
                                kwargs['mintage'] = issue.mintage

                            IssueMint(**kwargs).save()

                            found = True
                            break

                    if not found:
                        self.stderr.write((self.styles['warning']("Mint '%s' not found\n" % mint_name)))