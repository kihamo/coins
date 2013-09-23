from defaults import *

DATABASES['default']['NAME'] = os.path.join(
    ROOT_PATH, 'db', 'coins_development.db'
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE_CLASSES
TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
INSTALLED_APPS += ('debug_toolbar',)
