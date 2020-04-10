import json
from CustomErrors import WebDriverNotFound
from flask import Flask, request, make_response, render_template
from flask_restful import Api
from flask_cors import CORS
from flask.json import jsonify
from webScrapper import shopsInfo, webScrapper
from serializer import Serializer

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
    data = shopsInfo.get_shops()
    return make_response(jsonify(data), 200)

@app.route('/find', methods=['POST'])
def get_products():
    try:
        json_request = request.get_json()
        print(json_request)
        serializer = Serializer(json_request)
        serializer.serialize_data()

        if(serializer.is_valid()):
            serialized_data = serializer.get_data()
            products_list = serialized_data["products"]
            shops_list = serialized_data["shops"]
            scrapper = webScrapper(products_list)
            #products = scrapper.find_products(shops_list)

            #TESTING FILE - TO DELETE IN PRODUCTION VERSION!
            with open('data.json') as f:
                products = json.load(f)
            results = scrapper.sort_products_by_price(products)
            return make_response(jsonify(results), 200)
        return make_response(jsonify({"Error": serializer.get_errors()}), 400)

    except WebDriverNotFound:
        return make_response(jsonify({"Error": "Server configuration error"}), 500)
    except Exception as e:
        print(e)
        return make_response(jsonify({"Error": "Internal server error"}), 500)

