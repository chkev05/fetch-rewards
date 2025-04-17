import unittest
import json
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_process_receipt(self):
        receipt_data = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                "shortDescription": "Mountain Dew 12PK",
                "price": "6.49"
                },{
                "shortDescription": "Emils Cheese Pizza",
                "price": "12.25"
                },{
                "shortDescription": "Knorr Creamy Chicken",
                "price": "1.26"
                },{
                "shortDescription": "Doritos Nacho Cheese",
                "price": "3.35"
                },{
                "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
                "price": "12.00"
                }
            ],
            "total": "35.35"
        }
        
        response = self.app.post(
            '/receipts/process',
            data=json.dumps(receipt_data), 
            content_type='application/json'
        )

        print(response.get_json())

        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        self.assertIn('id', response_json)
        print(response_json)

        response = self.app.get(f'/receipts/{response_json["id"]}/points')
        response_json = response.get_json()
        print(response_json)

    def test_process_receipt_2(self):
        receipt_data = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [
                {
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                }
            ],
            "total": "9.00"
        }
        
        response = self.app.post(
            '/receipts/process',
            data=json.dumps(receipt_data),
            content_type='application/json'
        )

        print(response.get_json())

        self.assertEqual(response.status_code, 200)

        response_json = response.get_json()
        self.assertIn('id', response_json) 
        print(response_json)

        response = self.app.get(f'/receipts/{response_json["id"]}/points')
        response_json = response.get_json()
        print(response_json)

if __name__ == '__main__':
    unittest.main()
