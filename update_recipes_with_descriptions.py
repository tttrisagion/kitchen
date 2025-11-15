import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app, db
from models import Recipe

# Configure database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Map of recipe titles to their short descriptions from index.html
recipe_descriptions = {
    'Hoover Stew': 'A stark lesson in scarcity, community, and the failure of top-down systems.',
    'Beef and Noodles': 'Combining simple assets to create a comfort standard of living.',
    'Zaprezna Soup': 'Creating high value from the most basic, fundamental assets.',
    'Chipped Beef on Toast': 'The economic power of shelf-stable, preserved stores of value.',
    'Potato Soup': 'The "Multiplier Effect": Leveraging a single asset to feed many.',
    'Tuna Fish Stew': 'The principle of efficiency: In a resilient system, nothing is wasted.',
    'Baked Beans': 'Low-Time Preference: The value of patience and slow-cooked assets.',
    'Milk Potatoes': 'How human dignity is expressed through craft and process.',
    'Ash Cakes': 'First Principles: The "Proof-of-Work" of survival and tangible value.',
    'Rice Pudding': 'The "Dignity Premium": A system must account for comfort, not just survival.',
    'Hard Time Pudding': 'Emergent Properties: How free systems create abundance (and sauce).',
    'Banana Bread': 'Transforming "failed" assets into a luxury treat. The Dignity Premium.'
}

def update_recipe_descriptions():
    session = Session()
    try:
        for title, description in recipe_descriptions.items():
            recipe = session.query(Recipe).filter_by(title=title).first()
            if recipe:
                recipe.short_description = description
                print(f"Updated '{title}' with description")
            else:
                print(f"Recipe '{title}' not found in database")
        
        session.commit()
        print("\nSuccessfully updated all recipe descriptions!")
    except Exception as e:
        session.rollback()
        print(f"Error updating descriptions: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_recipe_descriptions()