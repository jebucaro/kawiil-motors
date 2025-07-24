from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Links this partner to all related loan applications
    application_ids = fields.One2many(
        comodel_name="loan.application", 
        inverse_name="partner_id",
        string="Loan Applications"
    )

    # A computed field that counts how many loan applications the partner has
    application_count = fields.Integer(
        compute="_compute_application_count",
        string="Application Count"
    )

    @api.depends('application_ids')
    def _compute_application_count(self):
        """Compute the number of loan applications for this partner."""
        for partner in self:
            partner.application_count = len(partner.application_ids)

    def action_view_applications(self):
        """Return an action to view loan applications for this partner."""
        action = {
            "name": _("Loan Applications"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "loan.application",
            "target": "current", 
            "domain": [("partner_id", "=", self.id)],
            "context": {
                "default_partner_id": self.id,
                "search_default_partner_id": self.id
            }
        }
        
        # If only one application, open it directly in form view
        if self.application_count == 1:
            action.update({
                "view_mode": "form,list",
                "res_id": self.application_ids[0].id,
            })
        
        return action
