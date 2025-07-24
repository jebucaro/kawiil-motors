from odoo import fields, models


class LoanApplicationDocument(models.Model):
    def action_accept(self):
        """Approve the document."""
        self.ensure_one()
        self.state = 'approved'
        return True

    def action_reject(self):
        """Reject the document."""
        self.ensure_one()
        self.state = 'rejected'
        return True

    @fields.onchange('attachment')
    def _onchange_attachment(self):
        if self.attachment:
            self.state = 'new'
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
