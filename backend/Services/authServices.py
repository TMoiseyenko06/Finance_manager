import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from utils.util import encode_token, token_required, decode_token
from database import db
from plaid.model.link_token_create_request_statements import LinkTokenCreateRequestStatements
from plaid.model.link_token_create_request_cra_options import LinkTokenCreateRequestCraOptions
from plaid.model.consumer_report_permissible_purpose import ConsumerReportPermissiblePurpose
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.api import plaid_api
from dotenv import load_dotenv
import os
import datetime as dt
import json
import time
from datetime import date, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products

load_dotenv()

accounts_collection = db['accounts']

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

user_token = None
item_id = None
access_token = None

def register(user_data):
    if accounts_collection.count_documents({'_id':user_data['username']}, limit = 1) == 0:
        new_account = {
            "_id":user_data['username'],
            "password":generate_password_hash(user_data['password'])
        }
        accounts_collection.insert_one(new_account)
        return jsonify({"status":"OK",
                        "message":"User Register"    
                        }),201
    else:
        return jsonify({"error":"username already exists"}), 400

def login(user_data):
    if accounts_collection.count_documents({"_id":user_data['username']}, limit = 1 ) != 0:
        user = accounts_collection.find_one({"_id": user_data['username']})
        if user is None:
           return jsonify({"status": "Error", "message": "Invalid username or password"}), 400
        if not check_password_hash(user['password'], user_data['password']):
            return jsonify({"status": "Error", "message": "Invalid username or password"}), 400
        user_id = user['_id']
        return jsonify({
            "status":"OK",
            "auth_token":encode_token(user_id)
                        }),200
    
def info():
    global access_token
    global item_id
    return jsonify({
        'item_id': item_id,
        'access_token': access_token,
        'products': PLAID_PRODUCTS
    })


def plaid_link_token():
    global user_token
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="Plaid Quickstart",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user = LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )

        if PLAID_REDIRECT_URI != None:
            request['redirect_uri'] = PLAID_REDIRECT_URI

        cra_products = []

        if Products('statements') in products:
            statements=LinkTokenCreateRequestStatements(
                end_date=date.today(),
                start_date=date.today()-timedelta(days=30)
            )
            request['statements']=statements
            cra_products = ["cra_base_report", "cra_income_insights", "cra_partner_insights"]
        
        if any(product in cra_products for product in PLAID_PRODUCTS):
            request['user_token'] = user_token
            request['consumer_report_permissible_purpose'] = ConsumerReportPermissiblePurpose('ACCOUNT_REVIEW_CREDIT')
            request['cra_options'] = LinkTokenCreateRequestCraOptions(
                days_requested=60
            )
        response = client.link_token_create(request)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body)


#REMINDER: test function, change it to save token to database
def exchange_token(public_token):
    global access_token
    global item_id
    try:
        user_token = decode_token()
        user_id = user_token['uid']
        exchange_request = ItemPublicTokenExchangeRequest(public_token = public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        accounts_collection.update_one({{"_id":user_id},{"$set":{"access_token":access_token,"item_id":item_id}}})
        return jsonify(exchange_response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body), 500
    
def is_connected():
    pass