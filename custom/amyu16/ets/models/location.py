import logging, pytz, datetime, pandas, math
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

class Location(models.Model):
    _name = 'location'
    _description = 'Location Record of the differnt cities involved'
    _sql_constraints = [
        (
            'unique_name', 
            'unique(name)',
            'Can\'t be duplicate value for this record!'
        )
    ]

    name = fields.Char(string="Location Name")

    @api.model
    def create(self, kwargs: dict):
        """ Overrides the create method of the model """

        unformatted_name = kwargs['name']
        formatted_name = str(unformatted_name).title()
        kwargs['name'] = formatted_name

        # Save
        return super(Location, self).create(kwargs)