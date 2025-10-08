import json

from odoo import http
from odoo.http import request


class SmkApiController(http.Controller):
    @http.route('/api/smk/guru', type='http', auth='user', methods=['GET'], csrf=False)
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

    @http.route('/api/smk/siswa', type='json', auth='user', methods=['POST'], csrf=False)
    def api_create_siswa(self, **payload):
        required_fields = ['name']
        missing = [field for field in required_fields if not payload.get(field)]
        if missing:
            return {'error': f"Field {', '.join(missing)} wajib diisi."}

        kelas_ids = payload.get('kelas_ids') or []
        primary_kelas_id = payload.get('kelas_id')
        if primary_kelas_id and primary_kelas_id not in kelas_ids:
            kelas_ids.append(primary_kelas_id)
        if not primary_kelas_id and kelas_ids:
            primary_kelas_id = kelas_ids[0]

        if not primary_kelas_id:
            return {'error': 'Minimal satu kelas wajib dipilih.'}

        kelas_records = request.env['smk.kelas'].sudo().browse(kelas_ids)
        if len(kelas_records) != len(kelas_ids):
            return {'error': 'Sebagian kelas tidak ditemukan.'}

        teacher_ids = payload.get('teacher_ids') or []
        teacher_records = request.env['smk.guru'].sudo().browse(teacher_ids)
        if len(teacher_records) != len(teacher_ids):
            return {'error': 'Sebagian guru tidak ditemukan.'}

        siswa_vals = {
            'name': payload.get('name'),
            'nis': payload.get('nis'),
            'kelas_id': primary_kelas_id,
            'kelas_ids': [(6, 0, kelas_ids)],
            'teacher_ids': [(6, 0, teacher_ids)],
            'phone': payload.get('phone'),
            'address': payload.get('address'),
        }

        siswa = request.env['smk.siswa'].sudo().create(siswa_vals)
        return {
            'id': siswa.id,
            'name': siswa.name,
            'kelas_id': siswa.kelas_id.id,
            'kelas_ids': siswa.kelas_ids.ids,
            'teacher_ids': siswa.teacher_ids.ids,
        }
