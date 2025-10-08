from odoo import fields, models


class SmkKelas(models.Model):
    _name = 'smk.kelas'
    _description = 'Kelas'

    name = fields.Char(string='Nama Kelas', required=True)
    guru_ids = fields.Many2many(
        'smk.guru',
        'smk_guru_kelas_rel',
        'kelas_id',
        'guru_id',
        string='Guru Pengajar',
    )
    siswa_ids = fields.Many2many(
        'smk.siswa',
        'smk_siswa_kelas_rel',
        'kelas_id',
        'siswa_id',
        string='Siswa',
    )
