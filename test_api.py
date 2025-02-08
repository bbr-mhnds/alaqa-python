import requests
import json
import time

def test_apis():
    base_url = 'http://127.0.0.1:8000'
    
    def print_response(response, endpoint):
        print(f'\nTesting {endpoint}:')
        print('Status Code:', response.status_code)
        print('Response:', json.dumps(response.json() if response.text else {}, indent=2))
        print('-' * 50)

    # Test 1: Doctor Registration Initiation
    print('\nTest 1: Doctor Registration Initiation')
    response = requests.post(
        f'{base_url}/api/v1/doctors/register/initiate/',
        json={
            'email': 'test.doctor@alaqa.net',
            'phone': '555552022'
        }
    )
    print_response(response, 'Doctor Registration Initiation')
    
    if response.status_code == 200:
        verification_data = response.json().get('data', {})
        verification_id = verification_data.get('verification_id')
        
        # Test 2: Doctor Registration Verification
        print('\nTest 2: Doctor Registration Verification')
        response = requests.post(
            f'{base_url}/api/v1/doctors/register/verify/',
            json={
                'verification_id': verification_id,
                'email': 'test.doctor@alaqa.net',
                'sms_code': '000000'
            }
        )
        print_response(response, 'Doctor Registration Verification')

    # Test 3: Authentication
    print('\nTest 3: Authentication')
    response = requests.post(
        f'{base_url}/api/v1/auth/login/',
        json={
            'email': 'admin@alaqa.net',
            'password': 'admin123'
        }
    )
    print_response(response, 'Authentication')
    
    if response.status_code == 200:
        token = response.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test 4: Get Doctors List
        print('\nTest 4: Get Doctors List')
        response = requests.get(
            f'{base_url}/api/v1/doctors/',
            headers=headers
        )
        print_response(response, 'Get Doctors List')

if __name__ == '__main__':
    test_apis() 