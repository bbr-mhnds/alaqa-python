import os
import django
import json
import requests
from datetime import datetime
from reportlab.pdfgen import canvas
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def create_test_pdf(filename, title="Test Document"):
    """Create a test PDF file with given title"""
    c = canvas.Canvas(filename)
    c.drawString(100, 750, title)
    c.drawString(100, 700, f"Generated for testing on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.save()
    return filename

def test_doctor_registration():
    """Test the complete doctor registration flow"""
    
    base_url = "https://api.alaqa.net"
    
    # Generate unique email
    unique_id = str(uuid.uuid4())[:8]
    test_email = f"test.doctor+{unique_id}@alaqa.net"
    
    # Step 1: Initiate Registration
    initiate_data = {
        "email": test_email,
        "phone": "555552022"
    }
    
    print("\nStep 1: Initiating Registration")
    print("-" * 50)
    print(f"Using test email: {test_email}")
    
    initiate_response = requests.post(
        f"{base_url}/api/v1/doctors/register/initiate/",
        json=initiate_data
    )
    
    print(f"Status Code: {initiate_response.status_code}")
    print(f"Response: {json.dumps(initiate_response.json(), indent=2)}")
    
    if initiate_response.status_code != 200:
        print("Registration initiation failed!")
        return
        
    verification_id = initiate_response.json().get('data', {}).get('verification_id')
    
    # Create test PDF files
    license_file = create_test_pdf('test_license.pdf', "Medical License Document")
    qualification_file = create_test_pdf('test_qualification.pdf', "Medical Qualification Document")
    
    # Step 2: Complete Registration with Verification
    registration_data = {
        "verification_id": verification_id,
        "email": test_email,
        "sms_code": "000000",  # Using the test OTP code
        "name_arabic": "طبيب تجريبي",
        "name": "Test Doctor",
        "sex": "male",
        "phone": "555552022",
        "experience": "10 years",
        "category": "specialist",
        "language_in_sessions": "both",
        "license_number": f"LIC{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "specialities": json.dumps(["188da049-4265-4ddb-9df7-5b9dc8cb2056"]),  # Convert to JSON string
        "profile_arabic": "نبذة عن الطبيب باللغة العربية",
        "profile_english": "Doctor profile in English",
        "password": "TestPass@123",
        "confirm_password": "TestPass@123",
        "terms_and_privacy_accepted": True,
        "bank_name": "Test Bank",
        "account_holder_name": "Test Doctor",
        "account_number": "12345678",
        "iban_number": "SA0380000000608010167519",
        "swift_code": "TESTBICX"
    }
    
    # Open files for upload
    files = {
        'license_document': ('test_license.pdf', open(license_file, 'rb'), 'application/pdf'),
        'qualification_document': ('test_qualification.pdf', open(qualification_file, 'rb'), 'application/pdf')
    }
    
    print("\nStep 2: Completing Registration")
    print("-" * 50)
    
    try:
        verify_response = requests.post(
            f"{base_url}/api/v1/doctors/register/verify/",
            data=registration_data,
            files=files
        )
        
        print(f"Status Code: {verify_response.status_code}")
        print(f"Response: {json.dumps(verify_response.json(), indent=2)}")
        
        if verify_response.status_code == 201:
            print("\nDoctor registration successful!")
            print("Next steps:")
            for step in verify_response.json().get('data', {}).get('next_steps', []):
                print(f"- {step}")
        else:
            print("\nDoctor registration failed!")
            
    finally:
        # Clean up test files
        for file in files.values():
            file[1].close()
        os.remove(license_file)
        os.remove(qualification_file)

if __name__ == "__main__":
    test_doctor_registration() 