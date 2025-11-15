from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from sqlalchemy.orm import joinedload

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS
    CORS(app)
    
    db.init_app(app)
    
    # Add template filters
    from ingredient_formatter import format_recipe_ingredient
    app.jinja_env.filters['format_ingredient'] = format_recipe_ingredient
    
    # Register API blueprint
    from api import api_bp
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

from models import Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, Equipment, RecipeEquipment

@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = Recipe.query.options(
        joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
    ).get_or_404(recipe_id)
    
    # Calculate recipe cost
    from price_calculator import calculate_recipe_cost
    cost_data = calculate_recipe_cost(recipe_id, db.session)
    
    return render_template('recipe_detail.html', recipe=recipe, cost_data=cost_data)

@app.route('/prices')
def price_manager():
    """Web UI for viewing ingredient prices"""
    return render_template('price_manager.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
