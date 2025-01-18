from django.core.management.base import BaseCommand
from specialties.models import Specialty
import uuid

class Command(BaseCommand):
    help = 'Add mental health specialties to the database'

    def handle(self, *args, **kwargs):
        specialties = [
            {"title": "Obsessives", "title_ar": "الوسواس القهري", "icon": "brain", "description": "Treatment for obsessive thoughts and compulsive behaviors"},
            {"title": "Substance Abuse", "title_ar": "إدمان المخدرات", "icon": "pills", "description": "Treatment for drug and alcohol addiction"},
            {"title": "RelationshipsProblem", "title_ar": "مشاكل العلاقات", "icon": "users", "description": "Help with relationship and interpersonal issues"},
            {"title": "Lack of appreciation and care", "title_ar": "نقص التقدير والرعاية", "icon": "heart-broken", "description": "Support for feeling undervalued and neglected"},
            {"title": "Doubt and Jealousy", "title_ar": "الشك والغيرة", "icon": "question-circle", "description": "Help managing trust issues and jealousy"},
            {"title": "Emotional Vacuum", "title_ar": "الفراغ العاطفي", "icon": "heart", "description": "Support for emotional emptiness and disconnection"},
            {"title": "Social phobia", "title_ar": "الرهاب الاجتماعي", "icon": "users-slash", "description": "Treatment for social anxiety and fear"},
            {"title": "Panic", "title_ar": "نوبات الهلع", "icon": "exclamation-circle", "description": "Help with panic attacks and anxiety"},
            {"title": "Schizophrenia disorder", "title_ar": "الفصام", "icon": "brain", "description": "Treatment for schizophrenia and related disorders"},
            {"title": "Mood disorder", "title_ar": "اضطراب المزاج", "icon": "smile", "description": "Treatment for depression and mood swings"},
            {"title": "Fear of death", "title_ar": "الخوف من الموت", "icon": "skull", "description": "Help managing death anxiety"},
            {"title": "Disorder", "title_ar": "اضطراب", "icon": "exclamation-triangle", "description": "General mental health support"},
            {"title": "Delusion of disease", "title_ar": "توهم المرض", "icon": "hospital", "description": "Treatment for hypochondria and health anxiety"},
            {"title": "Isolation and Introversion", "title_ar": "العزلة والانطواء", "icon": "user-lock", "description": "Support for social withdrawal and isolation"},
            {"title": "Dealing with self blame", "title_ar": "التعامل مع لوم الذات", "icon": "user-shield", "description": "Help with self-criticism and guilt"},
            {"title": "Sleep disorder", "title_ar": "اضطرابات النوم", "icon": "bed", "description": "Treatment for insomnia and sleep issues"},
            {"title": "Phycological stress", "title_ar": "الضغط النفسي", "icon": "brain", "description": "Help managing psychological stress"},
            {"title": "Low self esteem", "title_ar": "تدني تقدير الذات", "icon": "user-minus", "description": "Support for building self-esteem"},
            {"title": "Post-traumatic stress disorder", "title_ar": "اضطراب ما بعد الصدمة", "icon": "bolt", "description": "Treatment for PTSD and trauma"},
            {"title": "Anorexia", "title_ar": "فقدان الشهية", "icon": "weight", "description": "Treatment for eating disorders"}
        ]

        for specialty_data in specialties:
            specialty_data.update({
                "id": uuid.uuid4(),
                "background_color": "#f8f9fa",
                "color_class": "bg-light",
                "total_time_call": 30,
                "warning_time_call": 5,
                "alert_time_call": 4,
                "status": True
            })
            
            # Add Arabic description if not present
            if "description_ar" not in specialty_data:
                specialty_data["description_ar"] = specialty_data["description"]  # You may want to translate this properly
            
            try:
                Specialty.objects.create(**specialty_data)
                self.stdout.write(self.style.SUCCESS(f'Successfully added specialty: {specialty_data["title"]}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to add specialty {specialty_data["title"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Successfully added all mental health specialties')) 