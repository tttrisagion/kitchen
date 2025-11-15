from app import db

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.String(500), nullable=True)
    instructions = db.Column(db.Text, nullable=False)
    story = db.Column(db.Text, nullable=True)
    economic_lesson = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    ingredients = db.relationship('RecipeIngredient', back_populates='recipe', lazy=True)
    categories = db.relationship('RecipeCategory', back_populates='recipe', lazy=True)
    equipment_needed = db.relationship('RecipeEquipment', back_populates='recipe', lazy=True)

    def __repr__(self):
        return f'<Recipe {self.title}>'

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    recipes = db.relationship('RecipeIngredient', back_populates='ingredient', lazy=True)

    def __repr__(self):
        return f'<Ingredient {self.name}>'

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    quantity = db.Column(db.String(500), nullable=True) # e.g., "2 cups", "1/2 tsp"
    # Parsed values for calculations
    amount = db.Column(db.Numeric(10, 3), nullable=True) # e.g., 2.0
    unit = db.Column(db.String(20), nullable=True) # e.g., 'cup', 'tsp'

    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipes')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    recipes = db.relationship('RecipeCategory', back_populates='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class RecipeCategory(db.Model):
    __tablename__ = 'recipe_category'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)

    recipe = db.relationship('Recipe', back_populates='categories')
    category = db.relationship('Category', back_populates='recipes')

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    recipes = db.relationship('RecipeEquipment', back_populates='equipment', lazy=True)

    def __repr__(self):
        return f'<Equipment {self.name}>'

class RecipeEquipment(db.Model):
    __tablename__ = 'recipe_equipment'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), primary_key=True)

    recipe = db.relationship('Recipe', back_populates='equipment_needed')
    equipment = db.relationship('Equipment', back_populates='recipes')

class IngredientPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False) # e.g., 1.99
    unit = db.Column(db.String(20), nullable=False) # e.g., 'lb', 'oz', 'cup', 'dozen'
    quantity = db.Column(db.Numeric(10, 3), default=1.0, nullable=False) # e.g., 1.0 for "per pound"
    country_code = db.Column(db.String(50), default='USA', nullable=False) # ISO 3166-1 alpha-3: 'USA', 'GBR', 'CAN'
    currency = db.Column(db.String(3), default='USD', nullable=False) # e.g., USD, EUR, GBP
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    ingredient = db.relationship('Ingredient', backref=db.backref('prices', lazy=True))

    def __repr__(self):
        return f'<IngredientPrice {self.ingredient.name}: {self.price} {self.currency}/{self.quantity} {self.unit} in {self.region}>'
