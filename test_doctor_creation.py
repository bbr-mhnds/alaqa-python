import os
import django
import uuid
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_doctor_creation():
    """Test creating a doctor and verifying the creation"""
    
    # Generate unique email
    unique_id = str(uuid.uuid4())[:8]
    test_email = f'test.doctor+{unique_id}@alaqa.net'
    
    print(f"\nCreating test doctor with email: {test_email}")
    print("-" * 50)
    
    try:
        # Step 1: Create doctor verification
        from doctors.models import DoctorVerification
        from django.utils import timezone
        from django.db import connection
        
        # Create verification using raw SQL to handle SERIAL ID
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO doctors_doctorverification 
                (email, phone, email_verified, phone_verified, expires_at, is_used, email_code)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, [
                test_email, 
                '966555552022',
                True,
                True,
                timezone.now() + timezone.timedelta(minutes=10),
                False,
                '000000'
            ])
            verification_id = cursor.fetchone()[0]
            
        print("✓ Created doctor verification")
        
        # Step 2: Create user account
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Group
        User = get_user_model()
        
        # Create user
        user = User.objects.create_user(
            email=test_email,
            password='TestPass@123',
            is_active=True,
            is_staff=True
        )
        
        # Add to doctors group
        doctor_group, _ = Group.objects.get_or_create(name='Doctors')
        user.groups.add(doctor_group)
        
        print("✓ Created user account")
        
        # Step 3: Create doctor
        from doctors.models import Doctor
        doctor = Doctor.objects.create(
            name_arabic='طبيب تجريبي',
            name='Test Doctor',
            sex='male',
            email=test_email,
            phone='966555552022',
            experience='10 years',
            category='specialist',
            language_in_sessions='both',
            license_number=f'LIC{datetime.now().strftime("%Y%m%d%H%M%S")}',
            profile_arabic='نبذة عن الطبيب باللغة العربية',
            profile_english='Doctor profile in English',
            status='approved'
        )
        
        print("✓ Created doctor profile")
        
        # Step 4: Verify creation
        print("\nVerification Results:")
        print("-" * 50)
        print(f"Doctor exists: {Doctor.objects.filter(email=test_email).exists()}")
        print(f"User exists: {User.objects.filter(email=test_email).exists()}")
        print(f"User is active: {user.is_active}")
        print(f"User is in Doctors group: {user.groups.filter(name='Doctors').exists()}")
        print(f"Doctor status: {doctor.status}")
        print(f"\nTest credentials:")
        print("-" * 50)
        print(f"Email: {test_email}")
        print(f"Password: TestPass@123")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_doctor_creation() 