from app import app, db

from app.models import Ingredient, Product

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Ingredient': Ingredient, 'Product': Product}
