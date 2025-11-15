import os
from migrate_html_recipes import parse_recipe_html, migrate_recipe_to_db
from app import app

# Test parsing first
print("Testing HTML parsing...")
test_files = ['banana_bread.html', 'hoover_stew.html']

for file in test_files:
    print(f"\n=== Testing {file} ===")
    data = parse_recipe_html(file)
    print(f"Title: {data['title']}")
    print(f"Short description: {data.get('short_description', 'NONE')}")
    print(f"Story length: {len(data['story']) if data['story'] else 0} chars")
    print(f"Economic lesson length: {len(data['economic_lesson']) if data['economic_lesson'] else 0} chars")
    print(f"Ingredients: {len(data['ingredients'])} items")
    
    if data['story']:
        print(f"Story preview: {data['story'][:100]}...")
    if data['economic_lesson']:
        print(f"Lesson preview: {data['economic_lesson'][:100]}...")

# Now test migration
print("\n\n=== Testing Migration ===")
with app.app_context():
    for file in test_files:
        print(f"\nMigrating {file}...")
        data = parse_recipe_html(file)
        migrate_recipe_to_db(data)