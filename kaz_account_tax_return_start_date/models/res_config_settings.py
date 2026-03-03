from odoo import fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_tax_periodicity_start_date = fields.Date(
        related='company_id.account_tax_periodicity_start_date',
        readonly=False,
        string="Tax Return Start Date",
    )

    def open_tax_report_start_dates(self):
        """Open tree view to configure start dates per report (like Odoo 18)"""
        self.ensure_one()
        
        # Get all tax-related reports that actually exist in database
        tax_reports = self.env['account.report'].search([
            '|', '|', 
            ('root_report_id.name', 'ilike', 'tax'),
            ('name', 'ilike', 'tax'),
            ('id', '=', self.env.ref('account.generic_tax_report', raise_if_not_found=False).id if self.env.ref('account.generic_tax_report', raise_if_not_found=False) else 0)
        ])
        
        # Verify reports exist
        if not tax_reports:
            raise UserError("No tax reports found in the database. Please install account_reports module.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configure Tax Report Start Dates',
            'res_model': 'account.report',
            'view_mode': 'tree',
            'domain': [('id', 'in', tax_reports.ids)],
            'views': [(self.env.ref('kaz_account_tax_return_start_date.account_report_start_date_tree').id, 'tree')],
            'target': 'current',
        }
