from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    @api.constrains('guru_ids')
    def _check_guru_limits(self):
        for kelas in self:
            count = len(kelas.guru_ids)
            if count < 1:
                raise ValidationError('Setiap kelas wajib memiliki minimal satu guru pengajar.')
            if count > 3:
                raise ValidationError('Setiap kelas maksimal memiliki tiga guru pengajar.')
