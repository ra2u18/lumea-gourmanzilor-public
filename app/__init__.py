from flask import Flask
from config import Config
from jinja2 import environment

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# AWS SES library
import boto3

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.ses_client = boto3.client(
    'ses',
    region_name=app.config['AWS_REGION'],
    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
)

app.s3_client = boto3.client('s3', region_name=app.config['AWS_REGION'])

""" 
Jinja2 custom filters
"""
blacklist_stopwords = ['cu', 'pentru', 'de']

def splitpart(value, index, char = ','):
    value = str(value)
    return value.split(char)[index]

def format_lists(value):
    temp_list = []

    for item in value.all():
        item_name = item.name
        capitalize = []
        if len(item_name.split('@')) > 1:
            for word in item_name.split('@'):
                if word not in blacklist_stopwords:
                    capitalize.append(word.capitalize())
                else:
                    capitalize.append(word)
                
            temp_list.append(' '.join(capitalize))
        else:
            temp_list.append(item_name.capitalize())

    return ', '.join(temp_list)

environment.DEFAULT_FILTERS['splitpart'] = splitpart 
environment.DEFAULT_FILTERS['formatlists'] = format_lists 

from app import routes, models, errors
		