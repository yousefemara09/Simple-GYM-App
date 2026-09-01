{
    'name': 'GYM App',
    'author': 'Yousef Ibrahim',
    'version': '17.0.0.1.0',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/renew_wizard.xml',
        'views/base_menu.xml',
        'views/subscriber.xml',
        'views/package.xml',
        'views/client_actions.xml',
        'reports/card_sub_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'gym_app/static/src/css/gym_app.css',
            'gym_app/static/src/js/form_view/subscriber_card.js',
            'gym_app/static/src/js/form_view/subscriber_card.xml',
            'gym_app/static/src/js/subscriber_gym/subscriber_gym.js',
            'gym_app/static/src/js/subscriber_gym/subscriber_gym.xml',
            'gym_app/static/src/js/gym_dashboard/gym_dashboard.js',
            'gym_app/static/src/js/gym_dashboard/gym_dashboard.xml',
        ]
    },
    'application': True,
    'license': 'LGPL-3',
}
