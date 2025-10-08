from odoo import api, models


class ReportSmkGuru(models.AbstractModel):
    _name = 'report.SMK-Karangayar.report_smk_guru_document'
    _description = 'Laporan Daftar Guru'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['smk.guru'].browse(docids) if docids else self.env['smk.guru'].search([])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'smk.guru',
            'docs': docs,
        }
