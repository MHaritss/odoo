import json

from werkzeug.exceptions import BadRequest

from odoo import http
from odoo.http import request


class SmkApiController(http.Controller):
    @http.route('/api/smk/guru', type='json', auth='public', methods=['GET'], csrf=False)
    def api_get_guru(self, **kwargs):
        gurus = request.env['smk.guru'].sudo().search([])
        data = []
        for guru in gurus:
            students = (guru.kelas_ids.mapped('siswa_ids') | guru.teaching_student_ids)
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
                        'classes': siswa.kelas_ids.mapped('name'),
                        'active': siswa.active,
                    }
                    for siswa in students
                ],
            })
        body = json.dumps({'data': data})
        headers = [('Content-Type', 'application/json')]
        return request.make_response(body, headers=headers)

    @http.route('/api/smk/siswa', type='json', auth='public', methods=['POST'], csrf=False)
    def api_create_siswa(self):
        try:
            payload = json.loads(request.httprequest.data or '{}')
        except Exception as exc:
            raise BadRequest('Payload harus berupa JSON yang valid.') from exc

        name = payload.get('name')
        kelas_id = payload.get('kelas_id')
        if not name:
            raise BadRequest('Field name wajib diisi.')
        if not kelas_id:
            raise BadRequest('Field kelas_id wajib diisi.')

        kelas = request.env['smk.kelas'].sudo().browse(int(kelas_id))
        if not kelas:
            raise BadRequest('Kelas tidak ditemukan.')

        siswa_vals = {
            'name': name,
            'nis': payload.get('nis'),
            'kelas_id': kelas.id,
            # 'kelas_ids': [(6, 0, [kelas.id])],
            # 'phone': payload.get('phone'),
            'address': payload.get('address'),
        }
        siswa = request.env['smk.siswa'].sudo().create(siswa_vals)

        response_payload = {
            'id': siswa.id,
            'name': siswa.name,
            'kelas_id': siswa.kelas_id.id,
        }
        body = json.dumps(response_payload)
        headers = [('Content-Type', 'application/json')]
        response = request.make_response(body, headers=headers)
        response.status_code = 201
        return response
