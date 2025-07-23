from odoo import api, fields, models


class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'

    name = fields.Char(string="Application Number", required=True)  # required
    tag_ids = fields.Many2many(
        comodel_name='loan.application.tag',
        string="Tags"
    )
    document_ids = fields.One2many(
        comodel_name='loan.application.document',
        inverse_name='application_id',
        string="Documents"
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id.id
    )
    date_application = fields.Date(string="Application Date", readonly=True, copy=False)
    date_approval = fields.Date(string="Approval Date", readonly=True, copy=False)
    date_rejection = fields.Date(string="Rejection Date", readonly=True, copy=False)
    date_signed = fields.Datetime(string="Signed On", readonly=True, copy=False)
    down_payment = fields.Monetary(string="Downpayment", required=True, currency_field="currency_id")
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_amount = fields.Monetary(string="Loan Amount", required=True, currency_field="currency_id")
    loan_term = fields.Integer(string="Loan Term (Months)", required=True, default=36)
    rejection_reason = fields.Text(copy=False)
    state = fields.Selection(
        string="Status",
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('review', 'Credit Check'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('signed', 'Signed'),
            ('cancel', 'Canceled'),
        ],
        default='draft',
        copy=False
    )
    notes = fields.Html(string="Notes", copy=False)
