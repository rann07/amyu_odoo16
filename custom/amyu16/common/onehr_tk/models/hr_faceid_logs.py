from odoo import api, fields, models
from datetime import datetime, timedelta
from time import time
import requests, jwt, json


class HRFaceIDLogs(models.Model):
    _name = "hr.faceid.logs"
    _description = "Face ID Logs"

    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True)
    log_stamp = fields.Datetime(string="Log Stamp", required=True)
    manual_override = fields.Boolean(string="Manual Override", default=True)
    mo_reason = fields.Text(string="Manual Override Reason")
    db_key = fields.Integer(string="Transision Key")
    log_key = fields.Integer(string="Transision Key")
    company_id = fields.Many2one(string="Company", comodel_name="res.company")
    hr_ob_id = fields.Many2one(comodel_name="hr.ob", string="HR Official Business ID")
    hr_ob_in_out = fields.Selection(string="Time IN/Time Out", selection=[
        ("time_in", "Time In"), ("time_out", "Time Out"),
    ], default="time_in")
    from_crosschex = fields.Boolean(string="From CrossChex", default=False)
    crosschex_uuid = fields.Text(string="UUID")

    def name_get(self):
        result = []
        for log in self:
            name = str(log.hr_employee_id.name) + " - " + str(log.log_stamp + timedelta(hours=8))
            result.append((log.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            if 'company_id' not in vals:
                vals.update({'company_id': self.env['hr.all.employee'].browse([vals['hr_employee_id']]).company_id.id})
            res = super(HRFaceIDLogs, self).create(vals)
        return res

    def update_time_card(self, id):
        logs = self.browse(id)
        for res in logs:
            log_datetime = res.log_stamp + timedelta(hours=8)
            log_date = datetime.strftime(log_datetime, "%Y-%m-%d")
            time_in = 0.0
            time_out = 0.0
            self.env.cr.execute("""
                                    SELECT (to_char(log_stamp + '8 hours'::interval, 'HH24:MI')::TIME)::TEXT AS log_time
                                    FROM hr_faceid_logs WHERE (log_stamp + '8 hours'::interval)::DATE = %s::DATE
                                    AND hr_employee_id = %s ORDER BY log_stamp ASC LIMIT 1; 
                                """, (log_date, res.hr_employee_id.id))
            first_log = self.env.cr.fetchall()
            for f in first_log:
                log_time = f[0].split(':')
                t, hours = divmod(float(log_time[0]), 24)
                t, minutes = divmod(float(log_time[1]), 60)
                minutes = minutes / 60.0
                time_in = hours + minutes

            self.env.cr.execute("""
                                                SELECT (to_char(log_stamp + '8 hours'::interval, 'HH24:MI')::TIME)::TEXT AS log_time
                                                FROM hr_faceid_logs WHERE (log_stamp + '8 hours'::interval)::DATE = %s::DATE
                                                AND hr_employee_id = %s ORDER BY log_stamp DESC LIMIT 1; 
                                            """, (log_date, res.hr_employee_id.id))
            last_log = self.env.cr.fetchall()
            for l in last_log:
                log_time = l[0].split(':')
                t, hours = divmod(float(log_time[0]), 24)
                t, minutes = divmod(float(log_time[1]), 60)
                minutes = minutes / 60.0
                time_out = hours + minutes

            tc_obj = self.env['hr.time.card']

            tc_ids = tc_obj.search([
                ('hr_employee_id', '=', res.hr_employee_id.id),
                ('date', '=', log_date)
            ])

            if not tc_ids:
                tc_vals = {
                    'hr_employee_id': res.hr_employee_id.id,
                    'date': log_date,
                    'time_in': time_in,
                    'time_out': time_out
                }
                tc_obj.create(tc_vals)
            else:
                for tc in tc_ids:
                    tc_vals = {
                        'hr_employee_id': res.hr_employee_id.id,
                        'date': log_date,
                        'time_in': time_in,
                        'time_out': time_out
                    }
                    tc.write(tc_vals)

    def get_crosschex_cloud_logs(self):
        token = jwt.encode(
            {
                "header": {
                    "nameSpace": "authorize.token",
                    "nameAction": "token",
                    "version": "1.0",
                    "requestId": "f1becc28-ad01-b5b2-7cef-392eb1526f39",
                    "timestamp": "2022-10-21T07:39:07+00:00"
                },
                "payload": {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55X2NvZGUiOiIyMTAwMDMwNTEiLCJob29rc19vbiI6MSwidXJsIjoiaHR0cHM6XC9cL2Fudml6YXBpLnZybGFwcHMuY29tXC9hbnZpelwvYW52aXpkYXRhIiwic2VjcmV0IjoiMSIsImNyZWF0ZV90aW1lIjoiMjAyMi0wOC0wOSAwODoxMjozOSIsInVwZGF0ZV90aW1lIjoiMjAyMi0wOS0yNyAwOToxMToyMSIsImFwaV9rZXkiOiJmNzE3NzE2M2M4MzNkZmY0YjM4ZmM4ZDI4NzJmMWVjNiIsImFwaV9zZWNyZXQiOiJkZWVmZDU3MWExMGQ4YjQ2ZmQ4YThkZjdlZWU3MDZiZiIsImV4cCI6MTY2ODA2OTgwNn0.bNEJAb_mi7kBlf-JK4Ufu5Tzx5_IryjqN_WPrJ7uaM8",
                    "expires": "2022-11-10T08:43:26+00:00"
                }
            }
            ,
            "",
            algorithm='HS256'
        )
        url = "https://api.ap.crosschexcloud.com/"
        headers = {
            "header": {
                "nameSpace": "authorize.token",
                "nameAction": "token",
                "version": "1.0",
                "requestId": "f1becc28-ad01-b5b2-7cef-392eb1526f39",
                "timestamp": "2022-10-21T07:39:07+00:00"
            },
            "payload": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjb21wYW55X2NvZGUiOiIyMTAwMDMwNTEiLCJob29rc19vbiI6MSwidXJsIjoiaHR0cHM6XC9cL2Fudml6YXBpLnZybGFwcHMuY29tXC9hbnZpelwvYW52aXpkYXRhIiwic2VjcmV0IjoiMSIsImNyZWF0ZV90aW1lIjoiMjAyMi0wOC0wOSAwODoxMjozOSIsInVwZGF0ZV90aW1lIjoiMjAyMi0wOS0yNyAwOToxMToyMSIsImFwaV9rZXkiOiJmNzE3NzE2M2M4MzNkZmY0YjM4ZmM4ZDI4NzJmMWVjNiIsImFwaV9zZWNyZXQiOiJkZWVmZDU3MWExMGQ4YjQ2ZmQ4YThkZjdlZWU3MDZiZiIsImV4cCI6MTY2ODA2OTgwNn0.bNEJAb_mi7kBlf-JK4Ufu5Tzx5_IryjqN_WPrJ7uaM8",
                "expires": "2022-11-10T08:43:26+00:00"
            }
        }
        # Send the POST request with the payload
        response = requests.post(url, params=json.dumps(headers))

        # Check if the response was successful
        if response.ok:
            # Extract the token from the response
            # token = response.json()["token"]
            # print(f"Authentication token: {token}")
            print(response.json())
        else:
            # Print the error message if the request failed
            print(f"Error: {response.status_code} - {response.text}")
