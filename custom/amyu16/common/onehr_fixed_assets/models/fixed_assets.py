from io import BytesIO
import base64
import qrcode
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from xmlrpc import client as xmlrpclib


class FixedAssets(models.Model):
    _name = "onehr.fixed.assets"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Fixed Asset"
    _sql_constraints = [("unique_fa_code", "unique(company_id,name)",
                         "Uniqueness of Fixed Asset Code per OBU is violated. Please choose different Code"), ]

    company_id = fields.Many2one(string="Company", comodel_name="onehr.fa.view.all.companies",
                                 default=lambda self: self.env.company.id)
    has_one = fields.Boolean(string="Has ONe System", related="company_id.has_one", readonly=True)
    name = fields.Char(string="Asset Code", copy=False)
    asset_qty = fields.Integer(string="Quantity")
    short_description = fields.Char(string="Short Description")
    full_description = fields.Text(string="Full Description")
    remarks = fields.Text(string="Notes")
    date_issued = fields.Date(string="Date Issued")
    cancelled = fields.Boolean(string="Cancelled")
    cancel_notes = fields.Text(string="Cancellation Notes")
    date_cancelled = fields.Date(string="Date Cancelled")
    status = fields.Many2one(string="Status", comodel_name="onehr.fa.status")
    fa_location_id = fields.Many2one(string="Location", comodel_name="onehr.fa.location")
    uom_id = fields.Many2one(string="UoM", comodel_name="onehr.fa.uom")
    group_id = fields.Many2one(string="Group", comodel_name="onehr.fa.group")
    unit_price = fields.Float(string="Unit Price")
    date_purchased = fields.Date(string="Date Purchased")
    is_manually_tagged = fields.Boolean(string="Manually Tagged")
    manual_asset_code = fields.Char(string="Manual Asset Code")
    brand = fields.Char(string="Brand")
    serial_number = fields.Char(string="Serial Number")
    is_disposed = fields.Boolean(string="Disposed?")
    disposed_date = fields.Date(string="Disposal Date")
    disposed_notes = fields.Text(string="Notes")

    custodian = fields.Selection(string="Assigned to", selection=[
        ("employee", "Employee"), ("department", "Department"),
        ("none", "Non-Employee"), ("unassigned", "Unassigned")
    ], default="unassigned")
    non_employee = fields.Char(string="Name")
    hr_employee_id = fields.Many2one(string="Employee", comodel_name="onehr.fa.view.all.employees")
    # image_128 = fields.Binary(string="Employee Picture", related="hr_employee_id.image_1920", readonly=True)
    hr_department_id = fields.Many2one(string="Department", comodel_name="onehr.fa.view.all.departments")
    hr_department_head = fields.Char(string="Department Head", related="hr_department_id.manager_id.name")
    fa_movement_ids = fields.One2many(string="Movement Log", comodel_name="onehr.fa.movement.log", inverse_name="fa_id")
    fa_code_ids = fields.One2many(string="Code Update Log", comodel_name="onehr.fa.code.log", inverse_name="fa_id")
    qr_code = fields.Binary("QR Code")
    is_equipment = fields.Boolean(string="Equipment with Maintenance", default=False)
    equipment_id = fields.Many2one(string="Equipment Name", comodel_name="maintenance.equipment")
    with_lapsing = fields.Boolean(string="With Lapsing")
    assigned_to = fields.Char(string="Custodian", compute="get_assigned_to", readonly=True)
    for_leasing = fields.Boolean(string="Subject for leasing", default=False)
    one_id = fields.Integer()
    company_name = fields.Char(string="Company Name", related="company_id.name")

    def get_assigned_to(self):
        for fa in self:
            assigned_to = ""
            if fa.custodian == "employee":
                assigned_to = fa.hr_employee_id.name
            elif fa.custodian == "department":
                assigned_to = fa.hr_department_id.name + \
                              (
                                  " (" + fa.hr_department_id.manager_id.name + ")" if fa.hr_department_id.manager_id else "")
            elif fa.custodian == 'none':
                assigned_to = fa.non_employee
            fa.assigned_to = assigned_to

    @api.onchange("is_equipment")
    def is_equipment_changed(self):
        self.equipment_id = False if not self.is_equipment else self.equipment_id

    def code_update(self):
        old_name = self.name
        new_name = self.env['ir.sequence'].next_by_code('fa.seq')
        code_obj = self.env['onehr.fa.code.log']
        code_obj.create([{
            'from_code': old_name,
            'to_code': new_name,
            'fa_id': self.id
        }])
        self.write({'name': new_name})

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        for vals in vals_list:
            if self.with_lapsing:
                one_id = self.get_one_id()
                if one_id:
                    vals.update({'one_id': one_id})
                    vals.update({'name': self.env['ir.sequence'].next_by_code('fa.seq')})
                    res = super(FixedAssets, self).create(vals)
            else:
                vals.update({'name': self.env['ir.sequence'].next_by_code('fa.seq')})
                res = super(FixedAssets, self).create(vals)
            if res:
                if 'is_equipment' in vals and vals['is_equipment']:
                    print("Creating Equipment Record for Fixed Asset: " + vals['name'])
                    new_me_obj = self.env['maintenance.equipment'].create({'name': vals['name'], 'fa_id': res.id})
                    res.write({"qr_code": False, 'equipment_id': new_me_obj.id})
                else:
                    res.write({"qr_code": False})
                if 'with_lapsing' in vals and vals['with_lapsing']:
                    print("Creating COS/FOS/MOS Asset Lapsing")

        return res

    def write(self, vals):
        if 'is_equipment' in vals:
            if self.is_equipment and not vals['is_equipment']:
                print("Equipment will be deleted")
                self.env['maintenance.equipment'].browse([self.equipment_id.id]).unlink()
            if vals['is_equipment'] and not self.equipment_id:
                new_me_obj = self.env['maintenance.equipment'].create({'name': self.name})
                vals.update({'equipment_id': new_me_obj.id})

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = str(self.id)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        vals.update({"qr_code": qr_image})
        print(qr_data)

        if self.with_lapsing and not self.one_id:
            one_id = self.get_one_id()
            if one_id:
                vals.update({'one_id': one_id})
                super(FixedAssets, self).write(vals)
        else:
            super(FixedAssets, self).write(vals)

    def get_one_id(self):
        obu = self.env.company
        url = obu.host_ip
        db = obu.db_name
        username = obu.username
        password = obu.passwd
        print("Preparing to update " + obu.name + " products model...")
        print("Connecting to " + url)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise UserError(_(url + " failed to authenticate " + username))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if not models:
            raise UserError(_(url + " failed to authenticate " + username))

        # 1. get ID of Asset Type from ONe System
        asset_categ = models.execute_kw(db, uid, password,
                                        'account.asset.category', 'search', [[
                ['name', 'ilike', '%fixed asset%']
            ]])
        if asset_categ:
            asset_categ_id = asset_categ[0]
            # 2. create Fixed Asset record to ONe System
            asset = {
                'name': self.short_description or ('ONe-HR:' + self.name),
                'category_id': asset_categ_id,
                'code': ('ONe-HR:' + self.name),
                'value': 1
            }
            one_ids = models.execute_kw(db, uid, password, 'account.asset.asset', 'create', [asset])
            print(one_ids)
        return one_ids if one_ids else False


class FixedAssetGroup(models.Model):
    _name = "onehr.fa.group"
    _description = "Fixed Asset Group"
    _sql_constraints = [("unique_fa_group", "unique(company_id,name)",
                         "Uniqueness of Fixed Asset Group per OBU is violated. Please choose different Group Name"), ]

    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    name = fields.Char(string="Group Name", required=True)


class FixedAssetLocation(models.Model):
    _name = "onehr.fa.location"
    _description = "Fixed Asset Location"
    _sql_constraints = [("unique_fa_location", "unique(company_id,name)",
                         "Uniqueness of Fixed Asset Group per OBU is violated. Please choose different Group Name"), ]

    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    name = fields.Char(string="Group Name", required=True)
    active = fields.Boolean(string="Active?", default=True)


class FixedAssetUoM(models.Model):
    _name = "onehr.fa.uom"
    _description = "Fixed Asset UoM"
    _sql_constraints = [("unique_fa_uom", "unique(company_id,name)",
                         "Uniqueness of Fixed Asset Unit of Measure is violated. Please choose different UoM Name"), ]

    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    name = fields.Char(string="UoM", required=True)


class FixedAssetStatus(models.Model):
    _name = "onehr.fa.status"
    _description = "Fixed Asset Status"
    _sql_constraints = [("unique_fa_status", "unique(company_id,name)",
                         "Uniqueness of Fixed Asset Status is violated. Please choose different Status Name"), ]

    company_id = fields.Many2one(string="Company", comodel_name="res.company",
                                 default=lambda self: self.env.company.id)
    name = fields.Char(string="Status", required=True)


class FixedAssetMovementLogs(models.Model):
    _name = "onehr.fa.movement.log"
    _description = "Fixed Asset Movement Log"

    date_stamp = fields.Datetime(string="Stamp", default=fields.Datetime.now())
    user_id = fields.Many2one(string="Performed by", comodel_name="res.users", default=lambda self: self.env.user.id)
    from_employee_id = fields.Many2one(string="From Employee", comodel_name="hr.employee")
    to_employee_id = fields.Many2one(string="To Employee", comodel_name="hr.employee")
    from_department_id = fields.Many2one(string="From Department", comodel_name="hr.department")
    to_department_id = fields.Many2one(string="To Department", comodel_name="hr.department")
    fa_id = fields.Many2one(string="Fixed Asset", comodel_name="onehr.fixed.assets")
    company_id = fields.Many2one(string="Business Unit", comodel_name="res.company")


class FixedAssetCodeLogs(models.Model):
    _name = "onehr.fa.code.log"
    _description = "Fixed Asset Code Log"

    date_stamp = fields.Datetime(string="Stamp", default=fields.Datetime.now())
    user_id = fields.Many2one(string="Performed by", comodel_name="res.users", default=lambda self: self.env.user.id)
    from_code = fields.Char(string="From Code")
    to_code = fields.Char(string="To Code")
    fa_id = fields.Many2one(string="Fixed Asset", comodel_name="onehr.fixed.assets")
