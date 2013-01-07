from django.db.models.fields.files import ImageFieldFile, ImageField

class CoinImageFieldFile(ImageFieldFile):
    def get_url(self, thumb_width = None, thumb_height = None, thumb_format = None):
        if not thumb_width and hasattr(self.field, 'thumb_width') and self.field.thumb_width > 0:
            thumb_width = self.field.thumb_width

        if not thumb_height and hasattr(self.field, 'thumb_height') and self.field.thumb_height > 0:
            thumb_height = self.field.thumb_height

        if not thumb_format and hasattr(self.field, 'thumb_format'):
            thumb_format = self.field.thumb_format

        url = super(CoinImageFieldFile, self)._get_url()

        if thumb_width and thumb_height:
            url = '%s.%dx%d' % (url, thumb_width, thumb_height)

        if thumb_format:
            url = '%s.%s' % (url, self.field.thumb_format)

        return url
    url = property(get_url)

class CoinImageField(ImageField):
    attr_class = CoinImageFieldFile

    def __init__(self, verbose_name=None, name=None, width_field=None,
                 height_field=None, thumb_width=200, thumb_height=200,
                 thumb_format='png', **kwargs):
        from coins.utils.storage import DatabaseStorage

        kwargs['upload_to'] = 'coins'
        kwargs['blank'] = True
        kwargs['null'] = True
        kwargs['storage'] = DatabaseStorage()

        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
        self.thumb_format = thumb_format

        super(CoinImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def generate_filename(self, instance, name):
        return name