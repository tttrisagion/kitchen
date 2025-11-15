import os
from bs4 import BeautifulSoup

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
    'ash_cakes.html': 'Resilience at its purest: creating sustenance from almost nothing.',
    'banana_bread.html': 'Transforming "waste" into wealth through ingenuity and patience.',
    'hard_time_pudding.html': 'Finding sweetness in scarcity: the creativity of constraint.',
    'rice_pudding.html': 'Simple ingredients elevated: turning staples into comfort.'
}

def extract_descriptions_from_index():
    """Extract recipe descriptions directly from index.html"""
    with open('index.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    descriptions = {}
    
    # Find all recipe cards
    recipe_links = soup.find_all('a', href=True)
    for link in recipe_links:
        href = link.get('href', '')
        if href.endswith('.html') and href != 'index.html':
            # Find the description paragraph within this card
            p_tag = link.find('p', class_='mt-2 text-lg')
            if p_tag:
                description = p_tag.get_text(strip=True)
                descriptions[href] = description
    
    return descriptions

if __name__ == "__main__":
    # Extract from index.html
    descriptions = extract_descriptions_from_index()
    
    print("Recipe descriptions found:")
    for recipe, desc in descriptions.items():
        print(f"'{recipe}': '{desc}'")
    
    # Also print the hardcoded ones for comparison
    print("\n\nHardcoded descriptions:")
    for recipe, desc in recipe_descriptions.items():
        print(f"'{recipe}': '{desc}'")