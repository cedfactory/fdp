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
	return '''Hello world ! (v1.0)'''

@app.route('/list', methods=['OPTIONS', 'GET'])
def get_list():
   
    str_exchanges = request.args.get("exchanges")

    response = api.api_list(str_exchanges)
    response = jsonify(response)
    response = add_headers(response)

    return response

@app.route('/symbol', methods=['OPTIONS', 'GET'])
def get_symbol():
   
    str_screener = request.args.get("screener", "crypto")
    str_exchange = request.args.get("exchange")
    str_symbols = request.args.get("symbols")

    response = api.api_symbol(str_screener, str_exchange, str_symbols)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

@app.route('/history', methods=['OPTIONS', 'GET'])
def get_history():
   
    str_exchange = request.args.get("exchange")
    str_symbol = request.args.get("symbol")
    str_start = request.args.get("start")
    str_end = request.args.get("end")
    str_interval = request.args.get("interval", "1d")
    length = request.args.get("length", 100)
    if length != None:
        length = int(length)
    indicators= request.args.get("indicators", [])
    if isinstance(indicators, str):
        indicators = indicators.split(',')

    response = api.api_history(str_exchange, str_symbol, str_start, str_end, str_interval, length, indicators)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

@app.route('/recommendations', methods=['OPTIONS', 'GET'])
def get_recommendations():
   
    screener = request.args.get("screener")
    exchange = request.args.get("exchange")
    symbols = request.args.get("symbols")
    interval = request.args.get("interval", "1h")

    response = api.api_recommendations(screener, exchange, symbols, interval)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

@app.route('/portfolio', methods=['OPTIONS', 'GET'])
def get_portfolio():
   
    exchange_name = request.args.get("exchange", "ftx")
    recommendations = request.args.get("recommendations")
    if recommendations is None:
        recommendations = ["BUY", "STRONG_BUY"]
    else:
        recommendations = recommendations.split(',')
        
    intervals = request.args.get("intervals")
    if intervals is None:
        intervals = ["15m", "30m", "1h"]
    else:
        intervals = intervals.split(',')
    print(intervals)

    response = api.api_portfolio(exchange_name, recommendations, intervals)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

if __name__ == "__main__":
    app.run(debug=False, host= '0.0.0.0', port=5000)
