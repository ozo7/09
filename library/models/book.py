# -*- coding: utf-8 -*-
from odoo import models, fields, api
import re


class Books(models.Model):
    _inherit = 'product.product'

    # Olaf: ?? book title as name inherited from product
    # Olaf: R3 - only author-defined partners
    author_ids = fields.Many2many(
        "res.partner", string="Authors", domain=[('author', '=', True)])
    edition_date = fields.Date()
    isbn = fields.Char(string='ISBN', unique=True)
    publisher_id = fields.Many2one('res.partner', string='Publisher', domain=[
                                   ('publisher', '=', True)])
    copy_ids = fields.One2many('library.copy', 'book_id', string="Book Copies")
    book = fields.Boolean(string='Is a Book', default=False)


class BookCopy(models.Model):
    _name = 'library.copy'
    _description = 'Book Copy'
    # _rec_name is difficult to use for clean name, using name_get()
    # Olaf: R9 - display name needs to be configured, _res_name or name_get()

    # Olaf: Delegation - 'has-a-relationship'
    book_id = fields.Many2one('product.product', string="Book", domain=[(
        'book', "=", True)], required=True, ondelete="cascade", delegate=True)
    # Olaf: unique copy reference
    reference = fields.Char(required=True, string="Ref")
    # Olaf: the leases link here
    rental_ids = fields.One2many('library.rental', 'copy_id', string='Rentals')
    book_state = fields.Selection(
        [('available', 'Available'), ('rented', 'Rented'), ('lost', 'Lost')], default="available")
    readers_count = fields.Integer(compute="_compute_readers_count")

    def clean_string_display(self):
        return "something"

    # @api.multi
    def open_readers(self):
        self.ensure_one()
        reader_ids = self.rental_ids.mapped('customer_id')
        return {
            'name':      'Readers of %s' % (self.name),
            'type':      'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain':    [('id', 'in', reader_ids.ids)],
            'target':    'new',
        }

    @api.depends('rental_ids.customer_id')
    def _compute_readers_count(self):
        for book in self:
            book.readers_count = len(book.mapped('rental_ids'))

    # Olaf: using name function to create a display name that Odoo accepts
    def name_get(self):
        response = []
        for rec in self:
            unclean_name = rec.book_id.name + " -- " + rec.reference
            clean_name = re.sub('[^a-zA-Z0-9 \.-]+', '_',unclean_name)
            clean_name = re.sub(' +', '-', clean_name)
            clean_name = re.sub('--+', '--', clean_name)
            response.append([rec.id, clean_name])
        return response


class Wizard(models.TransientModel):
    _name = 'library.wizard'
    _description = 'Wizard to add attendees to a session'

    @api.model
    def default_get(self, fields):
        res = super(Wizard, self).default_get(fields)
        res.update({'copy_ids': [(6, 0, self._context.get('active_ids', []))]})
        return res

    copy_ids = fields.Many2many(
        'library.copy', string="Book copies", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer")
    rental_ids = fields.Many2many('library.rental')
    return_date = fields.Date()

    @api.model
    def create(self, vals):
        res = super(Wizard, self).create(vals)
        return res

    # @api.multi
    def next_step(self):
        for copy in self.copy_ids:
            copy.rental_ids |= self.env['library.rental'].create(
                {'copy_id': copy.id, 'customer_id': self.customer_id.id, 'return_date': self.return_date})
        return {
            'name':      'Rentals of %s' % (self.customer_id.name),
            'type':      'ir.actions.act_window',
            'res_model': 'library.rental',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain':    [('state', '=', "draft"), ('customer_id', "=", self.customer_id.id)],
            'target':    'self',
        }
