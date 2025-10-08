from odoo import fields, models


class SmkKelas(models.Model):
    _name = 'smk.kelas'
    _description = 'Kelas'

    name = fields.Char(string='Nama Kelas', required=True)
    guru_id = fields.Many2one('smk.guru', string='Wali Kelas', required=True)
    siswa_ids = fields.One2many('smk.siswa', 'kelas_id', string='Siswa')
