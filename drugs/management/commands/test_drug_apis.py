from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from drugs.models import Drug, DrugCategory, DrugDosageForm
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Test Drug APIs'

    def handle(self, *args, **kwargs):
        # Create test user and get token
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'password': 'testpass123',
                'is_active': True
            }
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Test Categories API
        self.stdout.write('Testing Drug Categories API...')
        response = client.get('/api/v1/drugs/categories/')
        self.stdout.write(f'Categories Response Status: {response.status_code}')
        self.stdout.write(f'Categories Response Data: {response.data if hasattr(response, "data") else "No data"}')
        
        # Test Dosage Forms API
        self.stdout.write('\nTesting Drug Dosage Forms API...')
        response = client.get('/api/v1/drugs/dosage-forms/')
        self.stdout.write(f'Dosage Forms Response Status: {response.status_code}')
        self.stdout.write(f'Dosage Forms Response Data: {response.data if hasattr(response, "data") else "No data"}')
        
        # Test Main Drugs API
        self.stdout.write('\nTesting Main Drugs API...')
        response = client.get('/api/v1/drugs/drugs/')
        self.stdout.write(f'Drugs Response Status: {response.status_code}')
        self.stdout.write(f'Drugs Response Data: {response.data if hasattr(response, "data") else "No data"}') 