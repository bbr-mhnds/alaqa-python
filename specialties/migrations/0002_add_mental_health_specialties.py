from django.db import migrations
import uuid

def add_specialties(apps, schema_editor):
    Specialty = apps.get_model('specialties', 'Specialty')
    specialties = [
        {
            "title": "Obsessive",
            "title_ar": "الوسواس القهري",
            "icon": "brain",
            "description": "Treatment for obsessive thoughts and compulsive behaviors",
            "description_ar": "علاج الأفكار الوسواسية والسلوكيات القهرية"
        },
        {
            "title": "Substance Abuse",
            "title_ar": "إدمان المخدرات",
            "icon": "pills",
            "description": "Treatment for drug and alcohol addiction",
            "description_ar": "علاج إدمان المخدرات والكحول"
        },
        {
            "title": "Relationships problems",
            "title_ar": "مشاكل العلاقات",
            "icon": "users",
            "description": "Help with relationship and interpersonal issues",
            "description_ar": "المساعدة في مشاكل العلاقات والتواصل بين الأشخاص"
        },
        {
            "title": "Lack of appreciation and care",
            "title_ar": "نقص التقدير والرعاية",
            "icon": "heart-broken",
            "description": "Support for feeling undervalued and neglected",
            "description_ar": "الدعم للشعور بعدم التقدير والإهمال"
        },
        {
            "title": "Doubt and jealousy",
            "title_ar": "الشك والغيرة",
            "icon": "question-circle",
            "description": "Help managing trust issues and jealousy",
            "description_ar": "المساعدة في إدارة مشاكل الثقة والغيرة"
        },
        {
            "title": "Emotional vacuum",
            "title_ar": "الفراغ العاطفي",
            "icon": "heart",
            "description": "Support for emotional emptiness and disconnection",
            "description_ar": "الدعم للفراغ العاطفي والانفصال"
        },
        {
            "title": "Social phobia",
            "title_ar": "الرهاب الاجتماعي",
            "icon": "users-slash",
            "description": "Treatment for social anxiety and fear",
            "description_ar": "علاج القلق الاجتماعي والخوف"
        },
        {
            "title": "Panic",
            "title_ar": "نوبات الهلع",
            "icon": "exclamation-circle",
            "description": "Help with panic attacks and anxiety",
            "description_ar": "المساعدة في نوبات الهلع والقلق"
        },
        {
            "title": "Schizophrenia Disorder",
            "title_ar": "الفصام",
            "icon": "brain",
            "description": "Treatment for schizophrenia and related disorders",
            "description_ar": "علاج الفصام والاضطرابات المرتبطة به"
        },
        {
            "title": "Mood disorder",
            "title_ar": "اضطراب المزاج",
            "icon": "smile",
            "description": "Treatment for depression and mood swings",
            "description_ar": "علاج الاكتئاب وتقلبات المزاج"
        },
        {
            "title": "Fear of death",
            "title_ar": "الخوف من الموت",
            "icon": "skull",
            "description": "Help managing death anxiety",
            "description_ar": "المساعدة في إدارة القلق من الموت"
        },
        {
            "title": "Disorder",
            "title_ar": "اضطراب",
            "icon": "exclamation-triangle",
            "description": "General mental health support",
            "description_ar": "الدعم النفسي العام"
        },
        {
            "title": "Delusion of disease",
            "title_ar": "توهم المرض",
            "icon": "hospital",
            "description": "Treatment for hypochondria and health anxiety",
            "description_ar": "علاج توهم المرض والقلق الصحي"
        },
        {
            "title": "Isolation and introversion",
            "title_ar": "العزلة والانطواء",
            "icon": "user-lock",
            "description": "Support for social withdrawal and isolation",
            "description_ar": "الدعم للانسحاب الاجتماعي والعزلة"
        },
        {
            "title": "Dealing with self blame",
            "title_ar": "التعامل مع لوم الذات",
            "icon": "user-shield",
            "description": "Help with self-criticism and guilt",
            "description_ar": "المساعدة في النقد الذاتي والشعور بالذنب"
        },
        {
            "title": "Sleep disorders",
            "title_ar": "اضطرابات النوم",
            "icon": "bed",
            "description": "Treatment for insomnia and sleep issues",
            "description_ar": "علاج الأرق ومشاكل النوم"
        },
        {
            "title": "Psychological stress",
            "title_ar": "الضغط النفسي",
            "icon": "brain",
            "description": "Help managing psychological stress",
            "description_ar": "المساعدة في إدارة الضغط النفسي"
        },
        {
            "title": "Low self esteem",
            "title_ar": "تدني تقدير الذات",
            "icon": "user-minus",
            "description": "Support for building self-esteem",
            "description_ar": "الدعم لبناء تقدير الذات"
        },
        {
            "title": "Post-traumatic stress disorder",
            "title_ar": "اضطراب ما بعد الصدمة",
            "icon": "bolt",
            "description": "Treatment for PTSD and trauma",
            "description_ar": "علاج اضطراب ما بعد الصدمة والصدمات النفسية"
        },
        {
            "title": "Anorexia",
            "title_ar": "فقدان الشهية",
            "icon": "weight",
            "description": "Treatment for eating disorders",
            "description_ar": "علاج اضطرابات الأكل"
        }
    ]

    for specialty_data in specialties:
        specialty_data.update({
            "id": uuid.uuid4(),
            "background_color": "#f8f9fa",
            "color_class": "bg-light",
            "total_time_call": 30,
            "warning_time_call": 5,
            "alert_time_call": 2,
            "status": True
        })
        Specialty.objects.create(**specialty_data)

def remove_specialties(apps, schema_editor):
    Specialty = apps.get_model('specialties', 'Specialty')
    Specialty.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('specialties', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_specialties, remove_specialties),
    ] 