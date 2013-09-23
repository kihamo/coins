from django.core.urlresolvers import reverse
from django.core.files.images import ImageFile
from database_storage import DatabaseStorage as DS

from coins.models import Image

from StringIO import StringIO
from base64 import b64encode, b64decode
from hashlib import md5
from mimetypes import guess_type


class DatabaseStorage(DS):
    def __init__(self):
        options = {
            'table': Image._meta.db_table,
            'base_url': ''
        }

        super(DatabaseStorage, self).__init__(options)

    def _open(self, name, mode='rb'):
        assert mode == 'rb', "DatabaseStorage open mode must be 'rb'."

        try:
            object = Image.objects.get(pk=name)
        except Image.DoesNotExist:
            return None

        inMemFile = StringIO(b64decode(object.data))
        inMemFile.name = object.filename
        inMemFile.mode = mode

        return ImageFile(inMemFile)

    def _save(self, name, content):
        binary = content.read()
        hash = md5(binary).hexdigest()

        try:
            object = Image.objects.get(pk=hash)
        except Image.DoesNotExist:
            object = Image(
                pk=hash,
                filename=name.replace('\\', '/'),
                size=len(binary),
                data=b64encode(binary),
                mime_type=guess_type(name)[0]
            )
            object.save()

        return object.pk

    def url(self, name):
        return reverse('show-image', args=[name])
