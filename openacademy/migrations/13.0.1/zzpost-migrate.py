# -*- coding: utf-8 -*-

from odoo import api, fields, models
from random import randint

# !!! Is not used


def migrate(cr, version):
    try:
        _logger.info('>>> migration start')

        # get 4 random partner and flag them as instructor
        p = env['res.partner']
        pp = p.search([])
        ppIDs = pp.ids  # used to prevent double results in random
        ppSet = set()
        for i in range(1, 4):
            r = randint(1, len(ppIDs))
            ppSet.add(ppIDs[r])
            del ppIDs[r]
        for s in ppSet:
            pp.browse(s).instructor = True

    except:
        # what kind of errors are available in exceptions. ?
        raise exceptions.UserError('!!! error in post-migrate.py'
