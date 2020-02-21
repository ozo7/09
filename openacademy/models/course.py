# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, exceptions, fields, models


class Course(models.Model):
    _name = 'oa9.course'
    _description = 'Course'
    _inherit = 'mail.thread'

    name = fields.Char(string='Title', required=True)
    description = fields.Text()

    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible")
    can_edit_responsible = fields.Boolean(compute='_compute_can_edit_responsible')

    session_ids = fields.One2many('oa9.session', 'course_id', string="Sessions")

    level = fields.Selection([('1', 'Easy'), ('2', 'Medium'), ('3', 'Hard')], string="Difficulty Level")
    session_count = fields.Integer(compute="_compute_session_count")
    attendee_count = fields.Integer(compute="_compute_attendee_count")

    fname = fields.Char('Filename')
    datas = fields.Binary('File')
    currency_id = fields.Many2one('res.currency', 'Currency')

    price = fields.Float('Price')

    _sql_constraints = [
        ('name_description_check', 'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique', 'UNIQUE(name)',
         "The course title must be unique"),
    ]

    @api.depends('responsible_id')
    def _compute_can_edit_responsible(self):
        self.can_edit_responsible = self.env.user.has_group('oa9.group_archmaesters')

    # @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    # @api.multi
    def open_attendees(self):
        self.ensure_one()
        attendee_ids = self.session_ids.mapped('attendee_ids')
        return {
            'name':      'Attendees of %s' % (self.name),
            'type':      'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain':    [('id', 'in', attendee_ids.ids)],
        }

    @api.depends('session_ids')
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)

    @api.depends('session_ids.attendees_count')
    def _compute_attendee_count(self):
        for course in self:
            course.attendee_count = len(course.mapped('session_ids.attendee_ids'))


class Session(models.Model):
    _name = 'oa9.session'
    _inherit = ['mail.thread']
    _order = 'name'
    _description = 'Session'

    # Olaf: changing the end date does not trigger any correction in start date or duration! => was corrected

    name = fields.Char(required=True)
    description = fields.Html()
    active = fields.Boolean(default=True)
    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed"), ('done', "Done")], default='draft')
    level = fields.Selection(related='course_id.level', readonly=True)
    responsible_id = fields.Many2one(related='course_id.responsible_id', readonly=True, store=True)

    start_date = fields.Date(default=fields.Date.context_today)
    # Olaf: is calculated, has inverse calculation
    end_date = fields.Date(string='End date', default=fields.Date.context_today, store=True, compute='_get_end_date', inverse='_set_end_date', )
    # Olaf: was not calculated, but editable and was corrected by inverse calculation of end_date. Now putting it to calculate and have a function prevents it from being editable! Now adding an inverse function makes it editable again and corrects it!
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=1, compute='_calc_duration', inverse='_get_end_date')

    instructor_id = fields.Many2one('res.partner', string="Instructor")
    # Olaf: Here the ondelete attribute will fulfill the "clean system" requirement from the exercise.
    course_id = fields.Many2one('oa9.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees", domain="[('is_company', '=', True)]")
    attendees_count = fields.Integer(compute='_get_attendees_count', store=True)
    seats = fields.Integer()
    taken_seats = fields.Float(compute='_compute_taken_seats', store=True)
    percentage_per_day = fields.Integer("%", default=100)

    is_paid = fields.Boolean('Is paid')
    product_id = fields.Many2one('product.template', 'Product')

    def _warning(self, title, message):
        return {'warning': {
            'title':   title,
            'message': message,
        }}

    @api.depends('seats', 'attendee_ids')
    def _compute_taken_seats(self):
        for session in self:
            if not session.seats:
                session.taken_seats = 0.0
            else:
                session.taken_seats = 100.0 * len(session.attendee_ids) / session.seats

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for session in self:
            session.attendees_count = len(session.attendee_ids)

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return self._warning("Incorrect 'seats' value", "The number of available seats may not be negative")
        if self.seats < len(self.attendee_ids):
            return self._warning("Too many attendees", "Increase seats or remove excess attendees")

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for session in self:
            if session.instructor_id and session.instructor_id in session.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")

    @api.depends('start_date', 'duration')
    # Olaf: function configured in end_date field to be computed
    # Olaf: is triggered by losing onFocus
    def _get_end_date(self):
        for session in self:
            if not (session.start_date and session.duration):
                session.end_date = session.start_date
            else:
                # Add duration to start_date, but: Monday + 5 days = Saturday,
                # so subtract one second to get on Friday instead
                start = fields.Datetime.from_string(session.start_date)
                duration = timedelta(days=session.duration, seconds=-1)
                session.end_date = str(start + duration)

    def _set_end_date(self):
    # Olaf: function configured in end_date field to be inverse computed.
    # Olaf: But what does it do? The duration is not the result of any manual change online of neither start nor end date! !! => Danger! The function is triggered by 'Save' and then the result is different from what the user saw!
        for session in self:
            if session.start_date and session.end_date:
                # Compute the difference between dates, but: Friday - Monday = 4
                # days, so add one day to get 5 days instead
                start_date = fields.Datetime.from_string(session.start_date)
                end_date = fields.Datetime.from_string(session.end_date)
                session.duration = (end_date - start_date).days + 1
    
    @api.depends('start_date', 'end_date')
    def _calc_duration(self):
    # Olaf: Alternative to above function to make it work in the front end already. It is configured without making duration computed => does not have effect!
        for session in self:
            if session.start_date and session.end_date:
                # Compute the difference between dates, but: Friday - Monday = 4
                # days, so add one day to get 5 days instead
                start_date = fields.Datetime.from_string(session.start_date)
                end_date = fields.Datetime.from_string(session.end_date)
                session.duration = (end_date - start_date).days + 1

    # @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body="Session %s of the course %s reset to draft" % (rec.name, rec.course_id.name))

    # @api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            rec.message_post(body="Session %s of the course %s confirmed" % (rec.name, rec.course_id.name))

    # @api.multi
    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.message_post(body="Session %s of the course %s done" % (rec.name, rec.course_id.name))

    def _auto_transition(self):
        for rec in self:
            if rec.taken_seats >= 50.0 and rec.state == 'draft':
                rec.action_confirm()

    # @api.multi
    def write(self, vals):
        res = super(Session, self).write(vals)
        for rec in self:
            rec._auto_transition()
        if vals.get('instructor_id'):
            self.message_subscribe([vals['instructor_id']])
        return res

    @api.model
    def create(self, vals):
        res = super(Session, self).create(vals)
        res._auto_transition()
        if vals.get('instructor_id'):
            res.message_subscribe([vals['instructor_id']])
        return res

    # @api.multi
    def create_invoice_teacher(self):
        teacher_invoice = self.env['account.move'].search([
            ('partner_id', '=', self.instructor_id.id)
        ], limit=1)

        if not teacher_invoice:
            teacher_invoice = self.env['account.move'].create({
                'partner_id': self.instructor_id.id,
            })

        # install module accounting and a chart of account to have at least one expense account in your CoA
        ### Olaf: You will find the 'invoices' as journal entries in the Accounting App: Menu: Accounting > Journal Entries
        expense_account = self.env['account.account'].search([('user_type_id', '=', self.env.ref('account.data_account_type_expenses').id)], limit=1)
        self.env['account.move.line'].create({
            'move_id': teacher_invoice.id,
            'product_id': self.product_id.id,
            'price_unit': self.product_id.lst_price,
            'account_id': expense_account.id,
            'name':       'Session',
            'quantity':   1,
        })

        self.write({'is_paid': True})
