import os
import json
from flask import Flask
from flask import make_response
from flask import request
from flask import json
from waitress import serve

import services
import push_notification_service
import db


app = Flask(__name__)

db = db.Database()
push_notification_service = push_notification_service.PushNotificationService()

if os.getenv('TESTING', 'False') == 'True':
    digitransitAPIService = services.DigitransitAPIService(db,
                                                           push_notification_service,
                                                           'http://localhost:11111')
else:
    digitransitAPIService = services.DigitransitAPIService(db,
                                                           push_notification_service,
                                                           'http://api.digitransit.fi/routing/v1/routers/hsl/index/graphql')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/test')
def digitransit_test():
    return json.dumps(digitransitAPIService.fetch_single_trip("HSL:1055_20161107_Ti_2_1329"))
    #return json.dumps(digitransitAPIService.get_stops(60.203978, 24.9633573))


@app.route('/stoprequests', methods=['GET', 'POST'])
def stoprequests():
    if request.method == 'GET':
        request_id = request.args.get('request_id')
        if not request_id:
            resp = make_response(json.dumps({'error': 'no request_id query parameter given'}), 400)
            resp.mimetype = 'application/json'
            return resp
        resp = make_response(json.dumps(digitransitAPIService.get_request_info(request_id)))
        resp.mimetype = 'application/json'
        return resp
    elif request.method == 'POST':
        json_data = request.json
        trip_id = json_data.get('trip_id')
        stop_id = json_data.get('stop_id')
        device_id = json_data.get('device_id', '0')
        push_notification = json_data.get('push_notification', True)
        if not (trip_id and stop_id):
            resp = make_response(json.dumps({'error': 'no trip_id or stop_id query parameter given'}), 400)
            resp.mimetype = 'application/json'
            return resp
        resp = make_response(json.dumps(digitransitAPIService.make_request(trip_id, stop_id, device_id, push_notification)))
        resp.mimetype = 'application/json'
        return resp


@app.route('/stoprequests/cancel', methods=['POST'])
def stoprequests_cancel():
    request_id = int(request.args.get('request_id'))
    if not request_id:
        resp = make_response(json.dumps({'error': 'no request_id query parameter given'}), 400)
        resp.mimetype = 'application/json'
        return resp
    result = digitransitAPIService.cancel_request(request_id)
    return result


@app.route('/stoprequests/report', methods=['POST'])
def report():
    json_data = request.json
    trip_id = json_data.get('trip_id')
    stop_id = json_data.get('stop_id')
    if not (trip_id and stop_id):
        resp = make_response(json.dumps({'error': 'no trip_id or stop_id query parameter given'}), 400)
        resp.mimetype = 'application/json'
        return resp
    result = digitransitAPIService.store_report(json_data)
    return result


@app.route('/stops', methods=['GET'])
def stops():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    rad = float(request.args.get('rad', 160))
    if not (lat and lon):
        resp = make_response(json.dumps({'error': 'not lat or lon query parameter given'}), 400)
        resp.mimetype = 'application/json'
        return resp
    result = digitransitAPIService.get_stops(lat, lon, rad)
    resp = make_response(json.dumps(result))
    resp.mimetype = 'application/json'
    return resp


@app.route('/routes', methods=['GET'])
def routes():
    trip_id = request.args.get('trip_id')
    stop_id = request.args.get('stop_id')
    if not trip_id:
        resp = make_response(json.dumps({'error': 'no trip_id query parameter given'}), 400)
        resp.mimetype = 'application/json'
        return resp
    if stop_id:
        result = digitransitAPIService.get_single_stop_by_trip_id(trip_id, stop_id)
    else:
        result = digitransitAPIService.get_stops_by_trip_id(trip_id)
    resp = make_response(json.dumps(result))
    resp.mimetype = 'application/json'
    return resp

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=os.getenv('PORT', 5000))
