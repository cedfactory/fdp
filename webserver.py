import sys
sys.path.insert(0, '../')
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route("/")
def hello():
	return '''Hello world !'''

@app.route('/hello', methods=['OPTIONS', 'GET', 'POST'])
def hello():
    
    name = request.args.get("name")

    start = datetime.now()
    result = "Hello " + name
    end = datetime.now()

    elapsed_time = str(end - start)

    response = {
        "result":result,
        "elapsed_time":elapsed_time
    }

    response = jsonify(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.add("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response

if __name__ == "__main__":
	app.run(debug=False, host= '0.0.0.0')
