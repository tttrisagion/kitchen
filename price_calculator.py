"""
Recipe price calculator using ingredient prices and unit conversions.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from models import Recipe, RecipeIngredient, IngredientPrice
from unit_converter import parse_quantity_string, format_amount
from pint_converter import convert_for_pricing, normalize_unit_name


def calculate_recipe_cost(recipe_id: int, session: Session, country_code: str = 'USA', servings: int = 4) -> Dict:
    """
    Calculate the total cost of a recipe and cost per serving.
    
    Returns a dict with:
    - total_cost: Total cost of the recipe
    - cost_per_serving: Cost per serving
    - missing_prices: List of ingredients without price data
    - ingredient_costs: Breakdown of costs per ingredient
    """
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        return None
    
    total_cost = Decimal('0')
    ingredient_costs = []
    missing_prices = []
    
    for ri in recipe.ingredients:
        ingredient = ri.ingredient
        
        # Try to parse the quantity if not already parsed
        if ri.amount is None or ri.unit is None:
            parsed = parse_quantity_string(ri.quantity) if ri.quantity else None
            if parsed:
                ri.amount, ri.unit = parsed
                session.add(ri)
        
        if ri.amount is None or ri.unit is None:
            missing_prices.append({
                'ingredient': ingredient.name,
                'quantity': ri.quantity or 'Unknown quantity'
            })
            continue
        
        # Find price for this ingredient in the specified country
        price_info = session.query(IngredientPrice).filter_by(
            ingredient_id=ingredient.id,
            country_code=country_code
        ).first()
        
        if not price_info:
            # Try USA as fallback
            if country_code != 'USA':
                price_info = session.query(IngredientPrice).filter_by(
                    ingredient_id=ingredient.id,
                    country_code='USA'
                ).first()
        
        if not price_info:
            missing_prices.append({
                'ingredient': ingredient.name,
                'quantity': ri.quantity
            })
            continue
        
        # Calculate cost for this ingredient
        recipe_unit = ri.unit if ri.unit else 'each'
        recipe_amount = ri.amount
        
        # Clean up compound units like "cups water"
        if ' ' in recipe_unit:
            recipe_unit = recipe_unit.split()[0]
        
        # Normalize unit names
        recipe_unit = normalize_unit_name(recipe_unit)
        price_unit = normalize_unit_name(price_info.unit)
        
        # Convert recipe unit to price unit using pint
        converted_amount = convert_for_pricing(recipe_amount, recipe_unit, price_unit)
        
        if converted_amount is None:
            # Units not compatible (e.g., weight vs volume)
            missing_prices.append({
                'ingredient': ingredient.name,
                'quantity': ri.quantity,
                'note': f"Cannot convert {ri.unit} to {price_info.unit}"
            })
            continue
        
        # Calculate cost: (amount needed / price quantity) * price
        ingredient_cost = (converted_amount / price_info.quantity) * price_info.price
        total_cost += ingredient_cost
        
        ingredient_costs.append({
            'ingredient': ingredient.name,
            'quantity': ri.quantity,
            'unit_cost': float(ingredient_cost),
            'price_basis': f"{format_amount(price_info.price)} {price_info.currency} per {format_amount(price_info.quantity)} {price_info.unit}"
        })
    
    session.commit()  # Save any parsed amounts
    
    return {
        'recipe_title': recipe.title,
        'country_code': country_code,
        'servings': servings,
        'total_cost': float(total_cost),
        'cost_per_serving': float(total_cost / servings) if servings > 0 else 0,
        'currency': price_info.currency if price_info else 'USD',
        'ingredient_costs': ingredient_costs,
        'missing_prices': missing_prices
    }


def bulk_update_parsed_quantities(session: Session):
    """
    Parse all recipe ingredient quantities and store the parsed values.
    This makes future calculations faster.
    """
    updated = 0
    failed = 0
    
    recipe_ingredients = session.query(RecipeIngredient).filter(
        (RecipeIngredient.amount == None) | (RecipeIngredient.unit == None)
    ).all()
    
    for ri in recipe_ingredients:
        if ri.quantity:
            parsed = parse_quantity_string(ri.quantity)
            if parsed:
                ri.amount, ri.unit = parsed
                updated += 1
            else:
                failed += 1
    
    session.commit()
    
    return {
        'updated': updated,
        'failed': failed,
        'total_processed': updated + failed
    }


def add_sample_prices(session: Session):
    """
    Add some sample ingredient prices for testing.
    These are rough estimates in USD per pound/unit.
    """
    sample_prices = [
        # Basics
        ('all-purpose flour', Decimal('0.50'), 'lb'),
        ('sugar', Decimal('0.75'), 'lb'),
        ('brown sugar', Decimal('0.85'), 'lb'),
        ('salt', Decimal('0.50'), 'lb'),
        ('butter', Decimal('3.50'), 'lb'),
        ('milk', Decimal('3.00'), 'gal'),
        ('eggs', Decimal('3.00'), 'dozen'),
        
        # Proteins
        ('ground beef', Decimal('4.50'), 'lb'),
        ('beef stew meat', Decimal('5.00'), 'lb'),
        ('canned tuna', Decimal('1.50'), 'can'),
        ('dried beef', Decimal('8.00'), 'lb'),
        
        # Produce
        ('potatoes', Decimal('0.50'), 'lb'),
        ('onion', Decimal('1.00'), 'lb'),
        ('overripe bananas', Decimal('0.30'), 'lb'),
        
        # Pantry
        ('rice', Decimal('1.00'), 'lb'),
        ('dried beans', Decimal('1.50'), 'lb'),
        ('canned tomatoes', Decimal('1.00'), 'can'),
        ('macaroni', Decimal('1.00'), 'lb'),
        ('egg noodles', Decimal('2.00'), 'lb'),
        
        # Spices/Misc
        ('black pepper', Decimal('15.00'), 'lb'),
        ('cinnamon', Decimal('20.00'), 'lb'),
        ('baking soda', Decimal('1.00'), 'lb'),
        ('corn meal', Decimal('0.75'), 'lb'),
    ]
    
    from models import Ingredient
    
    added = 0
    for name, price, unit in sample_prices:
        ingredient = session.query(Ingredient).filter_by(name=name).first()
        if ingredient:
            existing_price = session.query(IngredientPrice).filter_by(
                ingredient_id=ingredient.id,
                country_code='USA'
            ).first()
            
            if not existing_price:
                price_entry = IngredientPrice(
                    ingredient_id=ingredient.id,
                    price=price,
                    unit=unit,
                    quantity=Decimal('1.0'),
                    country_code='USA',
                    currency='USD'
                )
                session.add(price_entry)
                added += 1
    
    session.commit()
    return added