import json
import logging
from flask import Flask, request, make_response, render_template
from flask_restful import Api
from flask_cors import CORS
from flask.json import jsonify
from assets.WebScrapper import WebScrapper
from assets.serializer import Serializer
from assets.CustomErrors import WebDriverNotFound, ShopsNotSet, ProductsNotSet

logger = logging.getLogger('app')
logger.setLevel('ERROR')
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shops')
def get_shops():
    try:
        return make_response(jsonify(WebScrapper.get_shops()), 200)
    except FileNotFoundError as e:
        logger.exception(e)
        return make_response(jsonify({"Error": "Internal server error"}), 500)

@app.route('/find', methods=['POST'])
def get_products():
    try:
        json_request = request.get_json()
        print(json_request)
        serializer = Serializer(json_request)
        serializer.serialize_data()

        if(serializer.is_valid()):
            serialized_data = serializer.data
            scrapper = WebScrapper(serialized_data)
            products = scrapper.find_products(sort=True)

            #TESTING FILE - TO DELETE IN PRODUCTION VERSION!
            #with open('json/data.json') as f:
            #    prodcuts = json.load(f)

            return make_response(jsonify(products), 200)
        return make_response(jsonify({"Error": serializer.errors}), 400)

    except WebDriverNotFound as e:
        logger.error(e)
        return make_response(jsonify({"Error": "Server configuration error"}), 500)
    except ShopsNotSet as e:
        logger.exception(e)
        return make_response(jsonify({"Error": "Shops are not set"}), 400)
    except ProductsNotSet as e:
        logger.exception(e)
        return make_response(jsonify({"Error": "Products are not set"}), 400)
    except FileNotFoundError as e:
        logger.exception(e)
        return make_response(jsonify({"Error": "Internal server error"}), 500)
    except Exception as e:
        logger.exception(e)
        return make_response(jsonify({"Error": "Internal server error"}), 500)

