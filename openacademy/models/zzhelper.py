# -*- coding: utf-8 -*-, api
from odoo import api, fields, models
from random import randint

class zzHelper(models.Model):
    # Olaf: model name must not have capital letters
    _name = 'oa9.zzhelper'
    _description = 'this model holds functions for the whole application that are supposed to be accessible from anywhere, for example it is used in one of the xml file that load a function'

    # Olaf: We need this urgently to make the method accessible from the xml, for example
    @api.model
    def _flag4randomInstructors(self):        
            # get 4 random partner and flag them as instructor
            p = self.env['res.partner']
            pp = p.search([])
            ppIDs = pp.ids # used to prevent double results in random
            ppSet = set()
            for i in range(1,4):
                r = randint(1,len(ppIDs))
                ppSet.add(ppIDs[r])
                del ppIDs[r]
            for s in ppSet:
                pp.browse(s).instructor = True

