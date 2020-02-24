# -*- coding: utf-8 -*-, api
from odoo import api, fields, models
from random import randint


class zzHelper(models.TransientModel):
    # Olaf: model name must not have capital letters
    _name = 'library.zzhelper'
    _description = 'helper functions'
    # _log_access = False # Olaf: Transient Models need this.

    roles = ("author", "publisher", "customer")

    def get_all_partners(self):
        p = self.env['res.partner']
        pp = p.search([])
        return pp

    def clear_roles(self, roles):
        pp = self.get_all_partners()
        for role in roles:
            for ppp in pp:
                if getattr(ppp, role):
                    setattr(ppp, role, False)
        return True

    @api.model
    def flag_roles(self, roles):
        pp = self.get_all_partners()
        for role in roles:
            ppIDs = pp.ids  # used to prevent double results in random
            ppSet = set()
            for i in range(7):
                r = randint(0, len(ppIDs)-1)
                ppSet.add(ppIDs[r])
                del ppIDs[r]
            for s in ppSet:
                partner = pp.browse(s)
                setattr(partner, role, True)

    # Olaf: why is the parameter set by integer 3?!
    # So we explicitly prioritize the ffroles from the frontend
    @api.model
    def clear_flag_roles(self, roles):
        ffroles = self._context.get('ffroles', [])
        if ffroles:
            roles = ffroles
        self.clear_roles(roles)
        self.flag_roles(roles)
        return True
