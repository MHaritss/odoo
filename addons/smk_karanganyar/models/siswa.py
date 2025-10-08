from odoo import fields, models


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
    phone = fields.Char(string='Nomor Telepon Wali')
    address = fields.Text(string='Alamat')
    active = fields.Boolean(default=True)
