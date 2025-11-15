from app import app, db
from models import Ingredient

def list_all_ingredients():
    with app.app_context():
        ingredients = Ingredient.query.all()
        for ingredient in ingredients:
            print(ingredient.name)

if __name__ == '__main__':
    list_all_ingredients()
