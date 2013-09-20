from defaults import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
INSTALLED_APPS += ('debug_toolbar',)