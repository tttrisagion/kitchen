"""
Unit conversion utilities for recipe ingredients.
Uses standard imperial units as the base and converts to other systems on demand.
"""

from decimal import Decimal
from typing import Dict, Optional, Tuple

# Base unit conversions (everything stored as imperial in DB)
IMPERIAL_TO_METRIC = {
    # Weight
    'lb': ('kg', Decimal('0.453592')),
    'oz': ('g', Decimal('28.3495')),
    # Volume
    'cup': ('ml', Decimal('236.588')),
    'fl oz': ('ml', Decimal('29.5735')),
    'tbsp': ('ml', Decimal('14.7868')),
    'tsp': ('ml', Decimal('4.92892')),
    'gal': ('l', Decimal('3.78541')),
    'qt': ('l', Decimal('0.946353')),
    'pt': ('ml', Decimal('473.176')),
}

# Common unit abbreviations and variations
UNIT_ALIASES = {
    # Weight
    'pound': 'lb',
    'pounds': 'lb',
    'lbs': 'lb',
    'ounce': 'oz',
    'ounces': 'oz',
    # Volume
    'cups': 'cup',
    'tablespoon': 'tbsp',
    'tablespoons': 'tbsp',
    'teaspoon': 'tsp',
    'teaspoons': 'tsp',
    'gallon': 'gal',
    'gallons': 'gal',
    'quart': 'qt',
    'quarts': 'qt',
    'pint': 'pt',
    'pints': 'pt',
    # Count
    'dozen': 'dozen',
    'doz': 'dozen',
}

# Unit relationships within imperial system
IMPERIAL_CONVERSIONS = {
    # Weight
    ('lb', 'oz'): Decimal('16'),
    # Volume
    ('gal', 'qt'): Decimal('4'),
    ('qt', 'pt'): Decimal('2'),
    ('pt', 'cup'): Decimal('2'),
    ('cup', 'fl oz'): Decimal('8'),
    ('fl oz', 'tbsp'): Decimal('2'),
    ('tbsp', 'tsp'): Decimal('3'),
    # Additional conversions
    ('gal', 'cup'): Decimal('16'),  # 1 gal = 16 cups
    ('qt', 'cup'): Decimal('4'),    # 1 qt = 4 cups
    ('cup', 'tbsp'): Decimal('16'), # 1 cup = 16 tbsp
}


def normalize_unit(unit: str) -> str:
    """Normalize unit to standard form."""
    unit_lower = unit.lower().strip()
    return UNIT_ALIASES.get(unit_lower, unit_lower)


def convert_imperial_to_imperial(amount: Decimal, from_unit: str, to_unit: str) -> Optional[Decimal]:
    """Convert between imperial units."""
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)
    
    if from_unit == to_unit:
        return amount
    
    # Direct conversion
    if (from_unit, to_unit) in IMPERIAL_CONVERSIONS:
        return amount * IMPERIAL_CONVERSIONS[(from_unit, to_unit)]
    
    # Reverse conversion
    if (to_unit, from_unit) in IMPERIAL_CONVERSIONS:
        return amount / IMPERIAL_CONVERSIONS[(to_unit, from_unit)]
    
    return None


def convert_to_metric(amount: Decimal, imperial_unit: str) -> Optional[Tuple[Decimal, str]]:
    """Convert imperial unit to metric equivalent."""
    imperial_unit = normalize_unit(imperial_unit)
    
    if imperial_unit in IMPERIAL_TO_METRIC:
        metric_unit, factor = IMPERIAL_TO_METRIC[imperial_unit]
        return amount * factor, metric_unit
    
    return None


def format_amount(amount: Decimal) -> str:
    """Format amount for display, handling fractions nicely."""
    # Remove trailing zeros
    normalized = amount.normalize()
    
    # If it's a whole number, return as int
    if normalized == normalized.to_integral_value():
        return str(int(normalized))
    
    # Common fractions
    common_fractions = {
        Decimal('0.25'): '¼',
        Decimal('0.33'): '⅓',
        Decimal('0.5'): '½',
        Decimal('0.66'): '⅔',
        Decimal('0.67'): '⅔',
        Decimal('0.75'): '¾',
    }
    
    # Check if it's close to a common fraction
    for frac_val, frac_str in common_fractions.items():
        if abs(normalized - frac_val) < Decimal('0.01'):
            return frac_str
    
    # Check if it's 1 + fraction
    whole_part = int(normalized)
    if whole_part > 0:
        frac_part = normalized - whole_part
        for frac_val, frac_str in common_fractions.items():
            if abs(frac_part - frac_val) < Decimal('0.01'):
                return f"{whole_part} {frac_str}"
    
    # Otherwise return with up to 2 decimal places
    return f"{normalized:.2f}".rstrip('0').rstrip('.')


def parse_quantity_string(quantity_str: str) -> Optional[Tuple[Decimal, str]]:
    """
    Parse a quantity string like "2 cups" or "1/2 tsp" into amount and unit.
    Returns None if parsing fails.
    """
    import re
    
    # Pattern to match various formats
    pattern = r'^\s*([\d\s\./\-]+)\s*(.+?)\s*$'
    match = re.match(pattern, quantity_str)
    
    if not match:
        return None
    
    amount_str, unit = match.groups()
    
    # Handle fractions
    try:
        # Replace common fraction representations
        amount_str = amount_str.replace('½', '0.5').replace('¼', '0.25').replace('¾', '0.75')
        amount_str = amount_str.replace('⅓', '0.33').replace('⅔', '0.67')
        
        # Handle "1 1/2" style
        if ' ' in amount_str and '/' in amount_str:
            parts = amount_str.split(' ')
            whole = Decimal(parts[0])
            frac_parts = parts[1].split('/')
            frac = Decimal(frac_parts[0]) / Decimal(frac_parts[1])
            amount = whole + frac
        # Handle "1/2" style
        elif '/' in amount_str:
            parts = amount_str.split('/')
            amount = Decimal(parts[0]) / Decimal(parts[1])
        else:
            amount = Decimal(amount_str.strip())
        
        unit = normalize_unit(unit)
        return amount, unit
    except:
        return None