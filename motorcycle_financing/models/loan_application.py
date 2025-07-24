from odoo import api, fields, models


class LoanApplication(models.Model):
    _name = 'loan.application'
    _description = 'Loan Application'

    name = fields.Char(string="Application Number", required=True)
    
    # Relational Fields
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Related Sale Order",
        help="Sale order associated with this loan application"
    )
    product_id = fields.Many2one(
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
    
    # Related Fields (computed from sale_order_id)
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id",
        string="Customer",
        help="Customer for this loan application",
        store=True
    )
    user_id = fields.Many2one(
        related="sale_order_id.user_id",
        string="Salesperson",
        help="Salesperson responsible for this loan application",
        store=True
    )
    currency_id = fields.Many2one(
        related="sale_order_id.currency_id",
        string="Currency",
        store=True
    )
    sale_order_total = fields.Monetary(
        related="sale_order_id.amount_total",
        string="Sale Order Total",
        currency_field="currency_id",
        store=True
    )
    
    # Date fields
    date_application = fields.Date(string="Application Date", readonly=True, copy=False)
    date_approval = fields.Date(string="Approval Date", readonly=True, copy=False)
    date_rejection = fields.Date(string="Rejection Date", readonly=True, copy=False)
    date_signed = fields.Datetime(string="Signed On", readonly=True, copy=False)
    
    # Financial fields
    down_payment = fields.Monetary(string="Downpayment", required=True, currency_field="currency_id")
    loan_amount = fields.Monetary(
        string="Loan Amount",
        compute="_compute_loan_amount",
        inverse="_inverse_loan_amount",
        currency_field="currency_id",
        store=True
    )
    interest_rate = fields.Float(string="Interest Rate (%)", required=True, digits=(5, 2))
    loan_term = fields.Integer(string="Loan Term (Months)", required=True, default=36)
    
    # Other fields
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

    @api.depends('sale_order_total', 'down_payment')
    def _compute_loan_amount(self):
        """Compute loan amount as sale order total minus down payment"""
        for record in self:
            record.loan_amount = record.sale_order_total - record.down_payment

    def _inverse_loan_amount(self):
        """When loan amount is set manually, compute down payment"""
        for record in self:
            record.down_payment = record.sale_order_total - record.loan_amount

    @api.onchange('sale_order_id')
    def _onchange_sale_order_id(self):
        """When sale order changes, update product from first order line"""
        if self.sale_order_id and self.sale_order_id.order_line:
            self.product_id = self.sale_order_id.order_line[0].product_id
