from app import app, db
from price_calculator import calculate_recipe_cost

with app.app_context():
    # Test potato soup (recipe 9)
    cost_data = calculate_recipe_cost(9, db.session)
    
    print("=== Potato Soup Cost Breakdown ===")
    print(f"Total Cost: ${cost_data['total_cost']:.2f}")
    print(f"Cost per Serving: ${cost_data['cost_per_serving']:.2f}")
    print(f"Currency: {cost_data['currency']}")
    
    print("\n--- Ingredient Costs ---")
    for item in cost_data['ingredient_costs']:
        print(f"{item['ingredient']}: ${item['unit_cost']:.2f}")
        print(f"  Quantity: {item['quantity']}")
        print(f"  Price basis: {item['price_basis']}")
    
    print("\n--- Missing Prices ---")
    for item in cost_data['missing_prices']:
        print(f"{item['ingredient']}: {item['quantity']}")
        if 'note' in item:
            print(f"  Note: {item['note']}")