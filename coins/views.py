from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404

from rest_framework import generics
from serializers import MintSerializer

from models import Coin, Mint
from django.db.models.loading import get_model

from PIL import Image
from reportlab.graphics.barcode import createBarcodeDrawing

from coins.utils.box import Box

from coins.utils.storage import DatabaseStorage

# http://obroll.com/install-python-pil-python-image-library-on-ubuntu-11-10-oneiric/
def image(request, filename, width=None, height=None, image_format='png'):
    file = DatabaseStorage().open(filename, 'rb')
    if not file:
        raise Http404

    if not image_format or image_format.upper() not in ('PNG', 'JPEG', 'JPG', 'GIF'):
        image_format = 'PNG'
    else:
        image_format = image_format.upper()

        if image_format == 'JPG':
            image_format = 'JPEG'

    thumb = Image.open(file)

    if thumb.format == 'PNG' and image_format != thumb.format:
        imageWhiteBg = Image.new('RGB', thumb.size, (255,255,255))
        imageWhiteBg.paste(thumb, thumb)
        thumb = imageWhiteBg

    if width and height:
        thumb.thumbnail((int(width), int(height)), Image.ANTIALIAS)

    response = HttpResponse(mimetype = Image.MIME[image_format])
    thumb.save(response, image_format)

    return response

def barcode(request, model_name, coin_id, barcode_format='code128', image_format='png'):
    try:
        model = get_model(Coin._meta.app_label, model_name[0].upper() + model_name[1:].lower())
        model = model.objects.get(pk = coin_id)
    except Coin.DoesNotExist:
        raise Http404

    if image_format == 'jpeg':
        image_format = 'jpg'
    elif image_format not in ('png', 'jpg', 'gif'):
        image_format = 'png'

    if barcode_format == 'qr':
        barcode = createBarcodeDrawing(
            'QR',
            value = model.qr_code,
            barHeight = 90,
            barWidth = 90,
            barBorder = 0
        )
    else:
        barcode = createBarcodeDrawing(
            'Code128',
            value = str(model.barcode),
            barWidth = 1,
            quiet = False
        )

    return HttpResponse(
        content = barcode.asString(image_format),
        mimetype = 'image/%s' % image_format
    )

def box(request, coin_id, view_format = 'html'):
    try:
        coin = Coin.objects.get(pk = coin_id)
    except Coin.DoesNotExist:
        raise Http404

    if view_format not in ('html', 'pdf'):
        view_format = 'html'

    if view_format == 'html':
        return render_to_response('box.html', {'coin': coin})

    response = HttpResponse(mimetype='application/pdf')

    box = Box(coin)
    box.draw(response)

    return response

class MintList(generics.ListAPIView):
    queryset = Mint.objects.select_related('country').prefetch_related('marks')
    serializer_class = MintSerializer