"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'coins.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'coins.dashboard.CustomAppIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard

class CustomIndexDashboard(Dashboard):
    def init_with_context(self, context):
        self.children.append(modules.Group(
            title=_('Collection'),
            display='tabs',
            children=[
                modules.AppList(
                    title=_('Coins'),
                    models=(
                        'coins.models.CoinIssue',
                        'coins.models.Coin',
                        'coins.models.Mint',
                        'coins.models.MintMark',
                    )
                ),
                modules.AppList(
                    title=_('Banknotes'),
                    models=(
                        'coins.models.BanknoteIssue',
                        'coins.models.Banknote',
                    )
                ),
                modules.AppList(
                    title=_('Countries & currencies'),
                    models=(
                        'coins.models.Country',
                        'coins.models.Currency',
                    )
                ),
                modules.AppList(
                    title=_('Other'),
                    models=(
                        'coins.models.Collection',
                        'coins.models.Series',
                    )
                ),
                modules.AppList(
                    title=_('Settings'),
                    exclude=(
                        'django.contrib.*',
                        'coins.models.*',
                    ),
                )
            ]
        ))

        self.children.append(modules.LinkList(
            _('Links'),
            children=[
                {
                    'title': _('Commemorative and Investment Coins database'),
                    'url': 'http://cbr.ru/bank-notes_coins/?Prtid=coins_base',
                    'external': True,
                },
                {
                    'title': _('Collection list in google docs'),
                    'url': 'https://docs.google.com/a/kihamo.ru/spreadsheet/ccc?key=0AlUZ0Eqd4UJwdEZRTHVWMVFCcW5TX0JqSGh2ZGptS1E&usp=sharing',
                    'external': True,
                }
            ]
        ))

        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',),
        ))

        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5
        ))

class CustomAppIndexDashboard(AppIndexDashboard):
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        self.children += [
            modules.Group(
                title=_('Collection'),
                display='tabs',
                children=[
                    modules.AppList(
                        title=_('Coins'),
                        models=(
                            'coins.models.CoinIssue',
                            'coins.models.Coin',
                            'coins.models.Mint',
                            'coins.models.MintMark',
                        )
                    ),
                    modules.AppList(
                        title=_('Banknotes'),
                        models=(
                            'coins.models.BanknoteIssue',
                            'coins.models.Banknote',
                        )
                    ),
                    modules.AppList(
                        title=_('Countries & currencies'),
                        models=(
                            'coins.models.Country',
                            'coins.models.Currency',
                        )
                    ),
                    modules.AppList(
                        title=_('Other'),
                        models=(
                            'coins.models.Collection',
                            'coins.models.Series',
                        )
                    )
                ]
            ),
            modules.LinkList(
                _('Links'),
                children=[
                    {
                        'title': _('Commemorative and Investment Coins database'),
                        'url': 'http://cbr.ru/bank-notes_coins/?Prtid=coins_base',
                        'external': True,
                    },
                    {
                        'title': _('Collection list in google docs'),
                        'url': 'https://docs.google.com/a/kihamo.ru/spreadsheet/ccc?key=0AlUZ0Eqd4UJwdEZRTHVWMVFCcW5TX0JqSGh2ZGptS1E&usp=sharing',
                        'external': True,
                    }
                ]
            ),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        return super(CustomAppIndexDashboard, self).init_with_context(context)
