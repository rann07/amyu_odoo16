from odoo import api, models
import requests
from datetime import datetime, timedelta
import uuid


class GetCrossChexFaceIDLogs(models.TransientModel):
    _name = 'crosschex.faceid.logs.pool'
    _description = "CrossChex FaceID Logs Pool"

    @api.model
    def crosschex_faceid_logs_pool_cron(self):
        cc_api_key = self.env['ir.config_parameter'].sudo().get_param('onehr_tk.cc_api_key')
        cc_secret = self.env['ir.config_parameter'].sudo().get_param('onehr_tk.cc_secret')
        no_of_days = self.env['ir.config_parameter'].sudo().get_param('onehr_tk.no_of_days')
        s_count = no_of_days
        for x in range(int(no_of_days)):
            s_count = int(s_count) - 1
            formatted_s_date = (datetime.today() - timedelta(days=int(s_count))).strftime('%d-%m-%Y')
            if not cc_api_key or not cc_secret:
                print("No settings found!", cc_api_key, cc_secret)
                return False

            token_header = {
                "nameSpace": "authorize.token",
                "nameAction": "token",
                "version": "1.0",
                "requestId": str(uuid.uuid1()),
                "timestamp": str(datetime.utcnow() + timedelta(hours=8)),
            }
            token_payload = {
                "api_key": cc_api_key,
                "api_secret": cc_secret
            }
            r = requests.post("https://api.ap.crosschexcloud.com/", json={
                "header": token_header,
                "payload": token_payload
            })
            token = r.json()['payload']['token']
            ar_header = {
                "nameSpace": "	attendance.record",
                "nameAction": "getrecord",
                "version": "1.0",
                "requestId": str(uuid.uuid1()),
                "timestamp": str(datetime.utcnow() + timedelta(hours=8)),
            }
            ar_authorize = {
                "type": "token",
                "token": token,
            }
            # print(last_cc_record["log_stamp"])
            ar_payload = {
                "begin_time": formatted_s_date,
                "end_time": str(datetime.utcnow() + timedelta(hours=8)),
                "order": "asc",
                "page": '1',
                "per_page": "100",
            }
            r = requests.post("https://api.ap.crosschexcloud.com/", json={
                "header": ar_header,
                "authorize": ar_authorize,
                "payload": ar_payload
            })
            for index in range(r.json()['payload']['pageCount']):
                inner_ar_payload = {
                    "begin_time": formatted_s_date,
                    "end_time": str(datetime.utcnow() + timedelta(hours=8)),
                    "order": "asc",
                    "page": index + 1,
                    "per_page": "100",
                }
                inner_r = requests.post("https://api.ap.crosschexcloud.com/", json={
                    "header": ar_header,
                    "authorize": ar_authorize,
                    "payload": inner_ar_payload
                })
                inner_record_list = inner_r.json()['payload']['list']
                for i in inner_record_list:
                    if i['device']['serial_number'] != '1740100021020025':  # Skip demo unit device
                        time = i['checktime']
                        employee_exist = self.env['hr.all.employee'].search([('id', '=', i['employee']['workno'])])
                        if employee_exist:
                            if self.env['hr.faceid.logs'].search([('crosschex_uuid', '=', i['uuid'])]):
                                print("RECORD ALREADY EXIST")
                                print(i)
                            else:
                                print("RECORD DOES NOT EXIST")
                                print(i)
                                tk = {'hr_employee_id': int(i['employee']['workno']),
                                      'log_stamp': str(
                                          time[:4] + "-" + time[5:7] + "-" + time[8:10]
                                          + " " + time[11:13] + ":" + time[14:16] + ":" + time[17:19]),
                                      'manual_override': False,
                                      'from_crosschex': True,
                                      'crosschex_uuid': i['uuid']}
                                self.env['hr.faceid.logs'].create(tk)
