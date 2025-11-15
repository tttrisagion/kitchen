"""
Standardize all ingredients to a consistent internal format.
Internal format uses UPPERCASE_WITH_UNDERSCORES for ingredient names.
"""

import re
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

# Master list of standardized ingredient names and their variations
INGREDIENT_STANDARDS = {
    # Flour & Grains
    'FLOUR': ['flour', 'all-purpose flour', 'all purpose flour'],
    'RICE': ['rice', 'white rice', 'long grain rice'],
    'CORNMEAL': ['cornmeal', 'corn meal'],
    
    # Sugars
    'SUGAR': ['sugar', 'white sugar', 'granulated sugar'],
    'BROWN_SUGAR': ['brown sugar', 'packed brown sugar'],
    
    # Fats
    'BUTTER': ['butter', 'butter, softened', 'butter or margarine', 'margarine'],
    'LARD': ['lard', 'shortening', 'fat', 'bacon fat', 'bacon grease'],
    'OIL': ['oil', 'vegetable oil', 'cooking oil'],
    
    # Dairy
    'MILK': ['milk', 'whole milk', 'fresh milk'],
    'EGGS': ['eggs', 'egg', 'eggs, beaten', 'beaten eggs', 'large eggs'],
    'HARD_BOILED_EGGS': ['hard-boiled eggs', 'hard boiled eggs', 'hard-boiled eggs, chopped'],
    
    # Proteins
    'GROUND_BEEF': ['ground beef', 'hamburger', 'ground meat'],
    'BEEF': ['beef', 'beef stew meat', 'beef or pork, diced', 'stew meat'],
    'DRIED_BEEF': ['dried beef', 'chipped beef', 'dried beef, "chipped"'],
    'TUNA': ['tuna', 'canned tuna', 'tuna fish', 'canned tuna fish'],
    'HOT_DOGS': ['hot dogs', 'sausage', 'frankfurters', 'meat'],
    
    # Vegetables
    'POTATOES': ['potatoes', 'potato', 'medium potatoes', 'large potatoes'],
    'ONION': ['onion', 'onions', 'yellow onion'],
    'CARROTS': ['carrots', 'carrot'],
    'CELERY': ['celery', 'celery ribs'],
    'GARLIC': ['garlic', 'garlic cloves'],
    
    # Canned Goods
    'CANNED_TOMATOES': ['canned tomatoes', 'tomatoes', 'stewed tomatoes', 'tomatoes, chopped or stewed'],
    'CANNED_CORN': ['corn', 'canned corn', 'whole kernel corn'],
    'CREAMED_CORN': ['creamed corn', 'cream corn'],
    'CANNED_BEANS': ['beans', 'mixed beans', 'canned beans'],
    'CHICKEN_SOUP': ["campbell's chicken noodle soup", 'chicken noodle soup', 'condensed soup'],
    
    # Pasta & Noodles
    'EGG_NOODLES': ['egg noodles', 'wide egg noodles', 'noodles'],
    'MACARONI': ['macaroni', 'elbow macaroni', 'pasta'],
    
    # Beans (dried)
    'DRIED_BEANS': ['dried beans', 'dry beans', 'navy beans', 'pinto beans', 'beans (navy or pinto)'],
    
    # Seasonings & Spices
    'SALT': ['salt', 'table salt'],
    'PEPPER': ['pepper', 'black pepper', 'ground pepper'],
    'CINNAMON': ['cinnamon', 'ground cinnamon'],
    'PAPRIKA': ['paprika'],
    'CARAWAY_SEEDS': ['caraway seeds', 'caraway'],
    
    # Baking
    'BAKING_SODA': ['baking soda', 'soda'],
    'BAKING_POWDER': ['baking powder'],
    'VANILLA': ['vanilla', 'vanilla extract', 'vanilla flavoring'],
    
    # Fruits
    'BANANAS': ['bananas', 'overripe bananas', 'mashed bananas', 'mashed overripe bananas'],
    'RAISINS': ['raisins'],
    
    # Liquids
    'WATER': ['water', 'hot water', 'boiling water', 'warm water'],
    'STOCK': ['stock', 'meat stock', 'beef stock', 'chicken stock', 'broth'],
    
    # Sweeteners
    'HONEY': ['honey'],
    'MOLASSES': ['molasses'],
    'SYRUP': ['syrup', 'maple syrup', 'corn syrup'],
    
    # Bread
    'BREAD': ['bread', 'stale bread', 'toast', 'day-old bread'],
}

# Standard US pricing per unit (rough estimates)
STANDARD_US_PRICES = {
    # Price per pound unless noted
    'FLOUR': (0.50, 'lb'),
    'RICE': (1.00, 'lb'),
    'CORNMEAL': (0.75, 'lb'),
    
    'SUGAR': (0.75, 'lb'),
    'BROWN_SUGAR': (0.85, 'lb'),
    
    'BUTTER': (3.50, 'lb'),
    'LARD': (2.00, 'lb'),
    'OIL': (5.00, 'gal'),  # per gallon
    
    'MILK': (3.50, 'gal'),  # per gallon
    'EGGS': (3.00, 'dozen'),  # per dozen
    'HARD_BOILED_EGGS': (3.50, 'dozen'),  # per dozen (slightly more for pre-cooked)
    
    'GROUND_BEEF': (4.50, 'lb'),
    'BEEF': (5.00, 'lb'),
    'DRIED_BEEF': (8.00, 'lb'),
    'TUNA': (1.50, 'can'),  # per can
    'HOT_DOGS': (3.00, 'lb'),
    
    'POTATOES': (0.50, 'lb'),
    'ONION': (1.00, 'lb'),
    'CARROTS': (0.80, 'lb'),
    'CELERY': (1.50, 'lb'),
    'GARLIC': (3.00, 'lb'),
    
    'CANNED_TOMATOES': (1.00, 'can'),  # per can
    'CANNED_CORN': (1.00, 'can'),  # per can
    'CREAMED_CORN': (1.20, 'can'),  # per can
    'CANNED_BEANS': (1.00, 'can'),  # per can
    'CHICKEN_SOUP': (1.50, 'can'),  # per can
    
    'EGG_NOODLES': (2.00, 'lb'),
    'MACARONI': (1.00, 'lb'),
    
    'DRIED_BEANS': (1.50, 'lb'),
    
    'SALT': (0.50, 'lb'),
    'PEPPER': (15.00, 'lb'),
    'CINNAMON': (20.00, 'lb'),
    'PAPRIKA': (25.00, 'lb'),
    'CARAWAY_SEEDS': (30.00, 'lb'),
    
    'BAKING_SODA': (1.00, 'lb'),
    'BAKING_POWDER': (3.00, 'lb'),
    'VANILLA': (8.00, 'oz'),  # per ounce
    
    'BANANAS': (0.50, 'lb'),
    'RAISINS': (3.00, 'lb'),
    
    'WATER': (0.00, 'gal'),  # Free
    'STOCK': (2.00, 'qt'),  # per quart
    
    'HONEY': (6.00, 'lb'),
    'MOLASSES': (4.00, 'lb'),
    'SYRUP': (5.00, 'lb'),
    
    'BREAD': (2.00, 'loaf'),  # per loaf
}

# Common unit variations to standardize
UNIT_STANDARDS = {
    # Weight
    'lb': ['pound', 'pounds', 'lbs', 'lb'],
    'oz': ['ounce', 'ounces', 'oz'],
    
    # Volume
    'cup': ['cup', 'cups', 'c'],
    'tbsp': ['tablespoon', 'tablespoons', 'tbsp', 'tbs', 'T'],
    'tsp': ['teaspoon', 'teaspoons', 'tsp', 't'],
    'qt': ['quart', 'quarts', 'qt'],
    'pt': ['pint', 'pints', 'pt'],
    'gal': ['gallon', 'gallons', 'gal'],
    'fl_oz': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl. oz'],
    
    # Count/Other
    'each': ['each', 'whole', ''],
    'dozen': ['dozen', 'doz'],
    'can': ['can', 'cans', 'tin'],
    'package': ['package', 'pkg', 'pack'],
    'bag': ['bag', 'bags'],
    'box': ['box', 'boxes'],
    'loaf': ['loaf', 'loaves'],
}


def standardize_ingredient_name(raw_name: str) -> Optional[str]:
    """
    Convert a raw ingredient name to standardized format.
    Returns None if no match found.
    """
    # Clean and lowercase the input
    clean_name = raw_name.strip().lower()
    
    # Remove common qualifiers
    qualifiers = [
        'fresh', 'frozen', 'canned', 'dried', 'optional',
        'if available', 'or similar', 'chopped', 'sliced',
        'diced', 'minced', 'peeled', 'cooked', 'uncooked',
        'melted', 'softened', 'beaten', 'mashed', 'torn',
        'thin', 'thick', 'large', 'medium', 'small'
    ]
    
    for qual in qualifiers:
        clean_name = clean_name.replace(qual, '').strip()
    
    # Remove extra spaces
    clean_name = ' '.join(clean_name.split())
    
    # Try to match against standards
    for standard, variations in INGREDIENT_STANDARDS.items():
        for var in variations:
            if var in clean_name or clean_name in var:
                return standard
    
    return None


def standardize_unit(raw_unit: str) -> Optional[str]:
    """
    Convert a raw unit to standardized format.
    Returns None if no match found.
    """
    clean_unit = raw_unit.strip().lower()
    
    for standard, variations in UNIT_STANDARDS.items():
        for var in variations:
            if clean_unit == var:
                return standard
    
    return None


def parse_ingredient_line(line: str) -> Dict[str, any]:
    """
    Parse a full ingredient line into components.
    Returns dict with: amount, unit, ingredient, original
    """
    import re
    
    original = line.strip()
    
    # Common fraction replacements
    line = line.replace('½', '0.5').replace('¼', '0.25').replace('¾', '0.75')
    line = line.replace('⅓', '0.333').replace('⅔', '0.667')
    line = line.replace('1/2', '0.5').replace('1/4', '0.25').replace('3/4', '0.75')
    line = line.replace('1/3', '0.333').replace('2/3', '0.667')
    
    # Pattern to extract amount and unit
    # Handles: "2 cups", "1-2 tbsp", "15 oz can", etc.
    pattern = r'^([\d\.\s\-/]+)\s*([a-zA-Z]+\.?\s*(?:[a-zA-Z]+)?)\s+(.+)$'
    match = re.match(pattern, line)
    
    # Special case for "can of X"
    if ' can of ' in line.lower():
        parts = line.lower().split(' can of ')
        if len(parts) == 2:
            try:
                amount = float(parts[0].strip())
            except:
                amount = 1.0
            rest = parts[1].strip()
            unit = 'can'
            ingredient = standardize_ingredient_name(rest)
            return {
                'amount': Decimal(str(amount)),
                'unit': unit,
                'ingredient': ingredient or rest.upper().replace(' ', '_'),
                'original': original
            }
    
    if match:
        amount_str = match.group(1).strip()
        unit_str = match.group(2).strip()
        rest = match.group(3).strip()
        
        # Handle ranges (take average)
        if '-' in amount_str:
            parts = amount_str.split('-')
            try:
                low = float(parts[0])
                high = float(parts[1])
                amount = (low + high) / 2
            except:
                amount = 1.0
        else:
            try:
                amount = float(amount_str)
            except:
                amount = 1.0
        
        # Check if unit is actually part of ingredient (e.g., "15 oz can")
        if 'can' in rest.lower() and unit_str in ['oz', 'ounce', 'ounces']:
            rest = f"{unit_str} {rest}"
            unit_str = 'can'
        
        unit = standardize_unit(unit_str)
        ingredient = standardize_ingredient_name(rest)
        
        return {
            'amount': Decimal(str(amount)),
            'unit': unit or unit_str.lower(),
            'ingredient': ingredient or rest.upper().replace(' ', '_'),
            'original': original
        }
    else:
        # No amount/unit pattern found
        ingredient = standardize_ingredient_name(line)
        return {
            'amount': Decimal('1'),
            'unit': 'each',
            'ingredient': ingredient or line.upper().replace(' ', '_'),
            'original': original
        }