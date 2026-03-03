from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountReport(models.Model):
    _inherit = 'account.report'

    tax_return_start_date = fields.Date(
        string="Start Date",
        company_dependent=True,
        help="Tax periods will be calculated starting from this date"
    )

    def action_create_composite_report(self):
        """Create a composite report (variant) from selected reports"""
        if not self:
            raise UserError(_("Please select at least one report."))
        
        # In Odoo 17, composite reports are called "variants"
        # They require setting root_report_id, but there's no wizard UI (that's new in Odoo 18)
        raise UserError(_(
            "Creating composite reports requires manual configuration in Odoo 17.\n\n"
            "To create a variant:\n"
            "1. Open a report in form view\n"
            "2. Set the 'Root Report' field to link it to a parent report\n\n"
            "Odoo 18 adds a wizard to simplify this process."
        ))

    def action_insert_in_spreadsheet(self):
        """Insert selected reports in spreadsheet"""
        if not self:
            raise UserError(_("Please select at least one report."))
        
        # Check if spreadsheet module is installed
        if 'spreadsheet.dashboard' not in self.env:
            raise UserError(_("Spreadsheet module is not installed. Please install 'spreadsheet_dashboard' module."))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'action_open_spreadsheet',
            'params': {
                'spreadsheet_id': False,
                'default_report_ids': self.ids,
            }
        }

    def _init_options_date(self, options, previous_options=None):
        super()._init_options_date(options, previous_options)
        
        # We only apply the default for tax-related reports.
        is_tax_report = self.env.ref('account_reports.tax_report', raise_if_not_found=False)
        if is_tax_report and (self == is_tax_report or self.root_report_id == is_tax_report):
            # If the filter is custom or today (default), force it to tax_period to match Odoo 18
            current_filter = options.get('date', {}).get('filter')
            if current_filter in ('custom', 'today') or not current_filter:
                date_from, date_to = self.env.company._get_tax_closing_period_boundaries(fields.Date.context_today(self))
                options['date'] = self._get_dates_period(date_from, date_to, 'range')
                options['date']['filter'] = 'tax_period'

    def _get_options_domain(self, options, date_scope):
        domain = super()._get_options_domain(options, date_scope)
        
        # We only apply the filter for tax-related reports.
        is_tax_report = self.env.ref('account_reports.tax_report', raise_if_not_found=False)
        
        if is_tax_report and (self == is_tax_report or self.root_report_id == is_tax_report):
            # Use report's start date if set, otherwise company's
            start_date = self.tax_return_start_date or self.env.company.account_tax_periodicity_start_date
            if start_date:
                domain.append(('date', '>=', start_date))
        
        return domain
