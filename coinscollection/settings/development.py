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
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.profiling.ProfilingDebugPanel',
)

LOGGING['handlers']['console'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler'
}

LOGGING['loggers'][''] = {
    'level': 'DEBUG',
    'handlers': ['console']
}
