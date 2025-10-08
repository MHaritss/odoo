from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError

try:
    from num2words import num2words
except ImportError:  # pragma: no cover - library shipped with Odoo, fallback for safety
    num2words = None


class SmkInvoice(models.Model):
    _name = 'smk.invoice'
    _description = 'Tagihan Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nomor Tagihan', required=True, copy=False, readonly=True, default='New')
    student_id = fields.Many2one('smk.siswa', string='Siswa', required=True, tracking=True)
    teacher_ids = fields.Many2many('smk.guru', string='Guru Pengajar', related='student_id.teacher_ids', readonly=True)
    kelas_id = fields.Many2one('smk.kelas', string='Kelas Utama', related='student_id.kelas_id', store=True, readonly=True)
    date_invoice = fields.Date(string='Tanggal Tagihan', default=fields.Date.context_today, tracking=True)
    amount = fields.Monetary(string='Jumlah (IDR)', currency_field='currency_id', required=True, tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Mata Uang',
        default=lambda self: self._default_currency_id(),
        required=True,
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
    ], default='draft', tracking=True)
    description = fields.Text(string='Keterangan')

    @api.model
    @api.model
    def _get_idr_currency(self):
        currency = self.env.ref('base.IDR', raise_if_not_found=False)
        if not currency:
            currency = self.env['res.currency'].search([('name', '=', 'IDR')], limit=1)
        if not currency:
            raise UserError('Currency IDR belum tersedia. Silakan aktifkan mata uang IDR terlebih dahulu.')
        return currency

    @api.model
    def _default_currency_id(self):
        return self._get_idr_currency().id

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('smk.invoice') or 'New'
        vals['currency_id'] = self._default_currency_id()
        return super().create(vals)

    def write(self, vals):
        if 'currency_id' in vals:
            vals['currency_id'] = self._default_currency_id()
        return super().write(vals)

    def action_mark_paid(self):
        for invoice in self:
            invoice.state = 'paid'
        return True

    def action_print_kwitansi(self):
        if any(invoice.state != 'paid' for invoice in self):
            raise UserError('Kwitansi hanya dapat dicetak jika status tagihan Paid.')
        return self.env.ref('smk_karanganyar.report_smk_kwitansi').report_action(self)

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
                'currency_id': self._default_currency_id(),
            })

    def _amount_to_text_id(self):
        self.ensure_one()
        if num2words is None:
            return ''
        currency = self.currency_id or self._get_idr_currency()
        decimals = currency.decimal_places or 0
        formatted = f"%0.{decimals}f" % self.amount
        integer_part, _, fractional_part = formatted.partition('.')
        integer_value = int(integer_part or 0)
        fractional_value = int(fractional_part or 0)

        def _num2words(number):
            try:
                return num2words(number, lang='id').title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        unit = currency.currency_unit_label or 'Rupiah'
        subunit = currency.currency_subunit_label or 'Sen'
        words = f"{_num2words(integer_value)} {unit}".strip()
        if not currency.is_zero(self.amount - float(integer_value)) and fractional_value:
            words = f"{words} dan {_num2words(fractional_value)} {subunit}"
        return words
