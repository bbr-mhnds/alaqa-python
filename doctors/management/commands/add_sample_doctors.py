from django.core.management.base import BaseCommand
from doctors.models import Doctor
from specialties.models import Specialty
import uuid

class Command(BaseCommand):
    help = 'Add sample doctors to the database'

    def handle(self, *args, **kwargs):
        # Get or create specialties
        specialties = {}
        specialty_defaults = {
            'background_color': '#f8f9fa',
            'color_class': 'bg-light',
            'total_time_call': 30,
            'warning_time_call': 5,
            'alert_time_call': 4,
            'status': True
        }

        specialty_mappings = {
            'obsession': {'title': 'Obsessives', 'title_ar': 'الوسواس القهري', 'icon': 'brain', 'description': 'Treatment for obsessive thoughts and compulsive behaviors', 'description_ar': 'علاج الأفكار الوسواسية والسلوكيات القهرية'},
            'addiction': {'title': 'Substance Abuse', 'title_ar': 'إدمان المخدرات', 'icon': 'pills', 'description': 'Treatment for drug and alcohol addiction', 'description_ar': 'علاج إدمان المخدرات والكحول'},
            'relationships': {'title': 'RelationshipsProblem', 'title_ar': 'مشاكل العلاقات', 'icon': 'users', 'description': 'Help with relationship and interpersonal issues', 'description_ar': 'المساعدة في مشاكل العلاقات والقضايا الشخصية'},
            'lack_of_interest': {'title': 'Lack of appreciation and care', 'title_ar': 'نقص التقدير والرعاية', 'icon': 'heart-broken', 'description': 'Support for feeling undervalued and neglected', 'description_ar': 'الدعم للشعور بعدم التقدير والإهمال'},
            'suspicion': {'title': 'Doubt and Jealousy', 'title_ar': 'الشك والغيرة', 'icon': 'question-circle', 'description': 'Help managing trust issues and jealousy', 'description_ar': 'المساعدة في إدارة مشاكل الثقة والغيرة'},
            'emotional_emptiness': {'title': 'Emotional Vacuum', 'title_ar': 'الفراغ العاطفي', 'icon': 'heart', 'description': 'Support for emotional emptiness and disconnection', 'description_ar': 'الدعم للفراغ العاطفي والانفصال'},
            'social_phobia': {'title': 'Social phobia', 'title_ar': 'الرهاب الاجتماعي', 'icon': 'users-slash', 'description': 'Treatment for social anxiety and fear', 'description_ar': 'علاج القلق الاجتماعي والخوف'},
            'panic': {'title': 'Panic', 'title_ar': 'نوبات الهلع', 'icon': 'exclamation-circle', 'description': 'Help with panic attacks and anxiety', 'description_ar': 'المساعدة في نوبات الهلع والقلق'},
            'schizophrenia': {'title': 'Schizophrenia disorder', 'title_ar': 'الفصام', 'icon': 'brain', 'description': 'Treatment for schizophrenia and related disorders', 'description_ar': 'علاج الفصام والاضطرابات المرتبطة به'},
            'mood_disorder': {'title': 'Mood disorder', 'title_ar': 'اضطراب المزاج', 'icon': 'smile', 'description': 'Treatment for depression and mood swings', 'description_ar': 'علاج الاكتئاب وتقلبات المزاج'}
        }

        for key, mapping in specialty_mappings.items():
            specialty_data = {**mapping, **specialty_defaults}
            specialty, created = Specialty.objects.get_or_create(
                title=mapping['title'],
                defaults=specialty_data
            )
            specialties[key] = specialty
            action = 'Created' if created else 'Retrieved'
            self.stdout.write(self.style.SUCCESS(f'{action} specialty: {specialty.title}'))

        doctors_data = [
            {
                'name': 'Ali Mohammed Zairi',
                'name_arabic': 'علي محمد زيري',
                'sex': 'male',
                'email': 'ali.zairi@example.com',
                'phone': '+966500000001',
                'experience': 'Consultant Psychiatrist and Family Medicine, holds two PhDs in Psychiatry, has provided more than 30,000 consultations for all ages, children, and adults',
                'category': 'consultant',
                'language_in_sessions': 'both',
                'license_number': 'PSY001',
                'profile_english': 'Consultant Psychiatrist and Family Medicine, holds two PhDs in Psychiatry, has provided more than 30,000 consultations for all ages, children, and adults',
                'profile_arabic': 'استشاري الطب النفسي وطب الأسرة، يحمل درجتي دكتوراه في الطب النفسي، قدم أكثر من 30,000 استشارة لجميع الأعمار والأطفال والبالغين',
                'status': 'approved',
                'account_holder_name': 'Ali Mohammed Zairi',
                'account_number': '1234567890',
                'iban_number': 'SA0380000000608010167519',
                'specialties': ['obsession', 'addiction', 'relationships', 'lack_of_interest', 'suspicion', 'emotional_emptiness']
            },
            {
                'name': 'Nouf Al Zahrani',
                'name_arabic': 'نوف الزهراني',
                'sex': 'female',
                'email': 'nouf.zahrani@example.com',
                'phone': '+966500000002',
                'experience': 'Psychologist, behavioral therapy, marital therapy, family counselling, children and adults',
                'category': 'specialist',
                'language_in_sessions': 'both',
                'license_number': 'PSY002',
                'profile_english': 'Psychologist, behavioral therapy, marital therapy, family counselling, children and adults',
                'profile_arabic': 'أخصائية نفسية، علاج سلوكي، علاج زوجي، استشارات أسرية، أطفال وبالغين',
                'status': 'approved',
                'account_holder_name': 'Nouf Al Zahrani',
                'account_number': '0987654321',
                'iban_number': 'SA0380000000608010167520',
                'specialties': ['lack_of_interest', 'relationships', 'obsession', 'social_phobia', 'emotional_emptiness', 'suspicion']
            },
            {
                'name': 'Dr. Mohamed Ibrahim Ahmed Hamzy',
                'name_arabic': 'د. محمد إبراهيم أحمد حمزي',
                'sex': 'male',
                'email': 'mohamed.hamzy@example.com',
                'phone': '+966500000003',
                'experience': 'Dr. Muhammad Al-Hamzi, Consultant Psychiatrist, Treatment of psychological disorders for adults over 18 years of age, psychological depression, psychological anxiety, and psychological stress',
                'category': 'consultant',
                'language_in_sessions': 'both',
                'license_number': 'PSY003',
                'profile_english': 'Dr. Muhammad Al-Hamzi, Consultant Psychiatrist, Treatment of psychological disorders for adults over 18 years of age, psychological depression, psychological anxiety, and psychological stress',
                'profile_arabic': 'د. محمد الحمزي، استشاري الطب النفسي، علاج الاضطرابات النفسية للبالغين فوق 18 عاماً، الاكتئاب النفسي، القلق النفسي، والتوتر النفسي',
                'status': 'approved',
                'account_holder_name': 'Mohamed Ibrahim Ahmed Hamzy',
                'account_number': '1122334455',
                'iban_number': 'SA0380000000608010167521',
                'specialties': ['suspicion', 'lack_of_interest', 'obsession', 'schizophrenia', 'panic', 'social_phobia']
            },
            {
                'name': 'Imad Ali Al-Ruby',
                'name_arabic': 'عماد علي الروبي',
                'sex': 'male',
                'email': 'imad.ruby@example.com',
                'phone': '+966500000004',
                'experience': 'I studied at Cairo University, Faculty of Medicine, Kasr El Aini. Bachelor of Medicine in 2000. Then, I obtained a specialization and postgraduate degree in medicine',
                'category': 'specialist',
                'language_in_sessions': 'both',
                'license_number': 'PSY004',
                'profile_english': 'I studied at Cairo University, Faculty of Medicine, Kasr El Aini. Bachelor of Medicine in 2000. Then, I obtained a specialization and postgraduate degree in medicine',
                'profile_arabic': 'درست في جامعة القاهرة، كلية الطب، قصر العيني. بكالوريوس الطب عام 2000. ثم حصلت على تخصص ودرجة الدراسات العليا في الطب',
                'status': 'approved',
                'account_holder_name': 'Imad Ali Al-Ruby',
                'account_number': '5544332211',
                'iban_number': 'SA0380000000608010167522',
                'specialties': ['relationships', 'addiction', 'obsession', 'panic', 'social_phobia', 'suspicion']
            },
            {
                'name': 'Maha Mohammed',
                'name_arabic': 'مها محمد',
                'sex': 'female',
                'email': 'maha.mohammed@example.com',
                'phone': '+966500000005',
                'experience': 'Psychologist, sympathetic, understanding, supportive and helpful to you no matter what your problem is',
                'category': 'specialist',
                'language_in_sessions': 'both',
                'license_number': 'PSY005',
                'profile_english': 'Psychologist, sympathetic, understanding, supportive and helpful to you no matter what your problem is',
                'profile_arabic': 'أخصائية نفسية، متعاطفة، متفهمة، داعمة ومساعدة لك مهما كانت مشكلتك',
                'status': 'approved',
                'account_holder_name': 'Maha Mohammed',
                'account_number': '6677889900',
                'iban_number': 'SA0380000000608010167523',
                'specialties': ['suspicion', 'lack_of_interest', 'relationships', 'mood_disorder', 'social_phobia', 'emotional_emptiness']
            },
            {
                'name': 'Dr. Bandar Al-Aqeel',
                'name_arabic': 'د. بندر العقيل',
                'sex': 'male',
                'email': 'bandar.aqeel@example.com',
                'phone': '+966500000006',
                'experience': 'He obtained a Bachelor of Medicine and Surgery from King Saud University in 2006, then completed his training in Canada and obtained a board and fellowship in psychiatry',
                'category': 'consultant',
                'language_in_sessions': 'both',
                'license_number': 'PSY006',
                'profile_english': 'He obtained a Bachelor of Medicine and Surgery from King Saud University in 2006, then completed his training in Canada and obtained a board and fellowship in psychiatry',
                'profile_arabic': 'حصل على بكالوريوس الطب والجراحة من جامعة الملك سعود عام 2006، ثم أكمل تدريبه في كندا وحصل على البورد والزمالة في الطب النفسي',
                'status': 'approved',
                'account_holder_name': 'Bandar Al-Aqeel',
                'account_number': '0011223344',
                'iban_number': 'SA0380000000608010167524',
                'specialties': ['mood_disorder', 'schizophrenia', 'panic', 'social_phobia', 'obsession']
            }
        ]

        for doctor_data in doctors_data:
            try:
                # Check if doctor already exists
                if Doctor.objects.filter(email=doctor_data['email']).exists():
                    self.stdout.write(self.style.WARNING(f"Doctor {doctor_data['name']} already exists, skipping..."))
                    continue

                # Extract specialties
                doctor_specialties = [specialties[specialty_key] for specialty_key in doctor_data.pop('specialties')]
                
                # Create doctor
                doctor = Doctor.objects.create(**doctor_data)
                
                # Add specialties
                doctor.specialities.set(doctor_specialties)
                
                self.stdout.write(self.style.SUCCESS(f'Successfully added doctor: {doctor.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to add doctor {doctor_data["name"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully added all sample doctors')) 