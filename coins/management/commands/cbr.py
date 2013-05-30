# -*- coding: utf-8 -*-

# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

import re
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
from lxml.etree import parse, HTMLParser

from urllib import urlencode
import urllib2
from urlparse import urlparse

from coins.models import CoinIssue, Country, Series, Mint, MintMark, IssueMint
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
    base_url = '%s/bank-notes_coins/' % site_url

    year_url_template = '%sDefault.aspx?Prtid=coins_base' % base_url
    coin_url_template = '%sBase_of_memorable_coins/ShowCoins.aspx?cat_num=%%s' % base_url

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

    _main_information_mapping = {
        u'каталожный номер'     : 'catalog_number',
        u'дата выпуска'         : 'date_issue'
    }
    _main_params_mapping = {
        u'сплав'          : 'alloy',
        u'металл, проба'  : 'alloy',
        u'материал'       : 'alloy',
        u'тираж, шт.'     : 'mintage',
        u'диаметр, мм'    : 'diameter',
        u'толщина, мм'    : 'thickness',
        u'масса общая, г' : 'weight',
    }
    _other_params_mapping = {
        u'оформление гурта' : 'desc_edge',
        u'чеканка'          : 'mint'
    }
    _mint_names_mapping = {
        u'санкт-петергбургский монетный двор' : u'санкт-петербургский монетный двор',
        u'санкт-петергбурский монетный двор'  : u'санкт-петербургский монетный двор',
        u'санкт-петербугрский монетный двор'  : u'санкт-петербургский монетный двор',
        u'санкт петербургский'                : u'санкт-петербургский монетный двор',

        u'ленинградский монетный двор'        : u'ленинградский монетный двор',
        u'лениградский монетный двор'         : u'ленинградский монетный двор',

        u'московкий монетный двор'            : u'московский монетный двор',
        u'московский монетный'                : u'московский монетный двор',
    }

    _re_params = re.compile(r'^[\s]*([^:]+?)[\s]*:[\s]*(.+?)[\s.]*$', re.UNICODE)
    _re_mint = re.compile(r'[\W]*([^(]+?)\s*\((.+?)\)(?:\s*[^\d\s.]*\s*([\d\s]+?)\s*([\w]+)[.])?', re.UNICODE)

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

    def _load_image(self, url):
        image_url = '%s%s' % (self.site_url, url)
        self.stdout.write(self.style.HTTP_INFO('Load image %s' % image_url))

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
        doc = self._load_url(self.year_url_template)

        years = doc.xpath('.//select[@id="ctl00_ContentPlaceHolder1_UC_Plug_12434_YearSelect"]/option')
        if not years:
            raise CommandError('Years list not found')

        params = {}
        for param in doc.xpath('.//form[@id="aspnetForm"]/div/input'):
            params[param.get('name')] = param.get('value')

        self._country = Country.objects.get(iso = 'RUS')
        self._mints = list(Mint.objects.filter(country = self._country))

        if year:
            year = (int(year),)

        for element in years:
            year_value = int(element.text)

            if year and year_value not in year:
                continue

            self.stdout.write('Parse year %d' % year_value)

            params['ctl00$ContentPlaceHolder1$UC_Plug_12434$YearSelect'] = year_value
            doc = self._load_url(self.year_url_template, params)

            coins = doc.xpath('.//span[@id="ctl00_ContentPlaceHolder1_UC_Plug_12434_ResultData"]/table/tr[not(@align="center")][count(td)=4]/td[2]/text()')

            if not coins:
                self.stderr.write('Coins not found')
                continue

            for catalog_number in coins:
                nominal_index = catalog_number[2:4]
                    
                if not self.nominals.has_key(nominal_index) or not self.nominals[nominal_index]:
                    self.stderr.write('Nominal index error (catalog_number: %s)' % catalog_number)
                    continue

                self.stdout.write('Parse coin %s' % catalog_number)

                doc = self._load_url(self.coin_url_template % catalog_number)
                info = {
                    'nominal':        self.nominals[nominal_index],
                    'year':           year_value,
                    'catalog_number': catalog_number
                }

                # main information
                main_information = doc.xpath('.//div[@class="BnkHeader_block"]/descendant-or-self::*')
                if not main_information:
                    self.stderr.write('Main information not found')
                else:
                    for node in main_information:
                        string = node.text or node.tail
                        if not string:
                            continue

                        string = string.strip()
                        if not string:
                            continue

                        match = self._re_params.match(string)
                        if not match:
                            if 'name' in info:
                                self.stderr.write('Error parse main information string "%s"' % string)
                            elif node.tag == 'b':
                                info['series'] = string
                            else:
                                info['name'] = string

                            continue
                        elif node.tag == 'b':
                            info['series'] = match.group(2)

                        key = match.group(1).lower().replace('c', u'с')
                        if not key in self._main_information_mapping:
                            self.stderr.write('Not found key for main information "%s"' % key)
                            continue

                        info[self._main_information_mapping[key]] = match.group(2)

                # main params
                main_params = doc.xpath('//*[@id="form1"]/table[1]')
                if not main_params:
                    self.stderr.write('Main params not found')
                else:
                    columns = []
                    for node in main_params[0].xpath('tr[@class="monet_header_cl"]/td'):
                        key = ' '.join([x.strip(' *').strip().lower().replace('c', u'с') for x in node.xpath('text()')])

                        if key in self._main_params_mapping:
                            key = self._main_params_mapping[key]

                        columns.append(key)
                        info[key] = []

                    for tr in main_params[0].xpath('tr[position()>1]'):
                        i = 0
                        for td in tr.xpath('td'):
                            info[columns[i]].append(''.join(td.xpath('text()')).strip())
                            i += 1

                # obverse and reverse
                desc_obverse = doc.xpath('//*[@id="form1"]/table[2]/tr[1]/td[4]/descendant-or-self::*/text()[normalize-space(.)]')
                if not desc_obverse:
                    self.stderr.write('Obverse description not found')
                else:
                    info['desc_obverse'] = '\n'.join([x.strip() for x in desc_obverse])

                desc_reverse = doc.xpath('//*[@id="form1"]/table[2]/tr[2]/td[3]/descendant-or-self::*/text()[normalize-space(.)]')
                if not desc_reverse:
                    self.stderr.write('Reverse description not found')
                else:
                    info['desc_reverse'] = '\n'.join([x.strip() for x in desc_reverse])

                # images
                images = doc.xpath('//*[@id="form1"]/table[2]/.//img/@src')
                if not len(images) == 2:
                    self.stderr.write('Error count images. Found %d images' % len(images))
                else:
                    info['image_obverse'] = images[0]
                    info['image_reverse'] = images[1]

                # others params
                others = doc.xpath('//*[@id="form1"]/table[2]/tr[3]/td[@valign="top"]/descendant-or-self::*/text()[normalize-space(.)]')
                if not others:
                    self.stderr.write('Others rapams not found')
                else:
                    key = None

                    for string in others:
                        string = string.strip()
                        match = self._re_params.match(string)
                        if not match:
                            if key:
                                info[key] += '\n%s' % string.strip().strip('.')
                            else:
                                self.stderr.write('Error parse other param "%s"' % string)
                        else:
                            key = match.group(1).lower().replace('c', u'с')

                            if key in self._other_params_mapping:
                                key = self._other_params_mapping[key]

                            info[key] = match.group(2)

                # mints
                if 'mintage' in info:
                    info['mintage'] = sum([int(re.sub('[^\d]', '', i)) for i in info['mintage']])

                if not 'mint' in info:
                    self.stderr.write('Mint information not found')
                else:
                    mints = info['mint'].replace('\n', ';').split(';')
                    info['mint'] = []
                    total_mintage = 0

                    for string in mints:
                        string = string.strip()

                        if not string:
                            continue

                        match = self._re_mint.match(string.lower())
                        if not match:
                            self.stderr.write('Error parse mint "%s"' % string)
                            continue

                        mint = {
                            'name'   : ' '.join(match.group(1).replace('c', u'с').split()),
                            'mark'   : match.group(2),
                            'mintage': match.group(3)
                        }

                        if self._mint_names_mapping.has_key(mint['name']):
                            mint['name'] = self._mint_names_mapping[mint['name']]

                        mint['name'] = mint['name'].title()

                        if mint['mark']:
                            mint['mark'] = mint['mark'].upper()

                        if mint['mintage']:
                            mint['mintage'] = int(mint['mintage'].replace(' ', ''))
                            if match.group(4) and match.group(4) != u'шт':
                                if match.group(4) == u'млн':
                                    mint['mintage'] *= 1000000
                                else:
                                    self.stderr.write('Unknown unit "%s"' % match.group(4))

                            total_mintage += mint['mintage']

                        info['mint'].append(mint)

                    if 'mintage' in info:
                        if total_mintage > 0 and total_mintage != info['mintage']:
                            self.stderr.write('Total mintage %s is not the same as the total mintage %s' % (info['mintage'], total_mintage))
                        elif len(info['mint']) == 1 and not info['mint'][0]['mintage']:
                            info['mint'][0]['mintage'] = info['mintage']

                # descriptions
                desc = doc.xpath('//*[@id="form1"]/table[2]/tr[4]/td[2]/*/text()')
                if not desc:
                    self.stderr.write('Description not found')
                else:
                    info['desc'] = desc[0].strip()

                # remove double whitespace
                for key in info:
                    if isinstance(info[key], type(u'')):
                        info[key] = re.sub('[ \t\r\f\v]+', ' ', info[key].strip('"\''))
                        info[key] = re.sub('\n+', '\n', info[key])

                # type juggling
                if 'date_issue' in info:
                    info['date_issue'] = datetime.strptime(info['date_issue'], '%d.%m.%Y')

                # coin type
                info['type'] = CoinIssue.TYPES_CHOICES[0][0]
                if int(info['catalog_number'][0]) in [3, 5] and int(info['catalog_number'][1]) in [1, 2, 3, 4, 6]:
                    info['type'] = CoinIssue.TYPES_CHOICES[2][0]

                self._save_coin(info)

    def _save_coin(self, info):
        self.stdout.write('Import coin number %s' % info['catalog_number'])

        # save issue
        issue, created = CoinIssue.objects.get_or_create(
            catalog_number = info['catalog_number'],
            defaults = {
                'name'         : info['name'],
                'type'         : info['type'],
                'nominal'      : info['nominal'],
                'country'      : self._country,
                'currency'     : self._country.current_currency,
                'year'         : info['year']
            }
        )

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
                        self.stderr.write('Error load %s file for coin id %d' % (field.name, issue.pk))
            else:
                if field.name == 'series':
                    new_value, created = Series.objects.get_or_create(name = new_value)

                    if created:
                        self.stdout.write('Add series "%s"' % new_value)
                elif field.name in ['diameter', 'thickness', 'weight']:
                    match = re.match('(^[0-9]+[0-9,.]*[0-9]*).*', new_value[0], re.UNICODE)
                    if not match:
                        continue

                    new_value = float(match.group(1).replace(',', '.'))
                elif type(new_value) is list or type(new_value) is tuple:
                    new_value = new_value[0]

                current_value = getattr(issue, field.name)
                if current_value is None or current_value == '':
                    issue.__setattr__(field.name, new_value)

        self.stdout.write('Save %s coin issue "%s"' % ('new' if created else 'exists', issue.name))
        issue.save()

        # save mints
        if 'mint' in info:
            for mint_info in info['mint']:
                # http://cbr.ru/bank-notes_coins/Base_of_memorable_coins/ShowCoins.aspx?cat_num=5109-0079
                mint_info['name'] = mint_info['name'].split(':')[-1].strip()

                mint, created = Mint.objects.get_or_create(name = mint_info['name'], country = self._country)
                if created:
                    self.stdout.write('Add mint "%s"' % mint)

                if mint_info['mark']:
                    mark, created = MintMark.objects.get_or_create(mark = mint_info['mark'], mint = mint)
                    if created:
                        self.stdout.write('Add mark "%s" for mint "%s"' % (mark, mint))
                else:
                    mark = None

                issue_mint, created = IssueMint.objects.get_or_create(
                    mint = mint, issue = issue,
                    defaults = {
                        'mintage'   : mint_info['mintage'],
                        'mint_mark' : mark
                    }
                )
                if created:
                    self.stdout.write('Add mint "%s" for issue "%s"' % (mint, issue))
                elif issue_mint.mintage != mint_info['mintage']:
                    issue_mint.mintage = mint_info['mintage']
                    issue_mint.save()
                    self.stdout.write('Update mintage %d for mint "%s" in issue "%s"' % (issue_mint.mintage, mint, issue))