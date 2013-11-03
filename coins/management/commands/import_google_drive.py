# -*- coding: utf-8 -*-

from django.core.management.base import CommandError
from django.core.exceptions import ObjectDoesNotExist
from coins.management.base import BaseCommand

import httplib2
import re
import xlrd
import os

from oauth2client.client import OAuth2Credentials, OAuth2WebServerFlow
from apiclient.discovery import build
from optparse import make_option

from coins.models import Collection, CoinIssue, MintMark, Coin


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--client_id', type='string',
                    help='Google drive client identifier'),
        make_option('-s', '--client_secret', type='string',
                    help='Google drive client secret'),
        make_option('-f', '--filename', type='string',
                    help='File name in Google drive'),
    )

    help = 'Import collections from google drive file'

    def handle(self, client_id=None, client_secret=None, filename=None,
               verbosity=1, *args, **options):

        self.verbosity = int(verbosity)

        if client_id is None or client_secret is None or filename is None:
            raise CommandError('client_id or client_secret or file not given')

        self.service = self.authorize(client_id, client_secret)
        self.parse_file(filename)

    def authorize(self, client_id, client_secret):
        credentials = self.load_credentials(client_id, client_secret)

        http = httplib2.Http()
        credentials.authorize(http)

        return build('drive', 'v2', http=http)

    def load_credentials(self, client_id, client_secret):
        app_root = os.path.realpath(os.path.join(__file__, '..', '..', '..'))
        credentials_file = os.path.join(app_root, 'data', 'credentials.json')

        try:
            with open(credentials_file, 'r') as f:
                credentials = OAuth2Credentials.new_from_json(f.read())
        except IOError:
            flow = OAuth2WebServerFlow(
                client_id,
                client_secret,
                'https://www.googleapis.com/auth/drive.readonly',
                'urn:ietf:wg:oauth:2.0:oob',
            )

            self._notice('Go to the following link in your browser: %s',
                         flow.step1_get_authorize_url())
            code = raw_input('Enter verification code: ').strip()
            credentials = flow.step2_exchange(code)

            with open(credentials_file, 'w') as f:
                f.write(credentials.to_json())

        if not credentials:
            raise CommandError('Error load credentials')

        return credentials

    def get_file_content(self, filename):
        mimeType = 'application/vnd.google-apps.spreadsheet'
        exportLinks = 'application/vnd.openxmlformats-officedocument.' \
                      'spreadsheetml.sheet'
        filename = filename.decode('utf8')

        query = 'title = "%s" and mimeType = "%s"' % (filename, mimeType)

        file = self.service.files().list(q=query, maxResults=1).execute()

        if not len(file['items']):
            raise CommandError('Google drive file not found')

        file = file['items'][0]
        download_url = file['exportLinks'][exportLinks]

        response, content = self.service._http.request(download_url)
        if response.status != 200:
            raise CommandError('Downloading file failed')

        return content

    def parse_file(self, filename):
        content = self.get_file_content(filename)

        re_name = re.compile(r'^([^()]+?)\s*\(([\w]+)\)$', re.U)
        re_exists = re.compile(u'^есть.*$', re.U)

        book = xlrd.open_workbook(file_contents=content)
        sheet = book.sheet_by_index(0)

        numbers = []
        for row_index in range(1, sheet.nrows):
            number = sheet.cell(row_index, 1).value.strip()

            if number:
                numbers.append(number)

        issues = CoinIssue.objects \
                          .prefetch_related('issuemint_set__mint_mark') \
                          .prefetch_related('issuemint_set__mint') \
                          .filter(catalog_number__in=numbers)

        for issue in issues:
            numbers.remove(issue.catalog_number)

        for number in numbers:
            self._error('Issue "%s" not found', number)

        issues = dict((issue.catalog_number, issue) for issue in issues)
        marks = {}

        for col_index in range(4, sheet.ncols):
            collection = sheet.cell(0, col_index).value.strip()

            m = re_name.match(collection)
            if not m:
                continue

            collection, created = Collection.objects.get_or_create(
                name=m.group(1))
            if created:
                self._info('Add collection "%s"', collection.name, level=2)

            mark = m.group(2).upper()

            if not mark in marks:
                try:
                    mint_mark = MintMark.objects.get(mark=mark)
                    marks[mark] = mint_mark
                except ObjectDoesNotExist:
                    self._error('Mint mark "%s" not found', mark)
                    continue
            else:
                mint_mark = marks[mark]

            for row_index in range(1, sheet.nrows):
                value = sheet.cell(row_index, col_index).value.strip()
                catalog_number = sheet.cell(row_index, 1).value.strip()

                if (not value or not re_exists.match(value) or
                        not catalog_number in issues):
                    continue

                issue = issues[catalog_number]
                mint_found = False

                for issue_mint in issue.issuemint_set.all():
                    if issue_mint.mint_mark == mint_mark:
                        coin, created = Coin.objects.get_or_create(
                            collection=collection, issue=issue,
                            mint=issue_mint)
                        if created:
                            self._info('Add coin "%s" mint "%s" to "%s"'
                                       ' collection', catalog_number, mark,
                                       collection.name, level=2)

                        mint_found = True
                        break

                if not mint_found:
                    self._error('Mint mark "%s" not exists in coin issue '
                                '"%s"', mark, catalog_number)
