from odoo import api, models


class ReportSmkKwitansi(models.AbstractModel):
    _name = 'report.SMK-Karangayar.report_smk_kwitansi_document'
    _description = 'Laporan Kwitansi SMK'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['smk.invoice'].browse(docids)
        company = self.env.company
        return {
            'doc_ids': docs.ids,
            'doc_model': 'smk.invoice',
            'docs': docs,
            'company': company,
        }
