"""
RESTful API endpoints for Trading Kitchen
"""

from flask import Blueprint, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import cross_origin
from models import db, Ingredient, IngredientPrice
from datetime import datetime
from decimal import Decimal

# Create Blueprint for API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create API with Swagger documentation
api = Api(api_bp, 
    version='1.0', 
    title='Trading Kitchen API',
    description='API for accessing ingredient prices and recipe data',
    doc='/docs'
)

# Define namespaces
prices_ns = Namespace('prices', description='Ingredient price operations')
api.add_namespace(prices_ns)

# Define API models for documentation
price_model = api.model('Price', {
    'ingredient_id': fields.Integer(required=True, description='ID of the ingredient'),
    'ingredient_name': fields.String(required=True, description='Name of the ingredient'),
    'price': fields.Float(required=True, description='Price per unit'),
    'unit': fields.String(required=True, description='Unit of measurement (lb, oz, can, etc.)'),
    'quantity': fields.Float(required=True, description='Quantity for the price'),
    'currency': fields.String(required=True, description='Currency code (USD, EUR, etc.)'),
    'last_updated': fields.DateTime(required=True, description='Last update timestamp')
})

prices_response = api.model('PricesResponse', {
    'country_code': fields.String(required=True, description='ISO 3166-1 alpha-3 country code'),
    'currency': fields.String(required=True, description='Default currency for this country'),
    'total_prices': fields.Integer(required=True, description='Total number of prices'),
    'prices': fields.List(fields.Nested(price_model))
})

# ISO 3166-1 alpha-3 to currency mapping
COUNTRY_CURRENCIES = {
    'USA': 'USD',
    'GBR': 'GBP',
    'CAN': 'CAD',
    'AUS': 'AUD',
    'EUR': 'EUR',  # Generic Europe
    'JPN': 'JPY',
    'MEX': 'MXN',
    'BRA': 'BRL',
    'IND': 'INR',
    'CHN': 'CNY',
}


@prices_ns.route('/<string:country_code>')
@prices_ns.param('country_code', 'ISO 3166-1 alpha-3 country code (e.g., USA, GBR, CAN)')
class PricesByCountry(Resource):
    @prices_ns.doc('get_prices_by_country')
    @cross_origin()
    def get(self, country_code):
        """Get all ingredient prices for a specific country"""
        
        # Validate country code
        country_code = country_code.upper()
        if len(country_code) != 3:
            api.abort(400, f"Invalid country code format. Use ISO 3166-1 alpha-3 (e.g., USA)")
        
        # Get prices for country
        prices = db.session.query(IngredientPrice).filter_by(
            country_code=country_code
        ).join(Ingredient).all()
        
        if not prices:
            # Return empty list with country info
            return {
                'country_code': country_code,
                'currency': COUNTRY_CURRENCIES.get(country_code, 'USD'),
                'total_prices': 0,
                'prices': []
            }
        
        # Format response
        price_list = []
        for price in prices:
            price_list.append({
                'ingredient_id': price.ingredient_id,
                'ingredient_name': price.ingredient.name,
                'price': float(price.price),
                'unit': price.unit,
                'quantity': float(price.quantity),
                'currency': price.currency,
                'last_updated': price.last_updated.isoformat()
            })
        
        return {
            'country_code': country_code,
            'currency': prices[0].currency if prices else COUNTRY_CURRENCIES.get(country_code, 'USD'),
            'total_prices': len(price_list),
            'prices': price_list
        }


@prices_ns.route('/')
class AllPrices(Resource):
    @prices_ns.doc('get_all_countries')
    @cross_origin()
    def get(self):
        """Get list of all countries with available prices"""
        
        # Get distinct country codes
        countries = db.session.query(
            IngredientPrice.country_code,
            db.func.count(IngredientPrice.id).label('price_count')
        ).group_by(IngredientPrice.country_code).all()
        
        country_list = []
        for country_code, count in countries:
            country_list.append({
                'country_code': country_code,
                'currency': COUNTRY_CURRENCIES.get(country_code, 'USD'),
                'total_prices': count,
                'api_url': f'/api/prices/{country_code}'
            })
        
        return {
            'total_countries': len(country_list),
            'countries': country_list
        }


# Endpoint to add/update prices (for future use)
@prices_ns.route('/<string:country_code>/<string:ingredient_name>')
@prices_ns.param('country_code', 'ISO 3166-1 alpha-3 country code')
@prices_ns.param('ingredient_name', 'Standardized ingredient name')
class PriceUpdate(Resource):
    price_update = api.model('PriceUpdate', {
        'price': fields.Float(required=True, description='Price per unit'),
        'unit': fields.String(required=True, description='Unit of measurement'),
        'quantity': fields.Float(default=1.0, description='Quantity for the price'),
        'currency': fields.String(description='Currency code (defaults to country default)')
    })
    
    @prices_ns.doc('update_price')
    @prices_ns.expect(price_update)
    @cross_origin()
    def put(self, country_code, ingredient_name):
        """Update or create a price for a specific ingredient in a country"""
        # This would require authentication in production
        api.abort(501, "Price updates not yet implemented")


# Health check endpoint
@api.route('/health')
class HealthCheck(Resource):
    def get(self):
        """API health check"""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        }

# Define namespaces
recipes_ns = Namespace('recipes', description='Recipe operations')
api.add_namespace(recipes_ns)

@recipes_ns.route('/<int:recipe_id>/troubleshoot')
@recipes_ns.param('recipe_id', 'The recipe ID')
class RecipeTroubleshoot(Resource):
    @recipes_ns.doc('troubleshoot_recipe')
    @cross_origin()
    def get(self, recipe_id):
        """Troubleshoot a recipe's cost calculation"""
        from models import Recipe
        from price_calculator import calculate_recipe_cost

        recipe = db.session.query(Recipe).get(recipe_id)
        if not recipe:
            api.abort(404, f"Recipe with id {recipe_id} not found")

        cost_data = calculate_recipe_cost(recipe_id, db.session)

        ingredients_data = []
        for ri in recipe.ingredients:
            ingredients_data.append({
                'ingredient': ri.ingredient.name,
                'quantity': ri.quantity,
                'amount': ri.amount,
                'unit': ri.unit,
                'status': 'OK' if ri.amount and ri.unit else 'PARSE_ERROR'
            })

        return {
            'recipe_id': recipe.id,
            'recipe_title': recipe.title,
            'cost_data': cost_data,
            'ingredients': ingredients_data
        }