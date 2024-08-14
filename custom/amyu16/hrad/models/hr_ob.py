from odoo import api, fields, models
from datetime import datetime
# from firebase_admin import messaging, credentials
# import firebase_admin, base64, requests


class OfficialBusinessParticulars(models.Model):
    _name = "hr.ob.particulars"
    _description = "Official Business Particulars"

    time_in = fields.Float(string="Time In")
    time_out = fields.Float(string="Time Out")
    particular = fields.Char(string="Particulars")
    name_of_company = fields.Char(string="Name of Company/Address")
    person_visited = fields.Char(string="Person Visited")
    particulars_id = fields.Many2one(comodel_name="hr.ob", string="Official Business Particulars")


class OfficialBusiness(models.Model):
    _name = "hr.ob"
    _description = "Official Business"

    name = fields.Char(string="OB Number")
    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id, required=True, copy=False)
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="hr.employee", required=True)
    job_name = fields.Char(string="Job Position", related="hr_employee_id.job_id.name", readonly=True)
    department_name = fields.Char(string="Department", related="hr_employee_id.department_id.name", readonly=True)
    start_date = fields.Date(string="From", required=True, default=datetime.today())
    end_date = fields.Date(string="To", required=True, default=datetime.today())
    days = fields.Float(string="Days", default=1.0, required=True)
    reason = fields.Char(string="Particulars/Reason")
    person_visited = fields.Char(string="Person Visited")
    plate_number = fields.Char(string="Plate Number")
    odometer = fields.Integer(string="Odometer")
    mode_of_transportation = fields.Char(string="Mode of Transportation")
    qr_code_link = fields.Char(string="QR Code Link", default="")
    ob_particulars = fields.One2many(comodel_name="hr.ob.particulars", inverse_name="particulars_id",
                                     string="OB Particulars")
    status = fields.Selection(string="Status", selection=[
        ("for_approval", "For Approval"), ("approved", "Approved"),
        ("disapproved", "Disapproved"), ("cancelled", "Cancelled")
    ], default="for_approval")
    approved_from_app = fields.Boolean()
    approved_from_app_by = fields.Many2one(string="OB Approved by", comodel_name="hr.all.employee")
    approved_by = fields.Many2one(string="OB Approved by", comodel_name="res.users")
    approved_stamp = fields.Datetime()
    disapproved_from_app = fields.Boolean()
    disapproved_from_app_by = fields.Many2one(string="OB Disapproved by", comodel_name="hr.all.employee")
    disapproved_by = fields.Many2one(string="OB Approved by", comodel_name="res.users")
    disapproved_stamp = fields.Datetime()
    image_1920 = fields.Char(compute="leave_get_employee_image")

    def leave_get_employee_image(self):
        for s in self:
            s.image_1920 = s.env['hr.employee'].search([('id', '=', s.hr_employee_id.id)]).image_1920

    def action_approved(self):
        self.write({
            'status': 'approved',
            'approved_by': self.env.user.id,
            'approved_stamp': fields.Datetime.now()
        })

    def action_disapproved(self):
        self.write({
            'status': 'disapproved',
            'disapproved_by': self.env.user.id,
            'disapproved_stamp': fields.Datetime.now()
        })

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            name = self.env['ir.sequence'].next_by_code('ob.seq')
            vals.update({'name': name})
            res = super(OfficialBusiness, self).create(vals)

            if res:
                registration_token = []
                employee = self.env['hr.employee'].search([('id', '=', vals['hr_employee_id'])])
                approver_id = self.env['hr.employee'].search([('id', '=', employee.ot_approver_ids.id)])
                dev_obj = self.env['res.users.devices'].search([('user_id', '=', approver_id.user_id.id)])

                employee_name = employee.name
                if dev_obj:
                    for dev in dev_obj:
                        registration_token.append(dev.name)
                        print(dev)

                    params = {
                        'title': 'Official Application',
                        'body': employee_name + ' filed an Official Business Application',
                        'registration_token': registration_token,
                    }
                    self.push_notification(params)

        return res

    @api.onchange("start_date", "end_date")
    def date_changed(self):
        d1 = datetime.strptime(str(self.start_date), "%Y-%m-%d")
        d2 = datetime.strptime(str(self.end_date), "%Y-%m-%d")
        self.days = abs((d2 - d1).days) + 1

    def push_notification(self, vals={}):
        # [START send_to_token]py
        print("TEST")
        creds = credentials.Certificate({
            "type": "service_account",
            "project_id": "one-hr-app",
            "private_key_id": "29a2a927b87de1a0514c83a5384c26987989f8ce",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDNhbmPUsWBs/Ku\nn7csapzKa+P/txb7isfBNPsjhHAlR1H8gxxFqE5k4iOewC8LixtG1dmMylY6HnjF\nPuPvBeRYQ+PLLuKu2WfnlAA7r8wl3bBGVNfkEYHCN5lCmwQsjJNSFEzkuujBqeqk\nKgiNdqvznv2Tt3jxwQB17ddBom9fMkyhf3si345NQYoOgQJBYc2b9QHHPtox0zzs\nZ4ifLk3nJrhjaWzcpTS/sZ5h0IoP74bFwzwlYtGnZqFSlTWShITPqA2wPatpBpSY\nTOjaHS2hCQyH5xMMXlkIC46py4sMOw+3BdkA75HsFRIPnJ3pw8GkbXk5uznCWYfw\nfQklrKuzAgMBAAECggEAJZ4Z4kFgtEZXH55NPTyAWU6ZK1d8RetXd6Y2Z4BYtIIS\n4BixZpCRVMbNhUOg+Mhr5DHFQY9RbA7ixRunRbs62esHOUvqIt3ZNlpxFnutbqre\nlmj2ISERMpbRnw7Xmz3ZwzbDAkSx0KzErWqiKR51B8Dsogp9gSZ16p/ve+x63R33\n5HpFwKTT15HF3iTk81y3+cTkmy6f1DRXRXWHVV94BWabGm8IjAPw4PVFefI48IcX\naGtGnwpX+GSlX5ggLEpyjmjcla9mCuXQVr0EAeBaru57aERjMdpDb9L7YztaW3VT\nCbOz1Ehf5XcWXaMR4fc3uKvrQ2iP/2t61tViJYy2vQKBgQD9dvob5yy2vuktSEiq\n7EbVGs8y+JbS/XhEOG0FR5gqWCnCTP8HIux5qGMrcTqOz+3bYRuYJgOB4/om8wZA\nMxNAeBoVJmur/O/zKICxAqzkr7b4yqCl4YzJQlYqMYmFXny4TQYHF1+jtC0YILDz\noQKWTOwndZfBedm6wuh7++VDbwKBgQDPk/yBTnH8aitNL6w2P3YtJ2DPAiXo50nF\nWXE1EyudqnDons4gNzg3LrF+2rIydyQl1sCb7ze5IZRI2zMRUjKUfhEXlskX8qCT\nckQIqH2ZxFGh44B3Cw2Lwh1Bl+xd6GV0cslrlLnfhILgFYoBvYANin9N1RZY0Na9\nlN4a0Vfp/QKBgFVw4ea+CuifemL1VumnNElp/CamfdEp+HymuLlq5PSBO7Jv2hhB\nwY1RIfzm8mJp3Thyh6bGSbBjdVPj4FuL3BWDZudySCF15j0FjjwdNsLwKLG9PGIu\nohLF9d3LTRxUOZ62+C0zx92bQwg7HOtDf2fDDmhOz5U8yhSW11/UDfipAoGAOHH4\nXr0TF91S6wlEnffBzeOAWqot3thN4iFBPHp7CMOZMlhEmtQJMFA9Kc6UWE63gKaV\n95EkKO5toSYiC9q7ME/bm/t/sUhjy9RtlaEjjlWpEQmJHFXgGBnv1K9YMe0I8ZJp\nHRzzMkmZQQ/6WCDMmmIH3gVMr1gSnLjHcKlua40CgYEA3YA8Pm1qZg8eoNjwuMFc\ne1siqO4md0eLSrVg1x186n8ElUXGiAmlw4bJNXmaurV1mUAtJwxYHokhpKe4R3EI\n9Zoh53SDVS9lq9f6q9KopoOkG8vfnBnL2H236xKq3YHTh1nNVa6x1fd7WTjSU00u\nz2iMxc8mbjVkL006zlZHI6o=\n-----END PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk-dmh6w@one-hr-app.iam.gserviceaccount.com",
            "client_id": "109952179474382930240",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-dmh6w%40one-hr-app.iam.gserviceaccount.com"
        })

        # if not firebase_admin._apps:
        #     default_app = firebase_admin.initialize_app(creds)
        #     # This registration token comes from the client FCM SDKs.
        # else:
        #     default_app = firebase_admin.get_app()
        # # apns
        # # See documentation on defining a message payload.
        # android = messaging.AndroidConfig(notification=messaging.AndroidNotification(sound='default'))
        # ios = messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default')))
        # notification = messaging.Notification(title=vals['title'], body=vals['body'])
        # message = messaging.MulticastMessage(
        #     notification=notification,
        #     android=android,
        #     apns=ios,
        #     data={
        #         '1': '1',
        #     },
        #     tokens=vals['registration_token']
        # )
        #
        # # Send a message to the device corresponding to the provided
        # # registration token.
        # response = messaging.send_multicast(message, app=default_app)
        # if not response:
        #     messaging.send_multicast(message, app=default_app)
        # # Response is a message ID string.
        # print('Successfully sent message:', response)
        # # [END send_to_token]

    def write(self, vals):
        res = super(OfficialBusiness, self).write(vals)
        if res:
            registration_token = []
            employee = self.env['hr.employee'].search([('id', '=', self.hr_employee_id.id)])
            dev_obj = self.env['res.users.devices'].search([('user_id', '=', employee.user_id.id)])

            employee_name = employee.name
            if dev_obj:
                for dev in dev_obj:
                    registration_token.append(dev.name)
                    print(dev)

                params = {
                    'title': 'Official Application',
                    'body': 'Your Official Business Application has been ' + vals['status'],
                    'registration_token': registration_token,
                }
                self.push_notification(params)
