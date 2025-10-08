from odoo import api, fields, models


class SmkGuru(models.Model):
    _name = 'smk.guru'
    _description = 'Guru'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', required=True, tracking=True)
    address = fields.Text(string='Alamat')
    phone = fields.Char(string='Nomor Telepon', required=True, tracking=True)
    kelas_ids = fields.One2many('smk.kelas', 'guru_id', string='Kelas')
    siswa_ids = fields.One2many('smk.siswa', 'guru_id', string='Siswa')
    student_count = fields.Integer(
        string='Jumlah Siswa',
        compute='_compute_student_count',
        store=True,
        compute_sudo=True,
    )

    _sql_constraints = [
        ('unique_phone', 'unique(phone)', 'Nomor telepon guru harus unik.'),
    ]

    @api.depends('siswa_ids.active')
    def _compute_student_count(self):
        for guru in self:
            guru.student_count = len(guru.siswa_ids.filtered(lambda s: s.active))

    def action_activate_students(self):
        self.ensure_one()
        self.siswa_ids.write({'active': True})
        return True

    def action_deactivate_students(self):
        self.ensure_one()
        self.siswa_ids.write({'active': False})
        return True
