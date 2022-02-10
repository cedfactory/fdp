import sys
sys.path.insert(0, '../')
from flask import Flask, request, jsonify
import json
from datetime import datetime
import wiki as wiki

app = Flask(__name__)

@app.route("/")
def hello():
	return '''Hello world !'''

@app.route('/list', methods=['OPTIONS', 'GET', 'POST'])
def get_list():
   
    str_markets = request.args.get("markets")
    markets = str_markets.split(',')

    start = datetime.now()

    result_for_response = {}
    for market in markets:
        if market in ["cac", "cac40", "CAC", "CAC40"]:
            result_for_response[market] = wiki.get_list_CAC().to_json()
        elif market in ["dax", "DAX"]:
            result_for_response[market] = wiki.get_list_DAX().to_json()
        elif market in ["nasdaq", "nasdaq100", "NASDAQ", "NASDAQ100"]:
            result_for_response[market] = wiki.get_list_NASDAQ100().to_json()
        elif market in ["dji", "DJI"]:
            result_for_response[market] = wiki.get_list_DJI().to_json()
        elif market in ["sp500", "SP500"]:
            result_for_response[market] = wiki.get_list_SP500().to_json()

    end = datetime.now()
    elapsed_time = str(end - start)

    response = {
        "result":result_for_response,
        "elapsed_time":elapsed_time
    }

    response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response

if __name__ == "__main__":
	app.run(debug=False, host= '0.0.0.0', port=5002)
