from django.contrib.admin.widgets import AdminFileWidget

from django.utils.safestring import mark_safe
from django.utils.html import escape

class AdminImageFileWidget(AdminFileWidget):
    template_with_initial= u'%(initial_text)s: %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'

    def render(self, name, value, attrs=None):
        result = super(AdminImageFileWidget, self).render(name, value, attrs)

        if value and hasattr(value, 'url'):
            result = '<img src="%s" border="0" alt="%s" /><br /> %s' % (
                escape(value.url),
                value,
                result
            )

        return mark_safe('<p class="file-upload">%s</p>' % result)