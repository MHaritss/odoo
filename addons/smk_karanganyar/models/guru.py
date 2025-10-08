from odoo import api, fields, models


class SmkGuru(models.Model):
    _name = 'smk.guru'
    _description = 'Guru'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', required=True, tracking=True)
    address = fields.Text(string='Alamat')
    phone = fields.Char(string='Nomor Telepon', required=True, tracking=True)
    kelas_ids = fields.One2many('smk.kelas', 'guru_id', string='Kelas Diampu')
    siswa_ids = fields.One2many('smk.siswa', 'guru_id', string='Siswa Wali')
    teaching_student_ids = fields.Many2many(
        'smk.siswa',
        'smk_guru_student_rel',
        'guru_id',
        'siswa_id',
        string='Siswa Diajar',
    )
    student_count = fields.Integer(
        string='Jumlah Siswa',
        compute='_compute_student_count',
        store=True,
        compute_sudo=True,
    )

    _sql_constraints = [
        ('unique_phone', 'unique(phone)', 'Nomor telepon guru harus unik.'),
    ]

    @api.depends('kelas_ids.siswa_ids.active', 'teaching_student_ids.active')
    def _compute_student_count(self):
        for guru in self:
            students = (guru.kelas_ids.mapped('siswa_ids') | guru.teaching_student_ids).filtered(lambda s: s.active)
            guru.student_count = len(set(students.ids))

    def action_activate_students(self):
        self.ensure_one()
        students = self.kelas_ids.mapped('siswa_ids') | self.teaching_student_ids
        students.write({'active': True})
        return True

    def action_deactivate_students(self):
        self.ensure_one()
        students = self.kelas_ids.mapped('siswa_ids') | self.teaching_student_ids
        students.write({'active': False})
        return True
