# -*- coding: utf-8 -*-, api
from odoo import api, fields, models
from random import randint

class zzHelper(models.TransientModel):
    # Olaf: model name must not have capital letters
    _name = 'library.zzhelper'
    _description = 'helper functions'
    # _log_access = False # Olaf: Transient Models need this.

    roles = ("author", "publisher", "customer")

    def getallPartners(self):
        p = self.env['res.partner']
        pp = p.search([])
        return pp

    def clearRoles(self, roles):
        pp = self.getallPartners()
        for role in roles:
            for ppp in pp:
                if getattr(ppp,role):
                    setattr(ppp, role, False)
        return True

    @api.model
    def flagRoles(self, roles):               
        pp = self.getallPartners()
        for role in roles:
            ppIDs = pp.ids # used to prevent double results in random
            ppSet = set()
            for i in range(7):
                r = randint(0,len(ppIDs)-1)
                ppSet.add(ppIDs[r])
                del ppIDs[r]
            for s in ppSet:
                partner = pp.browse(s)
                setattr(partner, role, True)
    
    # Olaf: why is the parameter set by integer 3?!
    # So we explicitly prioritize the ffroles from the frontend
    @api.model
    def clearNflagRoles(self, roles):
        import pdb
        pdb.set_trace()
        ffroles = self._context.get('ffroles', [])
        if ffroles:
            roles = ffroles       
        self.clearRoles(roles)
        self.flagRoles(roles)
        return True

        

