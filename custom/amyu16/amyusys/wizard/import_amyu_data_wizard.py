import logging, base64, pandas as pd, json, math
from io import BytesIO
from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class ImportAmyuDataWizard(models.TransientModel):
    _name = 'import.amyu.data.wizard'
    _description = "Allows import of data according to models of AMYU modules"
    
    excel_file = fields.Binary()
    
    enable_print = True
    
    def process_import(self):
        # Check if uploaded or not
        if not (self.excel_file):
            return self._error_message('No files attached', 
                'Please attach a file in order to submit.')
        
        # Transform excel to json
        # data dict structure: { <model>: { <arbitrary__id>: { <data> } }}
        data: dict = self._parse_data()
        self._print_data(data, use_log=True)
        
        # Validate the worksheets
        invalid = self._invalid_data(data)
        if invalid: return invalid
        
        # Process the data and create records
        created, created_per_model = self._process_data(data)
        
        # Format message
        suffix = "" if created == 1 else "s"
        title = f'Created {created} record{suffix}'
        message = ''
        for model_name, count in created_per_model.items():
            message += f'{model_name}: {count} | '
        
        # Success
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
        
    def _parse_data(self):
        
        excel_file = base64.b64decode(self.excel_file)

        # Read the Excel file
        excel_data = pd.read_excel(BytesIO(excel_file), sheet_name=None)

        # Transform each sheet into CSV and then into JSON
        json_data = {}
        for sheet_name, sheet_data in excel_data.items():
            arb_list: list = sheet_data['arbitrary__id'].values.tolist()
            df = sheet_data.loc[:, sheet_data.columns != 'arbitrary__id']
            
            # Make the 'arbitrary__id' the key
            json_data[sheet_name] = {
                arb_id: data
                for arb_id, data in zip(
                    arb_list, 
                    json.loads(df.to_json(orient='records'))
                ) if arb_id and not math.isnan(arb_id)
            }
        
        return json_data

    def _invalid_data(self, data: dict):
        for model_name, _ in data.items():
            if not self.env['ir.model'].search([('model', '=', model_name)]):
                return self._error_message('Incorrect Naming', 
                                           'One of the worksheets do not correspond to a model.')
        return False
    
    def _process_data(self, data:dict):
        
        def _process_hr_employee(data: dict):
            created = 0
            employees = {}
            skipped = []
            record: dict
            for arbitrary__id, record in data.items():
                arbitrary__id = int(arbitrary__id)
                
                new_user = {}
                if record['res.users__login']:
                    # If user already exists, skip the record
                    existing = self.env['res.users'].search([('login', '=', record['res.users__login'])])
                    if existing: 
                        employees[arbitrary__id] = self.env['hr.employee'].search([('user_id', '=', existing.id)])
                        skipped.append(arbitrary__id)
                        self._print('User skipped: ' + str(arbitrary__id) + ' > with id of ' + str(employees[arbitrary__id].id), True)
                        continue
                    
                    new_user['name'] = record['first_name'] + ' ' + record['family_name']
                    new_user['login'] = record['res.users__login']
                    if record['res.users__password']:
                        new_user['password'] = record['res.users__password']
                user_id = None if not new_user else self.env['res.users'].create(new_user)
                self._print('User created: ' + str(arbitrary__id), True)
                
                record_no_arb = {'user_id': user_id.id} if user_id else {}
                field_name: str
                for field_name, value in record.items():
                    # Ignore res.users
                    if field_name.startswith('res.users'):
                        continue
                    # Skip arbitrary for now
                    if field_name.startswith('arbitrary__'):
                        continue
                    # If foreign key: department_id and job_id
                    if field_name in ['department_id', 'job_id'] and value:
                        fname = field_name.split('_')[0]
                        obj_id = self.env[f'hr.{fname}'].search([('name', '=', value)])
                        if not obj_id:
                            obj_id = self.env[f'hr.{fname}'].create({'name': value})
                        record_no_arb[field_name] = obj_id.id
                    # If regular field and values
                    else:
                        record_no_arb[field_name] = value
                
                employees[arbitrary__id] = self.env['hr.employee'].create(record_no_arb)
                created += 1
                self._print('Employee created: ' + str(arbitrary__id), True)
        
            # Process arbitrary now
            for arbitrary__id, record in data.items():
                if arbitrary__id in skipped: continue
                arb_fields = {}
                field_name: str
                for field_name, value in record.items():
                    if field_name.startswith('arbitrary__') and value:
                        fname = field_name.replace('arbitrary__', '')
                        arb_fields[fname] = employees[value].id
                user_id = employees[arbitrary__id]
                user_id.update(arb_fields)
                self._print('Employee updated: ' + str(arbitrary__id), True)
            
            if skipped:
                self._print('Employee skipped count: ' + str(len(skipped)), True)
            
            self.env.cr.commit()
            return created, employees
        
        def _process_associate_profile(data: dict, hr_employees: dict):
            created = 0
            associates = {}
            skipped = []
            record: dict
            for arbitrary__id, record in data.items():
                arbitrary__id = int(arbitrary__id)
                employee_id = hr_employees[record['user_id']]
                
                # If user already exists, skip the record
                existing = self.env['associate.profile'].search([('user_id', '=', employee_id.user_id.id)])
                if existing: 
                    associates[arbitrary__id] = existing
                    skipped.append(arbitrary__id)
                    self._print('Assoc Profile skipped: ' + str(arbitrary__id) + ' > with id of ' + str(existing.id), True)
                    continue
                
                team_id = self.env[f'team.department'].search([('name', '=', record['team_id'])])
                if not team_id:
                    team_id = self.env[f'team.department'].create({'name': record['team_id']})
                
                # self._print(user_id.first_name, True)
                
                associates[arbitrary__id] = self.env['associate.profile'].create({
                    'user_id': employee_id.user_id.id, 
                    'supervisor_id': employee_id.coach_id.id,
                    'manager_id': employee_id.parent_id.id,
                    'team_id': team_id.id, 
                    'cluster_id': employee_id.department_id.id,
                    'job_id': employee_id.job_id.id,
                    'lead_partner_id': employee_id.executive_id.id,
                })
                
                created += 1
                self._print('Assoc Profile created: ' + str(arbitrary__id), True)
            return created, associates
        
        def _process_client_profile(data: dict, hr_employees:dict, associates: dict):
            created = 0
            clients = {}
            skipped = []
            record: dict
            for arbitrary__id, record in data.items():
                arbitrary__id = int(arbitrary__id)
                
                # If user already exists, skip the record
                existing = self.env['client.profile'].search([('name', 'ilike', str(record['name']).upper())])
                if existing: 
                    associates[arbitrary__id] = existing
                    skipped.append(arbitrary__id)
                    self._print('Client Profile skipped: ' + str(arbitrary__id) + ' > with id of ' + str(existing.id), True)
                    continue
                
                employee_id = hr_employees[record['user_id']]
                assoc_id = associates[record['team_id']]
                
                new_record = {'user_id': employee_id.user_id.id, 'team_id': assoc_id.id}
                field_name:str
                for field_name, value in record.items():
                    if field_name.endswith('_id'):
                        continue
                    new_record[field_name] = value
                
                clients[arbitrary__id] = self.env['client.profile'].create(new_record)
                created += 1
                self._print('Client Profile created: ' + str(arbitrary__id), True)
            return created, clients
            
        created_total = 0
        created_per_model = {}
        records_dict: dict
        objects = {}
        for model_name, records_dict in data.items():
            created = 0
            if model_name == 'hr.employee':
                created, objects['hr_employees'] = _process_hr_employee(records_dict)
            elif model_name == 'associate.profile':
                created, objects['associates'] = _process_associate_profile(records_dict, objects['hr_employees'])
            elif model_name == 'client.profile':
                created, _ = _process_client_profile(records_dict, objects['hr_employees'],  objects['associates'])
            created_total += created 
            created_per_model[model_name] = created
            self._print('Created for ' + model_name + ' count: ' + str(created), True)
        
        return created_total, created_per_model
            # self.env[model_name].create(data)
    
    def _print(self, data, use_log=False):
        if not self.enable_print: return
        logger = self.Logger()
        display = print if not use_log else logger.log
        display('_______________________________________')
        display(str(data))
        display('_______________________________________')
         
    def _print_data(self, data: dict, use_log=False):
        if not self.enable_print: return
        logger = self.Logger()
        display = print if not use_log else logger.log
        
        disp_str = '\n\n_______________________________________'
        records: dict
        for model, records in data.items():
            disp_str += ('\n\n'+ model + ':')
            for record in records.items():
                disp_str += '\n' + str(record)
        disp_str += ('\n_______________________________________\n\n')
        display(disp_str)
 
    def _error_message(self, title: str, message: str):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'No files attached',
                'message': 'Please attach a file in order to submit.',
                'sticky': True,
                'type': 'danger'
            }
        }

                  
    class Logger():
        _logger = logging.getLogger(__name__)
        
        def log(self, data: any="Debug Message", method=None, repeat: int=1) -> None:
            """Outputs a debug message in the odoo log file"""
            method = method if method else self._logger.info
            for _ in range(repeat):
                method(data)
        
        def warn(self, data: any="Debug Message", repeat: int=1):
            self.log(self._logger.warning, data, repeat)