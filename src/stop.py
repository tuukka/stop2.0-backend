import os
import json
from flask import Flask
from flask import make_response
from flask import request
from flask import json
import paho.mqtt.publish as publish

import services
import db


app = Flask(__name__)

digitransitAPIService = services.DigitransitAPIService()
db = db.Database()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/test')
def digitransit_test():
    return json.dumps(digitransitAPIService.get_stops(60.203978, 24.9633573))

@app.route('/stoprequests', methods=['POST'])
def stoprequest():
    jsonData = request.json
    bus_id = jsonData["bus_id"]
    del jsonData["bus_id"]
    jsonData = json.dumps(jsonData)
    publish.single(topic="stoprequests/"+bus_id, payload=jsonData, hostname="epsilon.fixme.fi")
    return ('', 200)

@app.route('/stops', methods=['GET'])
def stops():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    rad = float(request.args.get('rad', default=160))
    result = digitransitAPIService.get_stops(lat, lon, rad)
    resp = make_response(json.dumps(result))
    resp.mimetype = 'application/json'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', '5000'))

