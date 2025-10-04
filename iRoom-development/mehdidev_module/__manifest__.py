{
    'name': 'MehdiDev23 Custom JavaScript and CSS Module',
    'summary': 'Module to add custom JavaScript and CSS',
    'description': 'This module adds custom JavaScript and CSS',
    'category': 'Website',
    'author': 'MehdiDev23',
    'depends' : ['web', 'website'],
    'assets': {
        'web.assets_frontend': [
            '/mehdidev_module/static/src/css/reset.css',
            '/mehdidev_module/static/src/css/plugins.css',
            '/mehdidev_module/static/src/css/style.css',
            '/mehdidev_module/static/src/css/color.css',
            '/mehdidev_module/static/src/js/plugins.js',
            '/mehdidev_module/static/src/js/scripts.js',
        ],
        'web.assets_backend': [
            '/mehdidev_module/static/src/css/bootstrap-extended.css',
            '/mehdidev_module/static/src/css/components.css',
            '/mehdidev_module/static/src/css/backend-style.css',
        ]
    },
    'installable': True,
    'license': 'LGPL-3',
}
