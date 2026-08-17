{
    'name': 'GYM App',
    'author': 'Yousef Ibrahim',
    'version': '17.0.0.1.0',
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/renew_wizard.xml',
        'views/base_menu.xml',
        'views/subscriber.xml',
        'views/package.xml',
        'reports/card_sub_report.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ]
    },
    'application': True,
    'license': 'LGPL-3',
}
