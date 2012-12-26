from django.http import HttpResponse
from django.http import Http404

from models import Coin

from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import createBarcodeDrawing

from coins.utils.storage import DatabaseStorage

# http://obroll.com/install-python-pil-python-image-library-on-ubuntu-11-10-oneiric/
def image_view(request, filename, format='jpg', width=None, height=None):
    file = DatabaseStorage().open(filename, 'rb')
    if not file:
        raise Http404

    image = ImageReader(file)

    print image

    if format == 'jpeg':
        format = 'jpg'

    response = HttpResponse(mimetype = 'image/%s' % format)

    #content_type, content_encoding = mimetypes.guess_type(filename)
    #thumb = Image.open(image_file)
    #if

    #if width and height:
    #    thumb = Image.open(image_file)
    #    thumb.thumbnail((int(width), int(height)), Image.ANTIALIAS)
    #    thumb.save(response, 'PNG')
    #else:
    #    response.content = image_file.read()

    return response

def barcode_view(request, coin_id, barcode_format, image_format):
    try:
        coin = Coin.objects.get(pk = coin_id)
    except Coin.DoesNotExist:
        raise Http404

    if image_format == 'jpeg':
        image_format = 'jpg'

    if barcode_format == 'qr':
        barcode = createBarcodeDrawing(
            'QR',
            value = coin.qr_code,
            barHeight = 90,
            barWidth = 90,
            barBorder = 0
        )
    else:
        barcode = createBarcodeDrawing(
            'Code128',
            value = str(coin.barcode),
            barWidth = 1
        )

    return HttpResponse(
        content = barcode.asString(image_format),
        mimetype = 'image/%s' % image_format
    )

def box_list(request):

    return HttpResponse()