from app import db

from flask import flash

# Association table ingr
association_table_ingredients = db.Table('associationIngr', db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'))
)

# Association table allergies
association_table_allergies = db.Table('associationProd', db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('allergies_id', db.Integer, db.ForeignKey('allergies.id'))
)

# Association table for bundles
association_table_bundle = db.Table('associationBundle', db.Model.metadata,
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('bundle_id', db.Integer, db.ForeignKey('bundle.id'))
)

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True)
    price = db.Column(db.String(10), index=True)

    small = db.Column(db.Boolean)
    medium = db.Column(db.Boolean)
    large = db.Column(db.Boolean)

    # Path is an uuid of length 36, but the real size takes into account the extension length
    jpeg_path = db.Column(db.String(42))
    
    ingredients = db.relationship("Ingredient", secondary=association_table_ingredients,
        backref=db.backref('products', lazy='dynamic'), lazy='dynamic')

    allergies = db.relationship("Allergies", secondary=association_table_allergies,
        backref=db.backref('products', lazy='dynamic'), lazy='dynamic')
    
    bundles = db.relationship("Bundle", secondary=association_table_bundle,
        backref=db.backref('products', lazy='dynamic'), lazy='dynamic')

    def get_discount(self):
        return str(round( float(self.price) * 20 / 100 ))

    @property
    def serialize(self):
        return{
            'id': self.id,
            'jpeg_path': self.jpeg_path,
            'title': self.title,
            'price': self.price,
            'discount': self.get_discount(),
            'new_price': (float(self.price) - float(self.get_discount())),
        }


    def __repr__(self):
        return f'Product {self.title} with id {self.id}'

class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return f'{self.name}'

class Allergies(db.Model):
    __tablename__ = 'allergies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return f'Allergy {self.name} with id {self.id}'

class Bundle(db.Model):
    __tablename__ = 'bundle'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    @property
    def serialize(self):
        """ Return object in easily serializable format """
        return{
            'id':self.id,
            'many2many': [item.serialize for item in self.products]
        }

    def __repr__(self):
        return f'Products in the bundle {self.products}'
    
