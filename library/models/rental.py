# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta

# Olaf: The fee logic is implemented on the button actions. When clicked, producing as a result a library.payment object per customer and click.
class Rentals(models.Model):
    _name = 'library.rental'
    _description = 'Book rental'
    _order = "rental_date desc,return_date_planned desc"

    customer_id = fields.Many2one('res.partner', string='Customer', domain=[
                                  ('customer', '=', True)], required=True)
    copy_id = fields.Many2one('library.copy', string="Book Copy", domain=[
                              ('book_state', '=', 'available')], required=True)
    book_id = fields.Many2one('product.product', string='Book', domain=[
                              ('book', '=', True)], related='copy_id.book_id', readonly=True)
    rental_date = fields.Date(default=fields.Date.context_today, required=True)
    return_date_planned = fields.Date(default=datetime.now().date() + timedelta(days=22), required=True, string="Planned Return Date")
    return_date_actual = fields.Date(string="Actual Return Date")

    # Olaf: history of rentals will be provided
    state = fields.Selection([
        ('draft', 'Draft'),
        ('rented', 'Rented'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
        ], default="draft")

    # @api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'rented'
            rec.copy_id.book_state = 'rented'
            rec.add_fee('time')

    # @api.multi
    def add_fee(self, type):
        for rec in self:
            if type == 'time':
                price_id = self.env.ref('library.price_rent')
                delta_dates = fields.Date.from_string(
                    rec.return_date_planned) - fields.Date.from_string(rec.rental_date)
                amount = delta_dates.days * price_id.price / price_id.duration
            elif type == 'loss':
                price_id = self.env.ref('library.price_loss')
                amount = price_id.price
            else:
                return

            self.env['library.payment'].create({
                'customer_id': rec.customer_id.id,
                'date':        rec.rental_date,
                'amount': - amount,
            })

    # @api.multi
    def action_return(self):
        for rec in self:
            rec.state = 'returned'
            rec.copy_id.book_state = 'available'

    # @api.multi
    def action_lost(self):
        for rec in self:
            rec.state = 'lost'
            rec.copy_id.book_state = 'lost'
            rec.copy_id.active = False
            rec.add_fee('loss')

    # Olaf: this is the code referenced in the cron action
    @api.model
    def _cron_check_date(self):
        late_rentals = self.search([
            ('state', '=', 'rented'),
            ('return_date_planned', '<', fields.Date.today())
            ])
        # Olaf: Mark the late leases as overdue:
        # Mark overdue and produce reminder email
        template_id = self.env.ref('library.mail_template_book_return')
        for latie in late_rentals:
            latie.state = 'overdue'
            mail_id = template_id.send_mail(latie.id)
