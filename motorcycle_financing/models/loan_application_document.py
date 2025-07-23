from odoo import fields, models


class LoanApplicationDocument(models.Model):
    _name = 'loan.application.document'
    _description = 'Loan Application Document'

    name = fields.Char(string="Document", required=True)
    application_id = fields.Many2one(
        comodel_name='loan.application',
        string="Application",
        required=True
    )
    attachment = fields.Binary(string="Attachment")
    type_id = fields.Many2one(
        comodel_name='loan.application.document.type',
        string="Type",
        required=True
    )
    state = fields.Selection(
        string="State",
        selection=[
            ('new', 'New'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='new',
        required=True
    )
