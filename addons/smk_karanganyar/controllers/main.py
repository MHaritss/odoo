import json

from odoo import http
from odoo.http import request


class SmkApiController(http.Controller):
    @http.route('/api/smk/guru', type='http', auth='user', methods=['GET'], csrf=False)
    def api_get_guru(self, **kwargs):
        gurus = request.env['smk.guru'].sudo().search([])
        data = []
        for guru in gurus:
            data.append({
                'id': guru.id,
                'name': guru.name,
                'address': guru.address,
                'phone': guru.phone,
                'student_count': guru.student_count,
                'students': [
                    {
                        'id': siswa.id,
                        'name': siswa.name,
                        'class': siswa.kelas_id.name,
                        'active': siswa.active,
                    }
                    for siswa in guru.siswa_ids
                ],
            })
        body = json.dumps({'data': data})
        headers = [('Content-Type', 'application/json')]
        return request.make_response(body, headers=headers)

    @http.route('/api/smk/siswa', type='json', auth='user', methods=['POST'], csrf=False)
    def api_create_siswa(self, **payload):
        required_fields = ['name']
        missing = [field for field in required_fields if not payload.get(field)]
        if missing:
            return {'error': f"Field {', '.join(missing)} wajib diisi."}

        siswa_vals = {
            'name': payload.get('name'),
            'nis': payload.get('nis'),
            'guru_id': payload.get('guru_id'),
            'kelas_id': payload.get('kelas_id'),
            'phone': payload.get('phone'),
            'address': payload.get('address'),
        }
        if siswa_vals['kelas_id'] and not siswa_vals['guru_id']:
            kelas = request.env['smk.kelas'].sudo().browse(siswa_vals['kelas_id'])
            if kelas:
                siswa_vals['guru_id'] = kelas.guru_id.id
        if not siswa_vals['guru_id'] or not siswa_vals['kelas_id']:
            return {'error': 'Guru dan kelas wajib diisi.'}

        guru = request.env['smk.guru'].sudo().browse(siswa_vals['guru_id'])
        kelas = request.env['smk.kelas'].sudo().browse(siswa_vals['kelas_id'])
        if not guru:
            return {'error': 'Guru tidak ditemukan.'}
        if not kelas:
            return {'error': 'Kelas tidak ditemukan.'}
        if kelas.guru_id and kelas.guru_id.id != guru.id:
            return {'error': 'Guru dan kelas tidak sesuai.'}

        siswa = request.env['smk.siswa'].sudo().create(siswa_vals)
        return {
            'id': siswa.id,
            'name': siswa.name,
            'guru_id': siswa.guru_id.id,
            'kelas_id': siswa.kelas_id.id,
        }
