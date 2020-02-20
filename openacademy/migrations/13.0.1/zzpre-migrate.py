# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    try:
        _logger.info('>>> migration start')

         # clear partner from being an instructor
        p = env['res.partner']
        pp = p.search([])
        for ppp in pp:
            ppp.browse(s).instructor = False

    except:
        # what kind of errors are available in exceptions. ?
        raise exceptions.UserError('!!! error in pre-migrate.py')