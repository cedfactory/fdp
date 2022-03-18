import sys
sys.path.insert(0, '../')
from flask import Flask, request, jsonify
import json
from src import api

app = Flask(__name__)

def add_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response

@app.route("/")
def hello():
	return '''Hello world !'''

@app.route('/list', methods=['OPTIONS', 'GET'])
def get_list():
   
    str_markets = request.args.get("markets")

    response = api.api_list(str_markets)
    response = jsonify(response)
    response = add_headers(response)

    return response

@app.route('/value', methods=['OPTIONS', 'GET'])
def get_value():
   
    str_values = request.args.get("values")

    response = api.api_value(str_values)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

@app.route('/history', methods=['OPTIONS', 'GET'])
def get_history():
   
    str_source = request.args.get("source")
    str_symbol = request.args.get("symbol")
    str_start = request.args.get("start")
    length = request.args.get("length", 100)
    if length != None:
        length = int(length)

    response = api.api_history(str_source, str_symbol, str_start, length)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

@app.route('/recommendations', methods=['OPTIONS', 'GET'])
def get_recommendations():
   
    screener = request.args.get("screener")
    exchange = request.args.get("exchange")
    symbol = request.args.get("symbol")
    interval = request.args.get("interval", "1h")

    response = api.api_recommendations(screener, exchange, symbol, interval)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

if __name__ == "__main__":
	app.run(debug=False, host= '0.0.0.0', port=5000)
