# -*- coding: utf-8 -*-
{
    'name': 'OT Management',

    'version': '1.0',

    'summary': 'OT',

    'category': 'Tools',

    'author': 'Tuan Hung',

    'depends': ['base', 'hr', 'project', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        'views/ot.xml',
        'data/mail_template.xml'
    ],

    'images': [],

    'installable': True,

    'application': False,

    'auto_install': False,
}