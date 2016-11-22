import unittest
import stop


class TestStopRoutes(unittest.TestCase):

    def setUp(self):
        stop.app.config['TESTING'] = True
        self.app = stop.app.test_client()


    def test_stops_get(self):
        response = self.app.get('/stops?lat=60.203978&lon=24.963357')
        self.assertEqual(response.status_code, 200)

    def test_stopsrequests_post(self):
        jsonString = '{"trip_id": "1234", "stop_id": "HSL:1282106", "device_id": "123", "push_notification": false}'
        response = self.app.post('/stoprequests', data=jsonString, content_type='application/json')
        self.assertEquals(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()