import json

from flask import Flask, request, make_response, render_template
from flask_restful import Api
from flask_cors import cross_origin, CORS
from flask.json import jsonify
from webScrapper import shopsInfo, webScrapper

app = Flask(__name__)
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
    json_request = request.get_json()

    '''COMMENT ONLY FOR DEBUGGING!!'''
    # if not 'products_list' in json_request:
    #     return make_response(jsonify({"Error": "products_list not set"}), 400)
    # products_list = json_request['products_list']
    # shops_list = json_request['shops_list'] if 'shops_list' in json_request else None
    #
    # scrapper = webScrapper(products_list)
    # result = scrapper.find_products(shops_list)

    with open('data.json',) as f:
        file = json.load(f)

    return jsonify(file)
