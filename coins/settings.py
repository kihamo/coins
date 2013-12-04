from django.utils.translation import ugettext_lazy as _

CONSTANCE_CONFIG = {
    'DEFAULT_ISSUE_COUNTRY': ('RUS', _('Default issue country')),
    'DEFAULT_ISSUE_CURRENCY': ('RUB', _('Default issue currency')),
    'API_TOKEN_LIFETIME': (1440, _('Api token lifetime (in minutes)')),
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.UnicodeJSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'coins.api.authentication.TokenAuthentication',
    )
}

CORS_ORIGIN_ALLOW_ALL = True
