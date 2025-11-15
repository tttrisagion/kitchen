"""
Unit conversion using pint library for accurate conversions.
"""

import pint
from decimal import Decimal
from typing import Optional, Tuple

# Initialize pint's unit registry
ureg = pint.UnitRegistry()

# Define common cooking abbreviations
ureg.define('tbsp = tablespoon')
ureg.define('tsp = teaspoon')
ureg.define('c = cup')
ureg.define('lb = pound')
ureg.define('oz = ounce')
ureg.define('fl_oz = fluid_ounce')
ureg.define('qt = quart')
ureg.define('pt = pint')
ureg.define('gal = gallon')

# Define custom units for food items
ureg.define('can = 15 * fluid_ounce')  # Standard can size
ureg.define('loaf = 1.5 * pound')      # Average loaf weight
ureg.define('dozen = 12 * count')
ureg.define('package = count')          # Generic package
ureg.define('bag = count')              # Generic bag
ureg.define('box = count')              # Generic box
ureg.define('each = count')             # Individual items


def convert_quantity(amount: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Convert a quantity from one unit to another using pint.
    Returns None if conversion is not possible.
    """
    try:
        # Clean up unit strings
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        
        # Handle special cases
        if from_unit == to_unit:
            return amount
        
        # Create quantity and convert
        qty = amount * ureg(from_unit)
        result = qty.to(to_unit)
        
        return result.magnitude
    except (pint.UndefinedUnitError, pint.DimensionalityError):
        return None


def normalize_unit_name(unit: str) -> str:
    """Normalize unit names to pint-compatible format."""
    unit = unit.lower().strip()
    
    # Common replacements
    replacements = {
        'tablespoons': 'tablespoon',
        'tablespoon': 'tablespoon',
        'tbsp': 'tablespoon',
        'tbsps': 'tablespoon',
        'teaspoons': 'teaspoon',
        'teaspoon': 'teaspoon',
        'tsp': 'teaspoon',
        'tsps': 'teaspoon',
        'cups': 'cup',
        'cup': 'cup',
        'pounds': 'pound',
        'pound': 'pound',
        'lbs': 'pound',
        'lb': 'pound',
        'ounces': 'ounce',
        'ounce': 'ounce',
        'oz': 'ounce',
        'fluid ounces': 'fluid_ounce',
        'fluid ounce': 'fluid_ounce',
        'fl oz': 'fluid_ounce',
        'quarts': 'quart',
        'quart': 'quart',
        'qt': 'quart',
        'pints': 'pint',
        'pint': 'pint',
        'pt': 'pint',
        'gallons': 'gallon',
        'gallon': 'gallon',
        'gal': 'gallon',
        'cans': 'can',
        'can': 'can',
        'packages': 'package',
        'package': 'package',
        'pkg': 'package',
        'bags': 'bag',
        'bag': 'bag',
        'boxes': 'box',
        'box': 'box',
        'loaves': 'loaf',
        'loaf': 'loaf',
        'dozen': 'dozen',
        'doz': 'dozen',
        'each': 'each',
        'whole': 'each',
    }
    
    return replacements.get(unit, unit)


def get_standard_conversions() -> dict:
    """Get standard conversions for common cooking measurements."""
    return {
        # Volume conversions
        ('gallon', 'quart'): 4.0,
        ('gallon', 'cup'): 16.0,
        ('quart', 'cup'): 4.0,
        ('quart', 'pint'): 2.0,
        ('pint', 'cup'): 2.0,
        ('cup', 'tablespoon'): 16.0,
        ('cup', 'teaspoon'): 48.0,
        ('tablespoon', 'teaspoon'): 3.0,
        ('cup', 'fluid_ounce'): 8.0,
        
        # Weight conversions
        ('pound', 'ounce'): 16.0,
        ('pound', 'gram'): 453.592,
        ('ounce', 'gram'): 28.3495,
        
        # Special food conversions (approximate)
        ('dozen', 'each'): 12.0,
        ('can', 'fluid_ounce'): 15.0,
        ('loaf', 'pound'): 1.5,
    }


def convert_for_pricing(amount: Decimal, from_unit: str, to_unit: str) -> Optional[Decimal]:
    """
    Convert units specifically for pricing calculations.
    Handles special cases for food items.
    """
    # Normalize units
    from_unit = normalize_unit_name(from_unit)
    to_unit = normalize_unit_name(to_unit)
    
    # Try pint conversion first
    result = convert_quantity(float(amount), from_unit, to_unit)
    if result is not None:
        return Decimal(str(result))
    
    # Handle special food cases
    # For items typically sold by count but measured by weight
    if from_unit == 'each' and to_unit in ['pound', 'ounce']:
        # Approximate weights for common items
        item_weights = {
            'egg': Decimal('0.125'),     # ~2 oz per egg
            'onion': Decimal('0.5'),      # ~8 oz per medium onion
            'potato': Decimal('0.33'),    # ~5 oz per medium potato
            'carrot': Decimal('0.15'),    # ~2.5 oz per carrot
            'apple': Decimal('0.33'),     # ~5 oz per apple
            'banana': Decimal('0.25'),    # ~4 oz per banana
        }
        # Default to 0.25 lb for unknown items
        weight_lb = item_weights.get('default', Decimal('0.25'))
        if to_unit == 'pound':
            return amount * weight_lb
        elif to_unit == 'ounce':
            return amount * weight_lb * 16
    
    return None