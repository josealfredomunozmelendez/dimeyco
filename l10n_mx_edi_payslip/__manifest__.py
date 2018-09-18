# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Payroll",
    "version": "11.0.1.0.1",
    "author": "Vauxoo",
    "category": "Localization",
    "website": "http://vauxoo.com",
    "license": "LGPL-3",
    "depends": [
        "hr_payroll",
        "l10n_mx_edi",
        "l10n_mx_edi_bank",
    ],
    "demo": [
        "demo/employee_demo.xml",
        "demo/res_users_demo.xml",
        "demo/payroll_cfdi_demo.xml",
        "demo/res_company_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/3.3/payroll12.xml",
        "data/mail_template.xml",
        "views/hr_payslip_view.xml",
        "views/res_company.xml",
        "views/hr_contract_view.xml",
        "views/hr_payslip_report.xml",
        "views/res_config_settings_views.xml",
        "data/hr_contract_type_data.xml",
        "data/hr_employee_data.xml",
        "data/salary_rule_data.xml",
        "data/fiscal_position_data.xml",
        "data/payroll_structure_data.xml",
    ],
    "js": [],
    "css": [],
    "qweb": [],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False
}
