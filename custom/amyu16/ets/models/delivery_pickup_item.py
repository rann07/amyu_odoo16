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
        
class DeliveryPickupItem(models.Model):
    _name = 'delivery.pickup.items'
    _description = 'Delivery and Pickup Items counted as "Others"'
    _sql_constraints = [
        (
            'unique_name', 
            'unique(name)',
            'Can\'t have duplicate value for this field!'
        )
    ]

    name = fields.Char(string="Item Name")

    @api.model
    def create(self, kwargs: dict):
        """ Overrides the create method of the model """

        unformatted_name = kwargs['name']
        formatted_name = str(unformatted_name).title()
        kwargs['name'] = formatted_name

        # Save
        return super(Location, self).create(kwargs)
