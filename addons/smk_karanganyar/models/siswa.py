from odoo import api, fields, models


class SmkSiswa(models.Model):
    _name = 'smk.siswa'
    _description = 'Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', required=True, tracking=True)
    nis = fields.Char(string='NIS', tracking=True)
    kelas_id = fields.Many2one('smk.kelas', string='Kelas Utama', tracking=True, required=True)
    kelas_ids = fields.Many2many(
        'smk.kelas',
        'smk_siswa_kelas_rel',
        'siswa_id',
        'kelas_id',
        string='Kelas Diikuti',
        tracking=True,
        help='Daftar kelas yang saat ini diikuti siswa.',
    )
    teacher_ids = fields.Many2many(
        'smk.guru',
        'smk_guru_student_rel',
        'siswa_id',
        'guru_id',
        string='Guru Pengajar',
    )
    phone = fields.Char(string='Nomor Telepon Wali')
    address = fields.Text(string='Alamat')
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('unique_nis', 'unique(nis)', 'NIS harus unik untuk setiap siswa.'),
    ]

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._sync_kelas_selection()
        return record

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('skip_kelas_sync') and ('kelas_id' in vals or 'kelas_ids' in vals):
            self._sync_kelas_selection()
        return res

    def _sync_kelas_selection(self):
        if self.env.context.get('skip_kelas_sync'):
            return
        for student in self:
            kelas = student.kelas_id
            if kelas:
                if kelas not in student.kelas_ids:
                    student.with_context(skip_kelas_sync=True).write({
                        'kelas_ids': [(4, kelas.id)],
                    })
            else:
                # If kelas_id is unset but classes exist, pick the first one as primary.
                if student.kelas_ids:
                    student.with_context(skip_kelas_sync=True).write({
                        'kelas_id': student.kelas_ids[0].id,
                    })
            class_teachers = student.kelas_ids.mapped('guru_ids')
            if class_teachers:
                missing_teachers = class_teachers - student.teacher_ids
                if missing_teachers:
                    student.with_context(skip_kelas_sync=True).write({
                        'teacher_ids': [(4, teacher.id) for teacher in missing_teachers],
                    })
