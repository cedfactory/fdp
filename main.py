import sys
sys.path.insert(0, '../')
from flask import Flask, request, jsonify
import json
from src import api

app = Flask(__name__)

@app.route("/")
def hello():
	return '''Hello world !'''

@app.route('/list', methods=['OPTIONS', 'GET', 'POST'])
def get_list():
   
    str_markets = request.args.get("markets")
    markets = str_markets.split(',')

    response = api.api_list(markets)

    response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response

if __name__ == "__main__":
	app.run(debug=False, host= '0.0.0.0', port=5000)
