from app import app, db
from models import Ingredient, RecipeIngredient, IngredientPrice
from sqlalchemy import func
from unit_converter import parse_quantity_string
import re

def extract_ingredient_name(full_string):
    """Extract just the ingredient name from strings like '2 cups flour'"""
    # Remove common measurements and quantities
    patterns = [
        r'^\d+[\s\-/]*\d*\s*(cups?|cup|tablespoons?|tbsp|teaspoons?|tsp|pounds?|lbs?|lb|ounces?|oz|can|cans|package|packages|bag|bags|box|boxes)\s+(?:of\s+)?',
        r'^\d+[\s\-/]*\d*\s+',
        r'^½|¼|¾|⅓|⅔\s*',
    ]
    
    clean_name = full_string
    for pattern in patterns:
        clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
    
    # Remove parenthetical optionals
    clean_name = re.sub(r'\s*\([^)]*\)\s*$', '', clean_name)
    
    return clean_name.strip()

with app.app_context():
    # Get all unique base ingredients
    all_ingredients = db.session.query(Ingredient).all()
    
    base_ingredients = {}
    for ing in all_ingredients:
        base_name = extract_ingredient_name(ing.name)
        if base_name and base_name not in base_ingredients:
            base_ingredients[base_name] = ing.id
    
    print(f"Found {len(base_ingredients)} unique base ingredients")
    print("\nSample extracted ingredients:")
    for name in sorted(base_ingredients.keys())[:20]:
        print(f"  - {name}")
    
    # Now add prices for these base ingredients
    sample_prices = {
        # Flour & Grains
        'all-purpose flour': (0.50, 'lb'),
        'flour': (0.50, 'lb'),
        'rice': (1.00, 'lb'),
        'corn meal': (0.75, 'lb'),
        'white rice': (1.00, 'lb'),
        
        # Sugars
        'sugar': (0.75, 'lb'),
        'white sugar': (0.75, 'lb'),
        'brown sugar': (0.85, 'lb'),
        
        # Fats
        'butter': (3.50, 'lb'),
        'butter, softened': (3.50, 'lb'),
        'lard': (2.00, 'lb'),
        'fat': (2.00, 'lb'),
        'butter or margarine': (3.00, 'lb'),
        'butter or oil': (3.00, 'lb'),
        
        # Dairy
        'milk': (3.00, 'gal'),
        'eggs': (3.00, 'dozen'),
        'eggs, beaten': (3.00, 'dozen'),
        'hard-boiled eggs, chopped': (3.00, 'dozen'),
        
        # Proteins
        'ground beef': (4.50, 'lb'),
        'beef or pork, diced': (5.00, 'lb'),
        'dried beef': (8.00, 'lb'),
        'tuna': (1.50, 'can'),
        
        # Vegetables
        'potatoes': (0.50, 'lb'),
        'potatoes, chopped': (0.50, 'lb'),
        'potatoes, sliced thin': (0.50, 'lb'),
        'potatoes, peeled and sliced/cubed': (0.50, 'lb'),
        'onion, chopped': (1.00, 'lb'),
        'onion, sliced thin': (1.00, 'lb'),
        'carrots, sliced': (0.80, 'lb'),
        'celery, chopped': (1.50, 'lb'),
        
        # Canned goods
        'tomatoes, chopped or stewed': (1.00, 'can'),
        'corn, peas, or mixed beans': (1.00, 'can'),
        'creamed corn': (1.00, 'can'),
        "Campbell's chicken noodle soup": (1.50, 'can'),
        
        # Pasta & Noodles
        'egg noodles': (2.00, 'lb'),
        'noodles': (1.50, 'lb'),
        'macaroni': (1.00, 'lb'),
        
        # Beans
        'dried beans': (1.50, 'lb'),
        
        # Spices & Misc
        'salt': (0.50, 'lb'),
        'black pepper': (15.00, 'lb'),
        'cinnamon': (20.00, 'lb'),
        'baking soda': (1.00, 'lb'),
        'baking powder': (3.00, 'lb'),
        'vanilla': (8.00, 'oz'),
        
        # Fruits
        'mashed overripe bananas': (0.30, 'lb'),
        'raisins': (3.00, 'lb'),
    }
    
    added = 0
    for ing_name, ing_id in base_ingredients.items():
        # Try to find a price match
        for price_name, (price, unit) in sample_prices.items():
            if price_name.lower() in ing_name.lower() or ing_name.lower() in price_name.lower():
                # Check if price already exists
                existing = db.session.query(IngredientPrice).filter_by(
                    ingredient_id=ing_id,
                    country_code='USA'
                ).first()
                
                if not existing:
                    new_price = IngredientPrice(
                        ingredient_id=ing_id,
                        price=price,
                        unit=unit,
                        quantity=1.0,
                        country_code='USA',
                        currency='USD'
                    )
                    db.session.add(new_price)
                    added += 1
                break
    
    db.session.commit()
    print(f"\nAdded {added} ingredient prices")