import time


from reportlab.platypus import BaseDocTemplate, Paragraph, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class Box():
    def __init__(self, coin):
        self.coin = coin

    def _init_document(self):
        pdfmetrics.registerFont(TTFont('Trebuchet', '/usr/share/fonts/truetype/msttcorefonts/trebuc.ttf'))

        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name      = 'Justify',
            alignment = TA_JUSTIFY,
            fontName  = 'Trebuchet'
        ))

    def draw(self, file):
        self._init_document()

        doc = BaseDocTemplate(file, pagesize = A4,
                              rightMargin = .5*cm,leftMargin = .5*cm,
                              topMargin=.5*cm, bottomMargin=.5*cm, _debug = 1)
        page_width, page_height = landscape(A4)

        elements = [Paragraph(self.coin.issue.name, self.styles.get('Justify'))]


        box = Frame(10, page_height + 10, 10*cm, 11.7*cm, showBoundary=1)


        boxes = [box]

        doc.addPageTemplates(PageTemplate(frames = boxes))

        doc.build(elements)