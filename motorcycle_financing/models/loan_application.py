from odoo import api, fields, models


class LoanApplication(models.Model):
    _sql_constraints = [
        ("downpayment_non_negative_value", "CHECK(down_payment >= 0)", "The downpayment cannot be negative."),
    ]
    @api.constrains('down_payment', 'sale_order_total')
    def _check_down_payment(self):
        for rec in self:
            if rec.down_payment and rec.sale_order_total and rec.down_payment > rec.sale_order_total:
                from odoo.exceptions import ValidationError
                raise ValidationError("Downpayment cannot exceed the sale order total.")
    def action_send(self):
        """Send application for approval: all documents must be approved."""
        self.ensure_one()
        if any(doc.state != 'approved' for doc in self.document_ids):
            from odoo.exceptions import UserError
            raise UserError("All documents must be approved before sending the application.")
        if self.state != 'draft':
            from odoo.exceptions import UserError
            raise UserError("Only draft applications can be sent.")
        self.state = 'sent'
        self.date_application = fields.Date.context_today(self)
        return True

    def action_approve(self):
        """Approve the loan application."""
        self.ensure_one()
        if self.state != 'sent':
            from odoo.exceptions import UserError
            raise UserError("Only sent applications can be approved.")
        self.state = 'approved'
        self.date_approval = fields.Date.context_today(self)
        return True

    def action_reject(self):
        """Reject the loan application."""
        self.ensure_one()
        if self.state not in ['sent', 'approved']:
            from odoo.exceptions import UserError
            raise UserError("Only sent or approved applications can be rejected.")
        self.state = 'rejected'
        self.date_rejection = fields.Date.context_today(self)
        return True
    _name = 'loan.application'
    _description = 'Loan Application'
    _order = 'date_application desc, id desc'

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

    @api.depends('partner_id', 'product_id')
    def _compute_display_name(self):
        """Compute display name as 'Customer Name - Motorcycle Name'"""
        for rec in self:
            customer_name = rec.partner_id.name if rec.partner_id else "Unknown Customer"
            motorcycle_name = rec.product_id.name if rec.product_id else "Unknown Motorcycle"
            rec.display_name = f'{customer_name} - {motorcycle_name}'

    @api.model_create_multi
    def create(self, vals_list):
        """Create loan applications and automatically generate documents for each active document type"""
        # Create the loan applications first
        applications = super().create(vals_list)
        
        # Get all active document types
        active_document_types = self.env['loan.application.document.type'].search([('active', '=', True)])
        
        # For each created application, create documents for all active types
        document_vals_list = []
        for application in applications:
            sequence = 10  # Start sequence at 10
            for doc_type in active_document_types:
                document_vals_list.append({
                    'name': doc_type.name,
                    'application_id': application.id,
                    'type_id': doc_type.id,
                    'state': 'new',
                    'sequence': sequence,
                })
                sequence += 10  # Increment by 10 for each document
        
        # Create all documents in batch
        if document_vals_list:
            self.env['loan.application.document'].create(document_vals_list)
        
        return applications

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

    def action_send(self):
        """Send loan application for review"""
        for record in self:
            if record.state == 'draft':
                record.state = 'sent'
                record.date_application = fields.Date.today()

    def action_review(self):
        """Set loan application to review state"""
        for record in self:
            if record.state == 'sent':
                record.state = 'review'

    def action_approve(self):
        """Approve loan application"""
        for record in self:
            if record.state == 'review':
                record.state = 'approved'
                record.date_approval = fields.Date.today()

    def action_reject(self):
        """Reject loan application"""
        for record in self:
            if record.state in ['sent', 'review']:
                record.state = 'rejected'
                record.date_rejection = fields.Date.today()

    def action_sign(self):
        """Sign loan application"""
        for record in self:
            if record.state == 'approved':
                record.state = 'signed'
                record.date_signed = fields.Datetime.now()

    def action_reset_to_draft(self):
        """Reset loan application to draft"""
        for record in self:
            record.state = 'draft'
            record.date_application = False
            record.date_approval = False
            record.date_rejection = False
            record.date_signed = False
            record.rejection_reason = False
