from odoo import api, fields, models


class SmkGuru(models.Model):
    _name = 'smk.guru'
    _description = 'Guru'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', required=True, tracking=True)
    address = fields.Text(string='Alamat')
    phone = fields.Char(string='Nomor Telepon', required=True, tracking=True)
    kelas_ids = fields.Many2many(
        'smk.kelas',
        'smk_guru_kelas_rel',
        'guru_id',
        'kelas_id',
        string='Kelas Diampu',
    )
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

    @api.depends('kelas_ids', 'kelas_ids.siswa_ids', 'kelas_ids.siswa_ids.active', 'teaching_student_ids', 'teaching_student_ids.active')
    def _compute_student_count(self):
        for guru in self:
            students = guru._gather_students(include_inactive=True).filtered(lambda s: s.active)
            guru.student_count = len(set(students.ids))

    def action_activate_students(self):
        self.ensure_one()
        students = self._gather_students(include_inactive=True)
        students.write({'active': True})
        return True

    def action_deactivate_students(self):
        self.ensure_one()
        students = self._gather_students(include_inactive=True)
        students.write({'active': False})
        return True

    def action_print_teacher_report(self):
        gurus = self.env['smk.guru'].sudo().search([])
        return self.env.ref('smk_karanganyar.report_smk_guru').report_action(gurus)

    def _gather_students(self, include_inactive=False):
        self.ensure_one()
        guru = self.with_context(active_test=False) if include_inactive else self
        students = guru.kelas_ids.mapped('siswa_ids') | guru.teaching_student_ids
        if not include_inactive:
            students = students.filtered(lambda s: s.active)
        return students
