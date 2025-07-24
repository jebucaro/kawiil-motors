{
	'name': 'Motorcycle Financing',
	'summary': 'Streamline the loan application process for dealerships',
	'license': 'OPL-1',
	'category': 'Kawiil/Finance',
	'author': 'Jonathan Búcaro',
	'version': '18.0.0.0.1',
	'depends': ['base', 'web', 'sale'],
	'data': [
		'security/motorcycle_financing_groups.xml',
		'security/ir.model.access.csv',
		'security/rules.xml',
		'views/loan_application_views.xml',
		'views/loan_application_tag_views.xml',
		'views/loan_application_document_type_views.xml',
		'views/motorcycle_financing_menu.xml',
	],
	'demo': [
        'data/loan_demo.xml',
	],
	'application': True,
}