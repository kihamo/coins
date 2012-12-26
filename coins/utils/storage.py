# from django.core.files.storage import Storage

from database_storage import DatabaseStorage as DS
from coins.models import Image

class DatabaseStorage(DS):
    def __init__(self):
        options = {
            'table': Image._meta.db_table,
            'base_url': '/coins/image/'
        }

        super(DatabaseStorage, self).__init__(options)

