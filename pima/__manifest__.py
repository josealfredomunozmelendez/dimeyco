# coding: utf-8
{
    "name": "Pima ERP Instance",
    "author": "PIMA, Vauxoo",
    "summary": """
    All the necessary modules to auto install our service instance
    """,
    "website": "http://www.pima.com",
    "license": "LGPL-3",
    "category": "PIMA",
    "version": "11.0.1.0.3",
    "depends": [
        # Account section
        "account_accountant",
        "account_budget",
        "account_cash_basis_base_account",
        "account_reports_followup",
        "account_online_sync",
        "account_voucher",
        "account_analytic_default",
        "account_accountant",
        "account_payment",

        # Project Section.
        "purchase_requisition",
        "project_forecast",
        "helpdesk",

        # Human resources
        "hr_expense",

        # Localizations
        "l10n_mx_edi",
        "l10n_mx_edi_landing",
        "l10n_mx_reports",
        "l10n_mx_import_taxes",
        "l10n_mx_edi_payment",
        "l10n_mx_edi_payslip",
        "hr_payroll_account",

        # Website modules
        "login",
        "web_search_with_and",

        # Sales
        "mrp_analytic",
        "crm",
        "sale_management",
        "sale_margin",
        "sale_timesheet",
        "sale_expense",
        "sale_stock",
        "website_quote",

        # Tools
        "document",
        "base_automation",
        "inter_company_rules",
        'auth_oauth',
        "mass_editing",
        "board",
        "contacts",
        "google_account",
        "partner_credit_limit",
        "mrp_plm",
        "product_extended",
        "inventory_requisition",
    ],
    "data": [
        # Main Configuration
        "data/res_config_settings.yml",
        # Data
        'data/res_currency.xml',
        #'data/company.xml',
        'data/project_tags.xml',
        "data/hr_timesheet_invoice_data.xml",
        "data/product.xml",
        "data/project_task_estimation.xml",
        # Security
        "security/ir_rule.xml",
        "security/res_users.xml",
        "security/ir.model.access.csv",
        # Views
        "views/project.xml",
        "views/account_analytic_line_view.xml",
        "views/account_budget_view.xml",
        "views/menu.xml",
        'views/saleorder.xml',
        # # Reports
        "report/layout.xml",
        "report/timesheet_template.xml",
        'report/sale_report_templates.xml',
        # # Wizards (One Per Wizard)
        "wizard/employee_user_view.xml",
        # # Stages Data
        "data/sales.xml",
        "data/base_automation_data.xml",
        "views/sale_template.xml",
        "views/company_view.xml",
    ],
    "demo": [
    ],
    "test": [
    ],
    "qweb": ['static/src/xml/*.xml'],
    "auto_install": False,
    "application": True,
    "pre_init_hook": "_auto_load_translation",
    "installable": True,
}
