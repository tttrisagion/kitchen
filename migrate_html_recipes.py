import os
import re
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import db, app
from models import Recipe, Ingredient, RecipeIngredient, Category, RecipeCategory, Equipment, RecipeEquipment

# Configure database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Map of recipe files to their short descriptions from index.html
recipe_descriptions = {
    'hoover_stew.html': 'A stark lesson in scarcity, community, and the failure of top-down systems.',
    'beef_and_noodles.html': 'Combining simple assets to create a comfort standard of living.',
    'zaprezna_soup.html': 'Creating high value from the most basic, fundamental assets.',
    'chipped_beef.html': 'The economic power of shelf-stable, preserved stores of value.',
    'potato_soup.html': 'The "Multiplier Effect": Leveraging a single asset to feed many.',
    'tuna_stew.html': 'The principle of efficiency: In a resilient system, nothing is wasted.',
    'baked_beans.html': 'Low-Time Preference: The value of patience and slow-cooked assets.',
    'milk_potatoes.html': 'How human dignity is expressed through craft and process.',
    'ash_cakes.html': 'First Principles: The "Proof-of-Work" of survival and tangible value.',
    'rice_pudding.html': 'The "Dignity Premium": A system must account for comfort, not just survival.',
    'hard_time_pudding.html': 'Emergent Properties: How free systems create abundance (and sauce).',
    'banana_bread.html': 'Transforming "failed" assets into a luxury treat. The Dignity Premium.'
}

def parse_recipe_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else os.path.basename(file_path).replace('.html', '').replace('_', ' ').title()
    
    # Get short description from our mapping
    filename = os.path.basename(file_path)
    short_description = recipe_descriptions.get(filename)

    ingredients_list = []
    ingredients_section = soup.find('h3', string=re.compile(r'Ingredients', re.IGNORECASE))
    if ingredients_section:
        ul = ingredients_section.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li'):
                ingredients_list.append(li.get_text(strip=True))

    instructions_list = []
    instructions_section = soup.find('h3', string=re.compile(r'Instructions', re.IGNORECASE))
    if instructions_section:
        ol = instructions_section.find_next_sibling('ol')
        if ol:
            for li in ol.find_all('li'):
                instructions_list.append(li.get_text(strip=True))
    
    instructions = "\n".join(instructions_list)

    # Extract 'The Story'
    story_content = []
    story_section_h2 = soup.find('h2', string=re.compile(r'The Story', re.IGNORECASE))
    if story_section_h2:
        story_div = story_section_h2.find_next_sibling('div')
        if story_div:
            for p_tag in story_div.find_all('p'):
                story_content.append(p_tag.get_text(strip=True))
    story = "\n\n".join(story_content) # Join paragraphs with double newline

    # Extract 'The Economic Lesson'
    economic_lesson_content = []
    economic_lesson_section_h2 = soup.find('h2', string=re.compile(r'The Economic Lesson', re.IGNORECASE))
    if economic_lesson_section_h2:
        economic_lesson_div = economic_lesson_section_h2.find_next_sibling('div')
        if economic_lesson_div:
            for p_tag in economic_lesson_div.find_all('p'):
                economic_lesson_content.append(p_tag.get_text(strip=True))
    economic_lesson = "\n\n".join(economic_lesson_content) # Join paragraphs with double newline


    return {
        'title': title,
        'short_description': short_description,
        'ingredients': ingredients_list,
        'instructions': instructions,
        'story': story,
        'economic_lesson': economic_lesson
    }

def convert_amount_to_numeric(amount_str):
    if not amount_str:
        return None
    amount_str = amount_str.strip()
    if '-' in amount_str:
        low, high = amount_str.split('-')
        try:
            return (float(low) + float(high)) / 2
        except ValueError:
            return None
    
    fraction_map = {
        '¼': 0.25, '½': 0.5, '¾': 0.75, '⅓': 1/3, '⅔': 2/3, '⅕': 1/5, '⅖': 2/5, '⅗': 3/5, '⅘': 4/5, '⅙': 1/6, '⅚': 5/6, '⅛': 1/8, '⅜': 3/8, '⅝': 5/8, '⅞': 7/8
    }
    if amount_str in fraction_map:
        return fraction_map[amount_str]
    
    try:
        return float(amount_str)
    except ValueError:
        # Handle cases like "1 1/2"
        if ' ' in amount_str:
            parts = amount_str.split(' ')
            if len(parts) == 2 and parts[1] in fraction_map:
                return float(parts[0]) + fraction_map[parts[1]]
        return None

def migrate_recipe_to_db(recipe_data):
    session = Session()
    try:
        # Check if recipe already exists
        existing_recipe = session.query(Recipe).filter_by(title=recipe_data['title']).first()
        if existing_recipe:
            # Update existing recipe with new fields
            existing_recipe.short_description = recipe_data.get('short_description')
            existing_recipe.story = recipe_data['story']
            existing_recipe.economic_lesson = recipe_data['economic_lesson']
            existing_recipe.instructions = recipe_data['instructions']

            session.query(RecipeIngredient).filter_by(recipe_id=existing_recipe.id).delete()
            session.flush()

            for item in recipe_data['ingredients']:
                # Improved regex to capture amount, unit, and ingredient name
                match = re.match(r'([\d\s\./\-¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]+)?\s*(cup|teaspoon|tablespoon|oz|g|lb|pinch|dash|large|medium|small|clove|slice|whole|can|package|bunch|head|stalk|sprig|fillet|piece|strip|slice|gram|milliliter|liter|pound|ounce|fluid ounce|quart|gallon|pint)s?\b\s*(.*)', item, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).strip() if match.group(1) else None
                    unit = match.group(2).strip() if match.group(2) else None
                    ingredient_name = match.group(3).strip()
                else:
                    amount_str = None
                    unit = None
                    ingredient_name = item.strip()

                amount = convert_amount_to_numeric(amount_str)

                ingredient = session.query(Ingredient).filter_by(name=ingredient_name).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name)
                    session.add(ingredient)
                    session.flush()

                recipe_ingredient = RecipeIngredient(
                    recipe_id=existing_recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=item,
                    amount=amount,
                    unit=unit
                )
                session.add(recipe_ingredient)

            print(f"Successfully updated '{existing_recipe.title}'")
            print(f"  - Story: {len(existing_recipe.story) if existing_recipe.story else 0} chars")
            print(f"  - Economic Lesson: {len(existing_recipe.economic_lesson) if existing_recipe.economic_lesson else 0} chars")
            print(f"  - Short Description: {existing_recipe.short_description}")
        else:
            new_recipe = Recipe(
                title=recipe_data['title'],
                short_description=recipe_data.get('short_description'),
                instructions=recipe_data['instructions'],
                story=recipe_data['story'],
                economic_lesson=recipe_data['economic_lesson'],
                image_url=None
            )
            session.add(new_recipe)
            session.flush()

            for item in recipe_data['ingredients']:
                match = re.match(r'([\d\s\./\-¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]+)?\s*(cup|teaspoon|tablespoon|oz|g|lb|pinch|dash|large|medium|small|clove|slice|whole|can|package|bunch|head|stalk|sprig|fillet|piece|strip|slice|gram|milliliter|liter|pound|ounce|fluid ounce|quart|gallon|pint)s?\b\s*(.*)', item, re.IGNORECASE)
                if match:
                    amount_str = match.group(1).strip() if match.group(1) else None
                    unit = match.group(2).strip() if match.group(2) else None
                    ingredient_name = match.group(3).strip()
                else:
                    amount_str = None
                    unit = None
                    ingredient_name = item.strip()
                
                amount = convert_amount_to_numeric(amount_str)

                ingredient = session.query(Ingredient).filter_by(name=ingredient_name).first()
                if not ingredient:
                    ingredient = Ingredient(name=ingredient_name)
                    session.add(ingredient)
                    session.flush()

                recipe_ingredient = RecipeIngredient(
                    recipe_id=new_recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=item,
                    amount=amount,
                    unit=unit
                )
                session.add(recipe_ingredient)
            
            print(f"Successfully migrated '{new_recipe.title}'")
            print(f"  - Story: {len(new_recipe.story) if new_recipe.story else 0} chars")
            print(f"  - Economic Lesson: {len(new_recipe.economic_lesson) if new_recipe.economic_lesson else 0} chars")
            print(f"  - Short Description: {new_recipe.short_description}")
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error migrating '{recipe_data['title']}': {e}")
    finally:
        session.close()
