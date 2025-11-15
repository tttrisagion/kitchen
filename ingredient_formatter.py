"""
Format ingredients for presentation layer.
Convert internal standardized format to human-readable display.
"""

from decimal import Decimal
from typing import Optional, Dict

# Human-readable names for standardized ingredients
INGREDIENT_DISPLAY_NAMES = {
    'FLOUR': 'flour',
    'RICE': 'rice',
    'CORNMEAL': 'cornmeal',
    'SUGAR': 'sugar',
    'BROWN_SUGAR': 'brown sugar',
    'BUTTER': 'butter',
    'LARD': 'lard',
    'OIL': 'vegetable oil',
    'MILK': 'milk',
    'EGGS': 'eggs',
    'HARD_BOILED_EGGS': 'hard-boiled eggs',
    'GROUND_BEEF': 'ground beef',
    'BEEF': 'beef',
    'DRIED_BEEF': 'dried beef',
    'TUNA': 'tuna',
    'HOT_DOGS': 'hot dogs',
    'POTATOES': 'potatoes',
    'ONION': 'onion',
    'CARROTS': 'carrots',
    'CELERY': 'celery',
    'GARLIC': 'garlic',
    'CANNED_TOMATOES': 'canned tomatoes',
    'CANNED_CORN': 'corn',
    'CREAMED_CORN': 'creamed corn',
    'CANNED_BEANS': 'beans',
    'CHICKEN_SOUP': 'chicken noodle soup',
    'EGG_NOODLES': 'egg noodles',
    'MACARONI': 'macaroni',
    'DRIED_BEANS': 'dried beans',
    'SALT': 'salt',
    'PEPPER': 'pepper',
    'CINNAMON': 'cinnamon',
    'PAPRIKA': 'paprika',
    'CARAWAY_SEEDS': 'caraway seeds',
    'BAKING_SODA': 'baking soda',
    'BAKING_POWDER': 'baking powder',
    'VANILLA': 'vanilla extract',
    'BANANAS': 'bananas',
    'RAISINS': 'raisins',
    'WATER': 'water',
    'STOCK': 'stock',
    'HONEY': 'honey',
    'MOLASSES': 'molasses',
    'SYRUP': 'syrup',
    'BREAD': 'bread',
}

# Unit display names
UNIT_DISPLAY = {
    'cup': 'cup',
    'cups': 'cups',
    'tbsp': 'tablespoon',
    'tsp': 'teaspoon',
    'lb': 'pound',
    'oz': 'ounce',
    'fl_oz': 'fl oz',
    'qt': 'quart',
    'pt': 'pint',
    'gal': 'gallon',
    'can': 'can',
    'package': 'package',
    'bag': 'bag',
    'box': 'box',
    'loaf': 'loaf',
    'dozen': 'dozen',
    'each': '',
}


def format_amount(amount: Decimal) -> str:
    """Format amount for display with fractions."""
    if amount is None:
        return ""
    
    # Common fractions
    fractions = {
        Decimal('0.25'): '¼',
        Decimal('0.33'): '⅓',
        Decimal('0.333'): '⅓',
        Decimal('0.5'): '½',
        Decimal('0.66'): '⅔',
        Decimal('0.667'): '⅔',
        Decimal('0.75'): '¾',
    }
    
    # Check for exact matches
    if amount in fractions:
        return fractions[amount]
    
    # Check for mixed numbers (e.g., 1.5 -> 1½)
    whole = int(amount)
    if whole > 0:
        fraction = amount - whole
        if fraction in fractions:
            return f"{whole} {fractions[fraction]}"
    
    # Format as decimal, removing unnecessary zeros
    if amount == amount.to_integral_value():
        return str(int(amount))
    else:
        return str(amount).rstrip('0').rstrip('.')


def format_unit(amount: Decimal, unit: str) -> str:
    """Format unit for display, handling pluralization."""
    if not unit or unit == 'each':
        return ''
    
    display_unit = UNIT_DISPLAY.get(unit, unit)
    
    # Handle pluralization for common units
    if amount != 1:
        singular_to_plural = {
            'cup': 'cups',
            'tablespoon': 'tablespoons',
            'teaspoon': 'teaspoons',
            'pound': 'pounds',
            'ounce': 'ounces',
            'quart': 'quarts',
            'pint': 'pints',
            'gallon': 'gallons',
            'can': 'cans',
            'package': 'packages',
            'bag': 'bags',
            'box': 'boxes',
            'loaf': 'loaves',
        }
        display_unit = singular_to_plural.get(display_unit, display_unit)
    
    return display_unit


def format_ingredient_name(ingredient_name: str) -> str:
    """Format ingredient name for display."""
    # Use display name if available
    if ingredient_name in INGREDIENT_DISPLAY_NAMES:
        return INGREDIENT_DISPLAY_NAMES[ingredient_name]
    
    # Otherwise, clean up the raw name
    # Convert UNDERSCORE_CASE to readable format
    if '_' in ingredient_name and ingredient_name.isupper():
        return ingredient_name.lower().replace('_', ' ')
    
    return ingredient_name


def format_recipe_ingredient(recipe_ingredient) -> str:
    """
    Format a RecipeIngredient object for display.
    Falls back to original quantity if parsing failed.
    """
    # If we have parsed amount and unit, use them
    if recipe_ingredient.amount is not None and recipe_ingredient.unit is not None:
        amount_str = format_amount(recipe_ingredient.amount)
        unit_str = format_unit(recipe_ingredient.amount, recipe_ingredient.unit)
        ingredient_str = format_ingredient_name(recipe_ingredient.ingredient.name)
        
        # Build the display string
        parts = []
        if amount_str:
            parts.append(amount_str)
        if unit_str:
            parts.append(unit_str)
        parts.append(ingredient_str)
        
        return ' '.join(parts)
    else:
        # Fall back to original quantity string
        return recipe_ingredient.quantity or recipe_ingredient.ingredient.name


def format_price(price: Decimal, currency: str = 'USD') -> str:
    """Format price for display."""
    if currency == 'USD':
        return f"${price:.2f}"
    else:
        return f"{price:.2f} {currency}"


def format_recipe_cost_breakdown(cost_data: Dict) -> Dict:
    """Format the cost breakdown for display."""
    if not cost_data:
        return None
    
    formatted = {
        'recipe_title': cost_data.get('recipe_title'),
        'total_cost': format_price(Decimal(str(cost_data.get('total_cost', 0)))),
        'cost_per_serving': format_price(Decimal(str(cost_data.get('cost_per_serving', 0)))),
        'servings': cost_data.get('servings', 4),
        'currency': cost_data.get('currency', 'USD'),
        'ingredient_costs': []
    }
    
    for item in cost_data.get('ingredient_costs', []):
        formatted['ingredient_costs'].append({
            'ingredient': item['ingredient'],
            'quantity': item['quantity'],
            'cost': format_price(Decimal(str(item['unit_cost']))),
            'price_basis': item.get('price_basis', '')
        })
    
    formatted['missing_prices'] = cost_data.get('missing_prices', [])
    
    return formatted