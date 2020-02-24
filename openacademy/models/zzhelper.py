# -*- coding: utf-8 -*-, api
from odoo import api, fields, models
from random import randint

class zzHelper(models.TransientModel):
    # Olaf: model name must not have capital letters
    _name = 'oa9.zzhelper'
    _description = 'this model holds functions for the whole application that are supposed to be accessible from anywhere, for example it is used in one of the xml file that load a function'
    # _log_access = False # Olaf: Transient Models need this.

    zzinfo = fields.Char(string="Info", default=">>> ...")

    def button_clearInstructors(self):
        p = self.env['res.partner']
        pp = p.search([])
        for ppp in pp:
            if ppp.instructor:
               ppp.instructor = False
        self.zzinfo = "cleared"
        return True

    # Olaf: we cannot call a function decorated by @api.model from a button, so we need to have this workaround instead:
    def button_flag4randomInstructors(self):
        self.flag4randomInstructors()
        # it needs to return something
        return True


    # Olaf: We need this @api.model urgently to make the method accessible from the xml, for example
    # Olaf: we can make the method private with a leading _ but then it cannot be called anymore from the button.
    @api.model
    def flag4randomInstructors(self):
            # get 4 random partner and flag them as instructor
            p = self.env['res.partner']
            pp = p.search([])
            ppIDs = pp.ids # used to prevent double results in random
            ppSet = set()
            for i in range(4):
                r = randint(0,len(ppIDs)-1)
                ppSet.add(ppIDs[r])
                del ppIDs[r]
            for s in ppSet:
                pp.browse(s).instructor = True
            self.zzinfo = str(ppSet)

