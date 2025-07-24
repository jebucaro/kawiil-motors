from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    loan_application_ids = fields.One2many(
        comodel_name="loan.application", 
        inverse_name="sale_order_id", 
        string="Loan Applications"
    )
    is_financed = fields.Boolean(string="Requires Financing", default=False)
    state = fields.Selection(selection_add=[
        ('loan', 'Applied for Loan')
    ])

    @api.onchange('is_financed')
    def _onchange_is_financed(self):
        """Validate motorcycle product when financing is enabled"""
        if self.is_financed:
            self._get_motorcycle_product()

    def action_apply_loan(self):
        """Apply for a loan - opens loan application form with pre-filled context"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("motorcycle_financing.new_loan_application_action")
        context = self._prepare_loan_application_context()
        context['search_default_sale_order_id'] = self.id
        action['context'] = context
        self.state = 'loan'
        return action
    
    def _prepare_loan_application_context(self):
        """Prepare context for loan application with default values"""
        self.ensure_one()
        product = self._get_motorcycle_product()
        application_context = {
            'default_sale_order_id': self.id,
            'default_product_id': product.id,
            'default_name': f'{self.partner_id.name} - {product.name}',
        }
        return application_context
    
    def _get_motorcycle_product(self):
        """Fetch the motorcycle product in the sale order, ensure there is exactly one."""
        # We use `env.ref()` to fetch a specific record by its external XML ID.
        # In this case, we retrieve the motorcycle category defined as a data record in `data/loan_data.xml`.
        # This approach is customer-specific and not fully scalable, but it simplifies the example
        # and demonstrates how to use external IDs to access records in your code.
        motorcycle_category = self.env.ref("motorcycle_financing.motorcycle_product_category")
        order_lines = self.order_line.filtered(lambda line: line.product_id.categ_id == motorcycle_category)
        
        if sum(order_lines.mapped('product_uom_qty')) > 1:
            raise UserError(_("This Sale Order contains more than one Motorcycle. You need a separate Sale Order for each Motorcycle Product you want to apply for a Loan."))
        
        if not order_lines:
            raise UserError(_("This Sale Order does not contain any Motorcycle Product. You need at least one motorcycle product to apply for a loan."))
        
        return order_lines.mapped('product_id')[0]
