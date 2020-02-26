# -*- coding: utf-8 -*-
from odoo import models, fields

# Olaf: For what is this?
class Editor(models.Model):
    _name = 'library.publisher'
    _description = 'Publisher'

    name = fields.Char()
