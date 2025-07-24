from odoo import fields, models


class LoanApplicationDocumentType(models.Model):
    _name = 'loan.application.document.type'
    _description = 'Loan Application Document Type'
    _sql_constraints = [
        ("unique_document_type_name", "UNIQUE(name)", "Document type name must be unique."),
    ]

    name = fields.Char(string="Document Type", required=True)
    active = fields.Boolean(string="Active", default=True)
