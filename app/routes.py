import os
import json
import uuid
from PIL import Image

from werkzeug.utils import secure_filename
from flask import render_template, make_response, jsonify, request, url_for, redirect, flash, send_from_directory, current_app


from app import app, db
from app.models import Ingredient, Product, Allergies, Bundle
from app.utils import allowed_file, thumb_size


@app.route('/uploads/<string:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_IMAGE_FOLDER'], filename)

@app.route('/')
@app.route('/acasa')
def home():
    products = Product.query.all()
    
    # Get the first and only bundle offer 
    bundle = Bundle.query.first()
    # Compute total price of the bundle
    bundle_ser = bundle.serialize
    b_item1_reduced_price = float(bundle_ser['many2many'][1]['new_price'])
    b_item0_price = round(float(bundle_ser['many2many'][0]['price']))

    total_price = b_item0_price + b_item1_reduced_price
    bundle_ser["total_value"] = str(total_price)

    return render_template('home.html', products=products, bundle=bundle_ser)

@app.route('/despre-noi')
def about_us():
    return render_template('about-us.html')

@app.route('/load')
def load():
    res = make_response(jsonify(db[0]), 200)
    return res

# Add products, uncomment to add products. Change this to log-in required later on instead of commenting it.
"""
@app.route('/add-products', methods=['GET'])
def add_products():
    ingredients = Ingredient.query.all()
    allergies = Allergies.query.all()

    json_ingredients = json.dumps([x.name for x in ingredients]) 

    return render_template('add-products.html', ingredients=ingredients, allergies=allergies, json_ingredients=json_ingredients)
"""

def preprocess_save_image(img, output_size):
    ''' Change the name of the image into an uuid '''
    tmp_name, ext = os.path.splitext(img.filename)
    img.filename = str(uuid.uuid4()) + ext

    ''' Open image and change size ratio to the preferred one '''
    prep_image = Image.open(img)

    size = prep_image.size
    ratio = min(output_size[0] / size[0], output_size[1] / size[1])

    new_size = [int(ratio * s) for s in prep_image.size]
    prep_image = prep_image.resize(new_size, Image.ANTIALIAS)

    prep_image.save(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], img.filename), optimize=True, quality=95)
    current_app.s3_client.upload_file(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], img.filename), app.config['AWS_BUCKET_NAME'], img.filename)
    
    return img.filename

# POST routes for adding products below
@app.route('/post_products', methods=['POST'])
def post_products():
    ingredients = request.form.getlist('check-ingr')
    allergies = request.form.getlist('check-alg')

    title = request.form['title']

    small = True if 'small' in request.form else False
    medium = True if 'medium' in request.form else False
    large = True if 'large' in request.form else False

    price = request.form['price']

    if 'file' not in request.files:
        flash('No File Part')
        return redirect(url_for('add_products'))
    
    image_file = request.files['file']
    if image_file.filename == '':
        flash('No Selected Files')
        return redirect(request.url)
    
    if image_file and allowed_file(image_file.filename):
        filename = preprocess_save_image(image_file, thumb_size)
        # return redirect(url_for('uploaded_file', filename=filename))
    else:
        flash('Please upload a proper file with allowed extensions')
        return redirect(url_for('add_products'))

    # Add product to database
    product = Product(title=title, small=small, medium=medium, large=large, price=price, jpeg_path=filename)

    """
    Problem, we can't handle ingredients like: hot saussage (2 words) -> hot@saussage
    """
    for ingr in ingredients:
        ingr_obj = Ingredient.query.filter(Ingredient.name == ingr).first()
        product.ingredients.append(ingr_obj)

    for alg in allergies:
        alg_obj = Allergies.query.filter(Allergies.name == alg).first()
        product.allergies.append(alg_obj)

    db.session.add(product)
    db.session.commit()

    return redirect(url_for('add_products'))

@app.route('/post_ingredients', methods=['POST'])
def post_ingredients():
    ingredient_name = request.form['ing-name'].lower()
    
    ingredient = Ingredient(name=ingredient_name)

    db.session.add(ingredient)
    db.session.commit()

    return redirect(url_for('add_products'))

@app.route('/post_allergies', methods=['POST'])
def post_allergies():
    allergy_name = request.form['alg-name'].lower()
    
    allergy = Allergies(name=allergy_name)

    db.session.add(allergy)
    db.session.commit()

    return redirect(url_for('add_products'))