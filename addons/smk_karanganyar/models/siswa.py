from odoo import api, fields, models


class SmkSiswa(models.Model):
    _name = 'smk.siswa'
    _description = 'Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', required=True, tracking=True)
    nis = fields.Char(string='NIS', tracking=True)
    guru_id = fields.Many2one('smk.guru', string='Guru', tracking=True, required=True)
    kelas_id = fields.Many2one('smk.kelas', string='Kelas', tracking=True, required=True)
    phone = fields.Char(string='Nomor Telepon Wali')
    address = fields.Text(string='Alamat')
    active = fields.Boolean(default=True)

    @api.onchange('kelas_id')
    def _onchange_kelas_id(self):
        if self.kelas_id:
            self.guru_id = self.kelas_id.guru_id
