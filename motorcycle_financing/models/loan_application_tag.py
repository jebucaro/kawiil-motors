from odoo import fields, models


class LoanApplicationTag(models.Model):
    _name = 'loan.application.tag'
    _description = 'Loan Application Tag'
    _sql_constraints = [
        ("unique_tag_name", "UNIQUE(name)", "Tag name must be unique."),
    ]

    name = fields.Char(string="Tag", required=True)
    color = fields.Integer(string="Color")
