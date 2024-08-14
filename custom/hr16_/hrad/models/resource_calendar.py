from odoo import models, api, _


class ResourceCalendar(models.Model):
    """ Calendar model for a resource. It has

     - attendance_ids: list of resource.calendar.attendance that are a working
                       interval in a given weekday.
     - leave_ids: list of leaves linked to this calendar. A leave can be general
                  or linked to a specific resource, depending on its resource_id.

    All methods in this class use intervals. An interval is a tuple holding
    (begin_datetime, end_datetime). A list of intervals is therefore a list of
    tuples, holding several intervals of work or leaves. """
    _inherit = "resource.calendar"
    _description = "ONe-HR Default Working Time"

    @api.model
    def default_get(self, fields):
        res = super(ResourceCalendar, self).default_get(fields)
        if not res.get('name') and res.get('company_id'):
            res['name'] = _('Working Hours of %s', self.env['res.company'].browse(res['company_id']).name)
        if 'attendance_ids' in fields and not res.get('attendance_ids'):
            company_id = res.get('company_id', self.env.company.id)
            company = self.env['res.company'].browse(company_id)
            company_attendance_ids = company.resource_calendar_id.attendance_ids
            if company_attendance_ids:
                res['attendance_ids'] = [
                    (0, 0, {
                        'name': attendance.name,
                        'dayofweek': attendance.dayofweek,
                        'hour_from': attendance.hour_from,
                        'hour_to': attendance.hour_to,
                        'day_period': attendance.day_period,
                    })
                    for attendance in company_attendance_ids
                ]
            else:
                res['attendance_ids'] = [
                    (0, 0, {'name': _('Monday'), 'dayofweek': '0', 'hour_from': 7.5, 'hour_to': 16.5,
                            'day_period': 'morning'}),
                    (0, 0, {'name': _('Tuesday'), 'dayofweek': '1', 'hour_from': 7.5, 'hour_to': 16.5,
                            'day_period': 'morning'}),
                    (0, 0, {'name': _('Wednesday'), 'dayofweek': '2', 'hour_from': 7.5, 'hour_to': 16.5,
                            'day_period': 'morning'}),
                    (0, 0, {'name': _('Thursday'), 'dayofweek': '3', 'hour_from': 7.5, 'hour_to': 16.5,
                            'day_period': 'morning'}),
                    (0, 0, {'name': _('Friday'), 'dayofweek': '4', 'hour_from': 7.5, 'hour_to': 16.5,
                            'day_period': 'morning'}),
                    (0, 0, {'name': _('Saturday'), 'dayofweek': '5', 'hour_from': 7.5, 'hour_to': 16.5,
                            'day_period': 'morning'})
                ]
        return res
