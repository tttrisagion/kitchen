from app import app, db
from price_calculator import add_sample_prices, bulk_update_parsed_quantities

with app.app_context():
    print("Adding sample prices...")
    prices_added = add_sample_prices(db.session)
    print(f"Added {prices_added} sample prices")
    
    print("\nParsing recipe quantities...")
    result = bulk_update_parsed_quantities(db.session)
    print(f"Updated: {result['updated']}")
    print(f"Failed: {result['failed']}")
    print(f"Total processed: {result['total_processed']}")
    
    print("\nSetup complete!")