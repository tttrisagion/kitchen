"""
Migrate all ingredients to standardized format with proper pricing.
"""

from app import app, db
from models import Recipe, Ingredient, RecipeIngredient, IngredientPrice
from standardize_ingredients import (
    parse_ingredient_line, 
    STANDARD_US_PRICES,
    standardize_ingredient_name
)
from decimal import Decimal
import re

def migrate_ingredients():
    """Complete migration to standardized ingredients"""
    
    with app.app_context():
        print("Starting ingredient standardization...")
        
        # Step 1: Create master ingredients if they don't exist
        print("\n1. Creating master ingredients...")
        master_ingredients = {}
        for std_name in STANDARD_US_PRICES.keys():
            # Check if this standard ingredient exists
            ing = db.session.query(Ingredient).filter_by(name=std_name).first()
            if not ing:
                ing = Ingredient(name=std_name)
                db.session.add(ing)
                print(f"  Created: {std_name}")
            master_ingredients[std_name] = ing
        
        db.session.commit()
        
        # Step 2: Add US prices for all standard ingredients
        print("\n2. Adding US prices...")
        prices_added = 0
        for std_name, (price, unit) in STANDARD_US_PRICES.items():
            ing = master_ingredients[std_name]
            
            # Check if price exists
            existing = db.session.query(IngredientPrice).filter_by(
                ingredient_id=ing.id,
                country_code='USA'
            ).first()
            
            if not existing:
                price_entry = IngredientPrice(
                    ingredient_id=ing.id,
                    price=Decimal(str(price)),
                    unit=unit,
                    quantity=Decimal('1.0'),
                    country_code='USA',
                    currency='USD'
                )
                db.session.add(price_entry)
                prices_added += 1
        
        db.session.commit()
        print(f"  Added {prices_added} prices")
        
        # Step 3: Re-parse all recipe ingredients
        print("\n3. Re-parsing recipe ingredients...")
        recipes = db.session.query(Recipe).all()
        
        for recipe in recipes:
            print(f"\n  Processing: {recipe.title}")
            
            # Get current ingredients
            current_ingredients = db.session.query(RecipeIngredient).filter_by(
                recipe_id=recipe.id
            ).all()
            
            # Delete current associations
            for ri in current_ingredients:
                db.session.delete(ri)
            
            db.session.commit()
            
            # Re-parse from original HTML
            from migrate_html_recipes import parse_recipe_html
            import os
            
            # Find the HTML file
            filename = recipe.title.lower().replace(' ', '_') + '.html'
            if os.path.exists(filename):
                recipe_data = parse_recipe_html(filename)
                
                # Track ingredients we've already added for this recipe
                added_ingredients = set()
                
                for ingredient_line in recipe_data['ingredients']:
                    parsed = parse_ingredient_line(ingredient_line)
                    
                    # Find or create the standardized ingredient
                    std_ing = master_ingredients.get(parsed['ingredient'])
                    if not std_ing:
                        # Create non-standard ingredient
                        std_ing = db.session.query(Ingredient).filter_by(
                            name=parsed['ingredient']
                        ).first()
                        if not std_ing:
                            # Truncate long ingredient names
                            ing_name = parsed['ingredient'][:255]
                            std_ing = Ingredient(name=ing_name)
                            db.session.add(std_ing)
                            db.session.flush()
                    
                    # Skip if we already have this ingredient for this recipe
                    if std_ing.id in added_ingredients:
                        print(f"    - Skipping duplicate: {parsed['ingredient']}")
                        continue
                    
                    added_ingredients.add(std_ing.id)
                    
                    # Truncate unit if too long
                    unit = parsed['unit'][:20] if parsed['unit'] else 'each'
                    
                    # Create the association
                    new_ri = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=std_ing.id,
                        quantity=ingredient_line,  # Keep original for display
                        amount=parsed['amount'],
                        unit=unit
                    )
                    db.session.add(new_ri)
                    print(f"    - {parsed['amount']} {unit} {parsed['ingredient']}")
            
        db.session.commit()
        
        # Step 4: Clean up old non-standard ingredients
        print("\n4. Cleaning up...")
        # Mark which ingredients are in use
        used_ingredient_ids = db.session.query(RecipeIngredient.ingredient_id).distinct().all()
        used_ids = [id[0] for id in used_ingredient_ids]
        
        # Delete unused ingredients
        unused = db.session.query(Ingredient).filter(
            ~Ingredient.id.in_(used_ids)
        ).all()
        
        for ing in unused:
            # Also delete any prices
            db.session.query(IngredientPrice).filter_by(ingredient_id=ing.id).delete()
            db.session.delete(ing)
            print(f"  Deleted unused: {ing.name}")
        
        db.session.commit()
        
        print("\n✅ Migration complete!")
        
        # Show summary
        total_ingredients = db.session.query(Ingredient).count()
        total_prices = db.session.query(IngredientPrice).count()
        total_associations = db.session.query(RecipeIngredient).count()
        
        print(f"\nSummary:")
        print(f"  Total ingredients: {total_ingredients}")
        print(f"  Total prices: {total_prices}")
        print(f"  Total recipe-ingredient links: {total_associations}")


if __name__ == "__main__":
    migrate_ingredients()