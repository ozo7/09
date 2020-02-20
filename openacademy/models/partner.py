# -*- coding: utf-8 -*-, api
from odoo import api, fields, models
from random import randint

# Olaf
levelcast = ('zero', 'easy', 'medium', 'hard')

class Partner(models.Model):
    _inherit = 'res.partner'

    instructor = fields.Boolean(default=False)
    session_ids = fields.Many2many('openacademy.session', string="Attended Sessions", readonly=True)

    level = fields.Char(compute="_get_level", string="Level", store=True)

    zzinfo = fields.Char(string="Info ===> ")
    count = fields.Integer(default=0)    

    @api.depends('category_id', 'category_id.name')
    def _get_level(self):
        for partner in self:
            level = []
            # Olaf: What is category_id ? This is not defined here?
            for categ in partner.category_id:
                if "Chain Level" in categ.name:
                    level.append(int(categ.name.split(' ')[-1]))
            # Olaf changed
            partner.level = levelcast[max(level)] if level else 0
    
    def clicking(self):        
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
        



