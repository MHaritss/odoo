from odoo import api, fields, models


class SmkSiswa(models.Model):
    _name = 'smk.siswa'
    _description = 'Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', required=True, tracking=True)
    nis = fields.Char(string='NIS', tracking=True)
    kelas_id = fields.Many2one('smk.kelas', string='Kelas', tracking=True, required=True)
    guru_id = fields.Many2one(
        'smk.guru',
        string='Wali Kelas',
        related='kelas_id.guru_id',
        store=True,
        readonly=True,
        tracking=True,
    )
    teacher_ids = fields.Many2many(
        'smk.guru',
        'smk_guru_student_rel',
        'siswa_id',
        'guru_id',
        string='Guru Pengajar',
    )
    kelas_history_ids = fields.Many2many(
        'smk.kelas',
        'smk_siswa_kelas_rel',
        'siswa_id',
        'kelas_id',
        string='Riwayat Kelas',
        help='Daftar kelas yang pernah diikuti siswa.',
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
        record._ensure_history_contains_current_class()
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'kelas_id' in vals:
            self._ensure_history_contains_current_class()
        return res

    def _ensure_history_contains_current_class(self):
        for student in self:
            kelas = student.kelas_id
            if kelas and kelas not in student.kelas_history_ids:
                student.kelas_history_ids = [(4, kelas.id)]
