from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from doctors.models import Doctor
from patients.models import Patient
from appointments.models import Appointment
from prescriptions.models import Prescription, PrescribedDrug, TestRecommendation
from drugs.models import Drug, DrugCategory, DrugDosageForm
from specialties.models import Specialty

class Command(BaseCommand):
    help = 'Create test data for prescriptions'

    def handle(self, *args, **options):
        try:
            # Create or get specialty
            specialty, _ = Specialty.objects.get_or_create(
                title='Test Specialty',
                defaults={
                    'title_ar': 'تخصص اختبار',
                    'icon': 'test-icon',
                    'background_color': '#ffffff',
                    'color_class': 'bg-primary',
                    'description': 'Test Description',
                    'description_ar': 'وصف الاختبار',
                    'total_time_call': 30,
                    'warning_time_call': 5,
                    'alert_time_call': 2,
                    'status': True
                }
            )

            # Get or create test doctor
            doctor, _ = Doctor.objects.get_or_create(
                email='test.doctor@example.com',
                defaults={
                    'name': 'Test Doctor',
                    'name_arabic': 'طبيب اختبار',
                    'sex': 'male',
                    'phone': '+1234567890',
                    'experience': '10 years',
                    'category': 'consultant',
                    'language_in_sessions': 'english',
                    'license_number': 'TEST123',
                    'profile_arabic': 'نبذة عن الطبيب',
                    'profile_english': 'Doctor profile',
                    'status': 'approved',
                }
            )
            doctor.specialities.add(specialty)
            self.stdout.write(f'Using doctor: {doctor.name}')

            # Get or create test patient
            patient, _ = Patient.objects.get_or_create(
                email='test.patient@example.com',
                defaults={
                    'name': 'Test Patient',
                    'name_arabic': 'مريض اختبار',
                    'sex': 'male',
                    'phone': '+1234567890',
                    'date_of_birth': timezone.now().date() - timedelta(days=365*25),
                    'status': 'active'
                }
            )
            self.stdout.write(f'Using patient: {patient.name}')

            # Create test appointment
            appointment = Appointment.objects.create(
                doctor=doctor,
                specialist_category='Test Category',
                gender='M',
                duration='30',
                language='English',
                phone_number='1234567890',
                slot_time=timezone.now() + timedelta(days=1),
                video_token='test_token'
            )
            appointment.specialties.add(specialty)
            self.stdout.write(f'Created appointment: {appointment}')

            # Create test drug category
            drug_category, _ = DrugCategory.objects.get_or_create(
                name='Test Category',
                defaults={
                    'name_arabic': 'فئة اختبار',
                    'status': True
                }
            )
            self.stdout.write(f'Using drug category: {drug_category.name}')

            # Create test drug dosage form
            drug_dosage_form, _ = DrugDosageForm.objects.get_or_create(
                name='Test Form',
                defaults={
                    'name_arabic': 'شكل اختبار',
                    'status': True
                }
            )
            self.stdout.write(f'Using drug dosage form: {drug_dosage_form.name}')

            # Create test drug
            drug, _ = Drug.objects.get_or_create(
                name='Test Drug',
                defaults={
                    'name_arabic': 'دواء اختبار',
                    'description': 'Test drug description',
                    'description_arabic': 'وصف دواء الاختبار',
                    'category': drug_category,
                    'dosage_form': drug_dosage_form,
                    'strength': '500mg',
                    'manufacturer': 'Test Manufacturer',
                    'status': True
                }
            )
            self.stdout.write(f'Using drug: {drug.name}')

            # Create test prescription
            prescription = Prescription.objects.create(
                appointment=appointment,
                diagnosis='Test diagnosis',
                notes='Test follow up notes',
                follow_up_date=timezone.now() + timedelta(days=7)
            )
            self.stdout.write(f'Created prescription: {prescription}')

            # Create test prescribed drug
            prescribed_drug = PrescribedDrug.objects.create(
                prescription=prescription,
                drug=drug,
                dosage='1 tablet',
                frequency='OD',
                duration=7,
                duration_unit='days',
                route='oral',
                instructions='Test notes'
            )
            self.stdout.write(f'Created prescribed drug: {prescribed_drug}')

            # Create test recommendation
            test_recommendation = TestRecommendation.objects.create(
                prescription=prescription,
                test_name='Blood Test',
                urgency='routine',
                notes='Test recommendation notes'
            )
            self.stdout.write(f'Created test recommendation: {test_recommendation}')

            self.stdout.write(self.style.SUCCESS('Successfully created test prescription data'))
            self.stdout.write(f'Admin URLs:')
            self.stdout.write(f'Prescription: /admin/prescriptions/prescription/{prescription.id}/')
            self.stdout.write(f'Prescribed Drug: /admin/prescriptions/prescribeddrug/{prescribed_drug.id}/')
            self.stdout.write(f'Test Recommendation: /admin/prescriptions/testrecommendation/{test_recommendation.id}/')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test data: {str(e)}')) 