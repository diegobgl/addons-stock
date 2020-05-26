{
    'name': 'MRP Split Manufacturing order',
    'summary': """
    Keyword: Split MO in two with transferred pickings.
    partial manufacture. split manufacturing order.split manufacture order. splitting MO.MO split.
    """,
    'version': '11.0.10.09',
    'category': 'Manufacturing',
    'author': 'Sunpop.cn',
    'license': 'AGPL-3',
    "price": 68.00,
    "currency": "EUR",
    'website': 'http://www.sunpop.cn',
    'images': ['static/description/banner.png'],
    'depends': [
        'mrp',
        'stock',
    ],
    'data': [
         'views/mrp_production_views.xml',
         'wizard/mrp_product_produce_views.xml',
    ],
}
