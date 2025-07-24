from odoo import api, fields, models


class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'

    name = fields.Char(string="Application Number", required=True)  # required
    
    # Customer and Sales Information
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        help="Customer for this loan application",
        required=True
    )
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Related Sale Order",
        help="Sale order associated with this loan application"
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        help="Salesperson responsible for this loan application",
        default=lambda self: self.env.user
    )
    product_template_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        help="Product to be financed through this loan"
    )
    
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

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """When sale order changes, update related fields automatically"""
        if self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id
            # Set product from the first order line if available
            if self.sale_order_id.order_line:
                self.product_template_id = self.sale_order_id.order_line[0].product_id
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """When partner changes, filter sale orders to only show those for this partner"""
        if self.partner_id and self.sale_order_id and self.sale_order_id.partner_id != self.partner_id:
            self.sale_order_id = False
