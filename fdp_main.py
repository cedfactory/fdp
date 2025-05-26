import sys
import time
sys.path.insert(0, '../')
from flask import Flask, request, jsonify, send_from_directory
from src import api
from src import data_recorder
from src import config
from src import crypto

from src import ws_global

app = Flask(__name__, static_folder='static')


@app.before_request
def init_ws():
    ws_global.ws_traces_start()
    ws_global.ws_candle_start()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def add_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response

@app.route("/")
def hello():
	return '''Hello world ! (v1.3)'''

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

@app.route('/history', methods=['OPTIONS', 'GET', 'POST'])
def get_history():
    history_params = api.api_history_parse_parameters(request)
    if history_params.get("status") == "ko":
        response = {
            "result":history_params.get("reason"),
            "status":"ok"
            }
    else:
        response = api.api_history(history_params)
    response = jsonify(response)
    response = add_headers(response)
    
    return response

@app.route('/status', methods=['OPTIONS', 'GET', 'POST'])
def get_ws_status():
    start_time = time.time()
    status = api.api_parse_status_parameters(request)
    if status == "ws_status":
        response = {
            "result": ws_global.ws_traces_get_status(),
            "status": "ok",
            "elapsed_time": str(time.time() - start_time)
        }
    else:
        response = {
            "result": {},
            "status": "nok",
            "elapsed_time": str(time.time() - start_time)
        }
    response = jsonify(response)
    response = add_headers(response)

    return response

@app.route('/last', methods=['OPTIONS', 'GET', 'POST'])
def get_last():
    history_params = api.api_history_parse_parameters(request, True)
    if history_params.get("status") == "ko":
        response = {
            "result":history_params.get("reason"),
            "status":"ok"
            }
    else:
        response = api.api_last(history_params)
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
   
    exchange_name = request.args.get("exchange", "binance")
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

    api.g_exchange, api.g_markets = crypto.get_exchange_and_markets("bitget")
    api.g_exchange.load_markets()

    if len(sys.argv) >= 2 and (sys.argv[1] == "--sim"):
        if len(sys.argv) != 4:
            print("usage : python main.py --sim csvfilename indicatorfilename")
            exit(0)
        else:
            config.use_mock = True
            config.g_data = data_recorder.DataRecorder(sys.argv[2], sys.argv[3])

    app.run(debug=False, host= '0.0.0.0', port=5000)
