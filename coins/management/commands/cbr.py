# -*- coding: utf-8 -*-

import re
import pprint

from coins.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management.color import color_style
from decimal import Decimal

from optparse import make_option
from lxml.etree import parse, HTMLParser

from urllib import urlencode
import urllib2
from urlparse import urlparse

from coins.models import CoinIssue, Country, Series, Mint, MintMark, IssueMint
from datetime import datetime

from django.core.files.images import ImageFile
from django.core.files.temp import NamedTemporaryFile


class ParseErrorException(Exception):
    pass


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-y', '--year', type='string', help='Year parse'),
        make_option('-n', '--number', type='str', help='Coin catalog number'),
        make_option('-d', '--debug', action='store_true', help='Debug mode'),
        make_option('-t', '--test', action='store_true', help='Test mode'),
    )

    help = 'Scan cbr.ru site'
    debug = False
    test = False
    verbosity = 1

    site_url = 'http://cbr.ru'
    base_url = '%s/bank-notes_coins/' % site_url

    year_url_template = '%sDefault.aspx?Prtid=coins_base' % base_url
    coin_url_template = '%sBase_of_memorable_coins/' \
                        'ShowCoins.aspx?cat_num=%%s' \
                        % base_url

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

    _params_mapping = {
        u'каталожный номер': 'catalog_number',
        u'серия': 'series',
        u'географическая серия': 'series',
        u'историческая серия': 'series',
        u'набор памятных монет': 'series',
        u'спортивная серия': 'series',
        u'дата выпуска': 'date_issue',
        u'сплав': 'alloy',
        u'металл, проба': 'alloy',
        u'материал': 'alloy',
        u'тираж, шт.': 'mintage',
        u'диаметр, мм': 'diameter',
        u'толщина, мм': 'thickness',
        u'масса общая, г': 'weight',
        u'оформление гурта': 'desc_edge',
        u'оформление гуртa': 'desc_edge',
        u'оформление': 'desc_edge',
        u'чеканка': 'mint',
        u'художник': 'painter',
        u'худжник': 'painter',
        u'художники': 'painter',
        u'автор эскиза': 'painter',
        u'скульптор': 'sculptor',
        u'скуоьптор': 'sculptor',
        u'скульпторы': 'sculptor',
        u'художник и скульптор': ('painter', 'sculptor'),
        u'художник и скульптур': ('painter', 'sculptor'),
        u'художники и скульпторы': ('painter', 'sculptor'),
    }

    _re_mint_fast_check = re.compile(
        ur'\b([СC]П[MМ]Д|[MМ][MМ]Д|Л[MМ]Д|[СC][MМ]Д)\b',
        re.I | re.U
    )
    _re_mint = re.compile(
        r'\W*'
        # mint name
        r'[\w\s-]+?'
        # mint marks
        r'(?:'
        r'\(([^)]+?)|'
        # ex. 5111-0209
        ur'\b([СC]П[MМ]Д|[MМ][MМ]Д|Л[MМ]Д|[СC][MМ]Д)\b'
        r')(?:\)|$)'
        # mintage
        r'(?:\s*[^\d\s.]*\s*([\d\s]+?)\s*'
        # multiplier
        r'(\w+)(?:[.]|$))?',
        re.I | re.U
    )

    def __init__(self):
        super(Command, self).__init__()

        self.urllib_handler = urllib2.HTTPHandler(debuglevel=0)
        opener = urllib2.build_opener(self.urllib_handler)
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/28.0.1490.2 Safari/537.36')
        ]
        urllib2.install_opener(opener)

        keys = map(re.escape, self._params_mapping.keys())
        exp = ur'^[\W\s]*(' \
              ur'(?:%s)(?![\w\s]*:)|[\w\s]+?(?=\s*:)' \
              ur')[:\s]*(.*?)[\s.]*$' \
              % '|'.join(sorted(keys, key=len, reverse=True))
        self._re_params = re.compile(exp, re.I | re.U)

        '''
        Error parse:
        - 5109-0016 (not parse desc_edge)
        - 5111-0162 (mint mark)
        '''

    def _load_url(self, url, data=None):
        try:
            if data:
                data = urlencode(data)

            self._info('Load url %s', url, level=3)
            content = urllib2.urlopen(url, data)
        except Exception as e:
            raise CommandError('Error "%s" load page %s' % (e, url))

        root = parse(content, HTMLParser(encoding='utf-8'))
        if not root:
            raise CommandError('Error parse page %s' % url)

        return root.getroot()

    def _load_image(self, url):
        image_url = '%s%s' % (self.site_url, url)

        try:
            content = urllib2.urlopen(image_url)
            self._info('Load image %s', url, level=3)
        except:
            raise CommandError('Error load image %s' % image_url)

        image_tmp = NamedTemporaryFile(delete=True)
        image_tmp.write(content.read())
        image_tmp.flush()
        image_tmp.seek(0)

        return ImageFile(image_tmp)

    def handle(self, year=None, number=None, test=None,
               debug=None, verbosity=1, *args, **options):
        self.test = test
        self.debug = debug
        self.verbosity = int(verbosity)
        self.style = color_style()

        if debug:
            self.urllib_handler.set_http_debuglevel(1)

        if number:
            self._parse_coin(number.split(','))
        else:
            self._parse_year(year.split(',') if year else year)

    def _parse_year(self, years):
        doc = self._load_url(self.year_url_template)

        years_exists = doc.xpath('.//select[@id="'
                                 'ctl00_ContentPlaceHolder1_'
                                 'UC_Plug_12434_YearSelect'
                                 '"]/option')
        if not years_exists:
            raise CommandError('Years list not found')

        if years:
            if type(years) is list or type(years) is tuple:
                years = map(int, years)
            else:
                years = (int(years),)

        params = {}
        for param in doc.xpath('.//form[@id="aspnetForm"]/div/input'):
            params[param.get('name')] = param.get('value')

        for element in years_exists:
            year = int(element.text)

            if years and year not in years:
                continue

            self._info('Parse year %d', year)

            params['ctl00$ContentPlaceHolder1$UC_Plug_12434$YearSelect'] = year

            doc = self._load_url(self.year_url_template, params)
            coins = doc.xpath('.//span[@id="'
                              'ctl00_ContentPlaceHolder1_'
                              'UC_Plug_12434_ResultData"]'
                              '/table/tr[not(@align="center")][count(td)=4]'
                              '/td[2]/text()')

            self._parse_coin(coins)

    def _parse_coin(self, catalog_numbers):
        if not catalog_numbers:
            self._error('Coins not found')

        self._country = Country.objects.get(iso='RUS')
        self._mints = list(Mint.objects.filter(country=self._country))

        catalog_numbers = map(str, catalog_numbers)
        for catalog_number in catalog_numbers:
            try:
                nominal_index = catalog_number[2:4]

                if (not nominal_index in self.nominals or
                   not self.nominals[nominal_index]):
                    raise ParseErrorException('Nominal index error')

                self._info('Parse coin %s', catalog_number)

                doc = self._load_url(self.coin_url_template % catalog_number)
                info = {
                    'nominal': self.nominals[nominal_index]
                }

                # check content labels
                main_information = doc.xpath('.//div[@class="BnkHeader_block"]'
                                             '/descendant-or-self::*')
                if not main_information:
                    raise ParseErrorException('Main information not found')

                others = doc.xpath('//*[@id="form1"]/table[2]/tr[3]'
                                   '/td[@valign="top"]/descendant-or-self::*')
                if not others:
                    raise ParseErrorException('Others params not found')

                params = doc.xpath('//*[@id="form1"]/table[1]')
                if not params:
                    raise ParseErrorException('Main params not found')

                desc_obverse = doc.xpath('//*[@id="form1"]/table[2]/tr[1]/'
                                         'td[4]/descendant-or-self::*/'
                                         'text()[normalize-space(.)]')
                if not desc_obverse:
                    raise ParseErrorException('Obverse description not found')

                desc_reverse = doc.xpath('//*[@id="form1"]/table[2]/tr[2]/'
                                         'td[3]/descendant-or-self::*/'
                                         'text()[normalize-space(.)]')
                if not desc_reverse:
                    raise ParseErrorException('Reverse description not found')

                images = doc.xpath('//*[@id="form1"]/table[2]/.//img/@src')
                if not len(images) == 2:
                    raise ParseErrorException('Error count images.'
                                              ' Found %d images' % len(images))

                desc = doc.xpath('//*[@id="form1"]/table[2]/tr[4]/td[2]/'
                                 '*/text()')
                if not desc:
                    raise ParseErrorException('Description not found')

                delimited_params = \
                    [e for e in main_information + others if e.text or e.tail]

                # main information
                key = None
                for e in delimited_params:
                    string = e.text or e.tail
                    string = string.strip().strip('.')

                    if not string:
                        continue

                    m = self._re_params.match(string)

                    # first line: series
                    if e.tag == 'b':
                        info['series'] = m.group(2) if m else string
                    # second line: name
                    elif not 'name' in info:
                        info['name'] = string
                    # others line
                    elif not m:
                        # ex. 5217-0017
                        if self._re_mint_fast_check.search(string):
                            if key == 'mint':
                                value += '\n%s' % string
                            else:
                                self._add_param(info, 'mint', string)
                        # ex. 5110-0039
                        elif key == 'mint':
                            self._notice('Error mint string "%s" (issue: %s)',
                                         string, catalog_number)
                        elif key:
                            value += '\n%s' % string
                        else:
                            self._notice('Error parse delimited param "%s" '
                                         '(issue: %s)', string, catalog_number)
                    else:
                        if key:
                            self._add_param(info, key, value)

                        key = m.group(1).lower().replace('c', u'с')
                        if key in self._params_mapping:
                            key = self._params_mapping[key]
                        elif key is not None:
                            self._notice('Unknown attribute "%s" (issue: %s)',
                                         key, catalog_number)

                        value = m.group(2)

                if key:
                    self._add_param(info, key, value)

                # main params
                columns = []
                for td in params[0].xpath('tr[@class="monet_header_cl"]/td'):
                    key = ' '.join([
                        x.strip(' *').strip().lower().replace('c', u'с')
                        for x in td.xpath('text()')
                    ])

                    if key in self._params_mapping:
                        key = self._params_mapping[key]

                        columns.append(key)
                        info[key] = []
                    else:
                        columns.append(None)

                for tr in params[0].xpath('tr[position()>1]'):
                    i = 0
                    for td in tr.xpath('td'):
                        if columns[i]:
                            info[columns[i]].append(
                                ''.join(td.xpath('text()')).strip()
                            )
                        i += 1

                # obverse and reverse
                self._add_param(info, 'desc_obverse', '\n'.join(
                    [x.strip() for x in desc_obverse]
                ))

                self._add_param(info, 'desc_reverse', '\n'.join(
                    [x.strip() for x in desc_reverse]
                ))

                # images
                info['image_obverse'] = images[0]
                info['image_reverse'] = images[1]

                # type juggling
                if not 'date_issue' in info:
                    raise ParseErrorException('Date issue not found')

                info['date_issue'] = datetime.strptime(info['date_issue'],
                                                       '%d.%m.%Y').date()

                info['year'] = info['date_issue'].year

                # mints
                if 'mintage' in info:
                    info['mintage'] = sum([
                        int(re.sub('[^\d]', '', i)) for i in info['mintage']
                    ])

                if not 'mint' in info:
                    self._notice('Mint information not found (issue: %s)',
                                 catalog_number)
                else:
                    info['mint'] = re.sub('[\n\r\t]+', ' ', info['mint'])

                    m = self._re_mint.findall(info['mint'])
                    if not m:
                        raise ParseErrorException('Error parse mint')

                    info['mint'] = []
                    total = 0

                    for match in m:
                        mint_default = {
                            'mintage': None
                        }

                        if match[2]:
                            mint_default['mintage'] = int(
                                match[2].replace(' ', '')
                            )
                            if match[3] and match[3].lower() != u'шт':
                                if match[3].lower() == u'млн':
                                    mint_default['mintage'] *= 1000000
                                else:
                                    self._notice('Unknown unit "%s" '
                                                 '(issue: %s)', match[3],
                                                 catalog_number)

                        marks = match[0] or match[1]
                        for mark in self._re_mint_fast_check.findall(marks):
                            mint = mint_default.copy()
                            mark = mark.upper().replace('M', u'М') \
                                               .replace('C', u'С')

                            if mark in [u'СПМД', u'СМД', u'ЛМД']:
                                if info['year'] >= 1996:
                                    mint['name'] = u'Санкт-Петербургский' \
                                                   u' монетный двор'
                                else:
                                    mint['name'] = u'Ленинградский' \
                                                   u' монетный двор'
                            elif mark == u'ММД':
                                mint['name'] = u'Московский монетный двор'
                            else:
                                self._notice('Unknown mint mark %s (issue:'
                                             ' %s)', mark, catalog_number)
                                continue

                            if mint['mintage']:
                                total += mint['mintage']

                            mint['mark'] = mark
                            info['mint'].append(mint)

                    if 'mintage' in info:
                        if total > 0 and total != info['mintage']:
                            self._notice('Total mintage %s is not the same as'
                                         ' the total mintage %s (issue: %s)',
                                         info['mintage'], total,
                                         catalog_number)
                        elif (len(info['mint']) == 1 and
                              info['mint'][0]['mintage'] is None):
                            info['mint'][0]['mintage'] = info['mintage']

                # descriptions
                self._add_param(info, 'desc', desc[0])

                # remove double whitespace
                for key in info:
                    if isinstance(info[key], unicode):
                        info[key] = re.sub('[ \t\r\f\v]+', ' ', info[key])
                        info[key] = re.sub('\n+\s*', '\n', info[key])

                # coin type
                info['type'] = CoinIssue.TYPES_CHOICES[0][0]
                if (int(info['catalog_number'][0]) in [3, 5] and
                   int(info['catalog_number'][1]) in [1, 2, 3, 4, 6]):
                    info['type'] = CoinIssue.TYPES_CHOICES[2][0]

                if not self.test:
                    self._save_coin(info)
                elif self.debug:
                    self._dump_coin(info)
            except ParseErrorException, e:
                self._error('%s (issue: %s)', e, catalog_number)

    def _add_param(self, info, key, value):
        value = re.sub('[\s]{2,}', ' ', value.strip())

        if len(value):
            if not hasattr(key, '__iter__'):
                key = [key]

            for var in key:
                if var in info:
                    info[var] += value
                else:
                    info[var] = value

    def _dump_coin(self, info):
        for key, value in info.items():
            self._info('%s: ', key, style=self.style.SQL_FIELD)

            if type(value) is list or type(value) is tuple:
                value = pprint.pformat(value)
                if value:
                    if value[0] in ('"', "'"):
                        value = value.decode('string_escape')
                    elif value[1:3] in ("u'", 'u"'):
                        value = value.decode('unicode_escape') \
                                     .encode(self.stdout.encoding)

            self._info(value, style=self.style.SQL_KEYWORD)

    def _save_coin(self, info):
        # save issue
        issue, created = CoinIssue.objects.get_or_create(
            catalog_number=info['catalog_number'],
            defaults={
                'name': info['name'],
                'type': info['type'],
                'nominal': info['nominal'],
                'country': self._country,
                'currency': self._country.current_currency,
                'year': info['year']
            }
        )

        if created:
            self._info('Add coin issue "%s"', issue.name, level=2)

        for field in issue._meta.fields:
            if not field.name in info:
                continue

            new_value = info[field.name]

            if field.get_internal_type() == 'FileField':
                if not getattr(issue, field.name):
                    try:
                        getattr(issue, field.name).save(
                            urlparse(new_value).path.split('/')[-1],
                            self._load_image(new_value)
                        )
                    except:
                        self._error('Error load %s file for coin id %d',
                                    field.name, issue.pk)
            else:
                if field.name == 'series':
                    new_value, created = Series.objects.get_or_create(
                        name=new_value)

                    if created:
                        self._info('Add series "%s"', new_value, level=2)

                elif field.get_internal_type() == 'DecimalField':
                    if hasattr(new_value, '__iter__'):
                        new_value = new_value[0]

                    if not isinstance(new_value, unicode):
                        new_value = unicode(new_value)

                    match = re.match('(^\d+[\d,.]*\d*).*', new_value, re.U)
                    if not match:
                        continue

                    new_value = Decimal(match.group(1).replace(',', '.'))
                elif hasattr(new_value, '__iter__'):
                    new_value = new_value[0]

                current_value = getattr(issue, field.name)

                if current_value is None or current_value != new_value:
                    issue.__setattr__(field.name, new_value)

        issue.save()

        # save mints
        if 'mint' in info:
            for mint_info in info['mint']:
                mint_info['name'] = mint_info['name'].split(':')[-1].strip()

                mint, created = Mint.objects.get_or_create(
                    name=mint_info['name'],
                    country=self._country)
                if created:
                    self._info('Add mint "%s"', mint, level=2)

                if mint_info['mark']:
                    mark, created = MintMark.objects.get_or_create(
                        mark=mint_info['mark'],
                        mint=mint)
                    if created:
                        self._info('Add mark "%s" for mint "%s"',
                                   mark, mint, level=2)
                else:
                    mark = None

                issue_mint, created = IssueMint.objects.get_or_create(
                    mint=mint, issue=issue,
                    defaults={
                        'mintage': mint_info['mintage'],
                        'mint_mark': mark
                    }
                )
                if created:
                    self._info('Add mint "%s" for issue "%s"', mint, issue,
                               level=2)
                elif (mint_info['mintage'] and
                      issue_mint.mintage != mint_info['mintage']):
                    issue_mint.mintage = mint_info['mintage']
                    issue_mint.save()

                    self._info('Update mintage %d for mint "%s" in issue "%s"',
                               issue_mint.mintage, mint, issue, level=2)
