import os
from migrate_html_recipes import parse_recipe_html, migrate_recipe_to_db
from app import app

# Get all HTML recipe files
html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']

print(f"Found {len(html_files)} recipe files to migrate")

with app.app_context():
    for html_file in html_files:
        print(f"\nProcessing {html_file}...")
        try:
            recipe_data = parse_recipe_html(html_file)
            migrate_recipe_to_db(recipe_data)
        except Exception as e:
            print(f"Error processing {html_file}: {e}")

print("\n✅ Migration complete!")