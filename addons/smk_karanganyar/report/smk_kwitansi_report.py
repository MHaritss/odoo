from odoo import api, fields, models


class ReportSmkKwitansi(models.AbstractModel):
    _name = 'report.smk_karanganyar.report_smk_kwitansi_document'
    _description = 'Laporan Kwitansi SMK'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['smk.invoice'].browse(docids)
        company = self.env.company
        timestamp = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        return {
            'doc_ids': docs.ids,
            'doc_model': 'smk.invoice',
            'docs': docs,
            'company': company,
            'print_date': timestamp.strftime('%d/%m/%Y') if timestamp else '-',
            'print_time': timestamp.strftime('%H:%M:%S') if timestamp else '-',
        }
