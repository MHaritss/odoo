from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError


class SmkInvoice(models.Model):
    _name = 'smk.invoice'
    _description = 'Tagihan Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nomor Tagihan', required=True, copy=False, readonly=True, default='New')
    student_id = fields.Many2one('smk.siswa', string='Siswa', required=True, tracking=True)
    guru_id = fields.Many2one('smk.guru', string='Guru', related='student_id.guru_id', store=True)
    kelas_id = fields.Many2one('smk.kelas', string='Kelas', related='student_id.kelas_id', store=True)
    date_invoice = fields.Date(string='Tanggal Tagihan', default=fields.Date.context_today, tracking=True)
    amount = fields.Monetary(string='Jumlah', currency_field='currency_id', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
    ], default='draft', tracking=True)
    description = fields.Text(string='Keterangan')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('smk.invoice') or 'New'
        return super().create(vals)

    def action_mark_paid(self):
        for invoice in self:
            invoice.state = 'paid'
        return True

    def action_print_kwitansi(self):
        if any(invoice.state != 'paid' for invoice in self):
            raise UserError('Kwitansi hanya dapat dicetak jika status tagihan Paid.')
        return self.env.ref('SMK-Karangayar.report_smk_kwitansi').report_action(self)

    @api.model
    def cron_create_monthly_invoice(self):
        today = fields.Date.context_today(self)
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1)
        else:
            end_date = date(today.year, today.month + 1, 1)

        for student in self.env['smk.siswa'].sudo().search([('active', '=', True)]):
            exists = self.search_count([
                ('student_id', '=', student.id),
                ('date_invoice', '>=', start_date),
                ('date_invoice', '<', end_date),
            ])
            if exists:
                continue
            self.create({
                'student_id': student.id,
                'amount': 0.0,
                'description': 'Tagihan bulanan otomatis',
                'date_invoice': today,
            })
