"""
Add sample prices for additional countries to test the API
"""

from app import app, db
from models import IngredientPrice, Ingredient
from decimal import Decimal

# Sample conversion rates (rough estimates)
COUNTRY_MULTIPLIERS = {
    'GBR': {'multiplier': 0.8, 'currency': 'GBP'},    # UK prices in GBP
    'CAN': {'multiplier': 1.3, 'currency': 'CAD'},    # Canadian prices in CAD
    'MEX': {'multiplier': 17.0, 'currency': 'MXN'},   # Mexican prices in MXN
}

def add_country_prices():
    with app.app_context():
        # Get all USA prices as base
        usa_prices = db.session.query(IngredientPrice).filter_by(country_code='USA').all()
        
        added = 0
        for country_code, config in COUNTRY_MULTIPLIERS.items():
            for usa_price in usa_prices:
                # Check if price already exists
                existing = db.session.query(IngredientPrice).filter_by(
                    ingredient_id=usa_price.ingredient_id,
                    country_code=country_code
                ).first()
                
                if not existing:
                    # Create adjusted price for this country
                    new_price = IngredientPrice(
                        ingredient_id=usa_price.ingredient_id,
                        price=usa_price.price * Decimal(str(config['multiplier'])),
                        unit=usa_price.unit,
                        quantity=usa_price.quantity,
                        country_code=country_code,
                        currency=config['currency']
                    )
                    db.session.add(new_price)
                    added += 1
        
        db.session.commit()
        print(f"Added {added} prices for {len(COUNTRY_MULTIPLIERS)} countries")

if __name__ == "__main__":
    add_country_prices()