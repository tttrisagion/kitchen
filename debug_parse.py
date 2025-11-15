from bs4 import BeautifulSoup
import re

def debug_parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    print(f"\n=== Parsing {file_path} ===")
    
    # Check for h1 title
    h1 = soup.find('h1')
    print(f"Title: {h1.get_text(strip=True) if h1 else 'NOT FOUND'}")
    
    # Debug story section
    print("\n--- Looking for Story ---")
    story_h2 = soup.find('h2', string=re.compile(r'The Story', re.IGNORECASE))
    if story_h2:
        print(f"Found story h2: {story_h2.get_text()}")
        # Try different methods to find the content
        
        # Method 1: Next sibling div
        story_div = story_h2.find_next_sibling('div')
        if story_div:
            print(f"Found div after h2, classes: {story_div.get('class')}")
            p_tags = story_div.find_all('p')
            print(f"Found {len(p_tags)} paragraphs in div")
            
        # Method 2: Find next section
        story_section = story_h2.find_parent('section')
        if story_section:
            print(f"Found parent section")
            p_tags = story_section.find_all('p')
            print(f"Found {len(p_tags)} paragraphs in section")
            for i, p in enumerate(p_tags[:2]):  # Show first 2 paragraphs
                print(f"  P{i}: {p.get_text()[:100]}...")
    else:
        print("Story h2 NOT FOUND")
    
    # Debug economic lesson section
    print("\n--- Looking for Economic Lesson ---")
    econ_h2 = soup.find('h2', string=re.compile(r'The Economic Lesson', re.IGNORECASE))
    if econ_h2:
        print(f"Found economic lesson h2: {econ_h2.get_text()}")
        # Try different methods
        
        # Method 1: Next sibling div
        econ_div = econ_h2.find_next_sibling('div')
        if econ_div:
            print(f"Found div after h2, classes: {econ_div.get('class')}")
            p_tags = econ_div.find_all('p')
            print(f"Found {len(p_tags)} paragraphs in div")
            
        # Method 2: Find next section
        econ_section = econ_h2.find_parent('section')
        if econ_section:
            print(f"Found parent section")
            p_tags = econ_section.find_all('p')
            print(f"Found {len(p_tags)} paragraphs in section")
            for i, p in enumerate(p_tags[:2]):  # Show first 2 paragraphs
                print(f"  P{i}: {p.get_text()[:100]}...")
    else:
        print("Economic lesson h2 NOT FOUND")

# Test with a few files
test_files = ['banana_bread.html', 'hoover_stew.html', 'ash_cakes.html']
for file in test_files:
    debug_parse_html(file)