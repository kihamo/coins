import os

from reportlab.platypus import BaseDocTemplate, Paragraph, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class Box():
    width = 10*cm
    height = 11.7*cm

    def __init__(self, coin):
        self.coin = coin

    def _init_document(self):
        font_file = os.path.abspath(os.path.dirname(__file__) + '/../data') + '/trebuc.ttf'
        pdfmetrics.registerFont(TTFont('Trebuchet', font_file))

        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name      = 'Justify',
            alignment = TA_JUSTIFY,
            fontName  = 'Trebuchet'
        ))

    def draw(self, file):
        self._init_document()

        doc = BaseDocTemplate(
            file,
            pagesize = A4,
            title = 'Boxes',
            showBoundary = 1
        )

        page_width, page_height = doc.pagesize

        box_params = {
            'width': self.width,
            'height': self.height,
            'showBoundary': 1
        }

        box1_params =  {
            'x1': .5 * cm,
            'y1': page_height - self.height - .5 * cm
        }

        box2_params =  {
            'x1': .5 * cm,
            'y1': page_height - (self.height - .5 * cm) * 2
        }

        box1_params.update(box_params)
        box2_params.update(box_params)

        box1_frame = Frame(**box1_params)
        box2_frame = Frame(**box2_params)

        doc.addPageTemplates(PageTemplate(frames = box1_frame))
        doc.addPageTemplates(PageTemplate(frames = box2_frame))


        elements = [Paragraph(self.coin.issue.name, self.styles.get('Justify'))]
        doc.build(elements)