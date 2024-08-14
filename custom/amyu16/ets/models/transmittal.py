
import logging, pytz, datetime, pandas
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Test
def test_with_logger(data: any="Debug Message", warn: bool = False) -> None:
    """
        Outputs a debug message in the odoo log file, 5 times in a row
    """
    method = _logger.info if not warn else _logger.warning
    for _ in range(5):
        method(data)

class Transmittal(models.Model):
    _name = 'transmittal'
    _description = 'Transmittal Record, one-to-one to an Errand Record'

    ctrl_no = fields.Char(string='Ctrl No.') # auto generated
    errand = fields.Many2one(string='Errand')

    # RE-EXAMINE - new table?
    original_qty = fields.Integer(string='Original qty.') # validation, either one should be present
    duplicate_qty = fields.Integer(string='Duplicate qty.')

    unit = fields.Char(string='Unit') # auto suggest
    specific_descriptions = fields.Char(string='Specific Description of Contents')
    remarks = fields.Char(string='Remarks')

