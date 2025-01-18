from rest_framework import serializers
from drugs.serializers import DrugSerializer
from .models import Prescription, PrescribedDrug, TestRecommendation

class TestRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestRecommendation
        fields = [
            'id', 'test_name', 'description', 'urgency',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class PrescribedDrugSerializer(serializers.ModelSerializer):
    drug_details = DrugSerializer(source='drug', read_only=True)
    
    class Meta:
        model = PrescribedDrug
        fields = [
            'id', 'drug', 'drug_details', 'dosage', 'frequency',
            'duration', 'duration_unit', 'route', 'instructions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class PrescriptionSerializer(serializers.ModelSerializer):
    prescribed_drugs = PrescribedDrugSerializer(many=True, read_only=True)
    test_recommendations = TestRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'appointment', 'diagnosis', 'notes',
            'follow_up_date', 'prescribed_drugs', 'test_recommendations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class PrescriptionCreateSerializer(serializers.ModelSerializer):
    prescribed_drugs = PrescribedDrugSerializer(many=True)
    test_recommendations = TestRecommendationSerializer(many=True, required=False)
    
    class Meta:
        model = Prescription
        fields = [
            'appointment', 'diagnosis', 'notes', 'follow_up_date',
            'prescribed_drugs', 'test_recommendations'
        ]
    
    def create(self, validated_data):
        prescribed_drugs_data = validated_data.pop('prescribed_drugs')
        test_recommendations_data = validated_data.pop('test_recommendations', [])
        
        prescription = Prescription.objects.create(**validated_data)
        
        # Create prescribed drugs
        for drug_data in prescribed_drugs_data:
            PrescribedDrug.objects.create(prescription=prescription, **drug_data)
        
        # Create test recommendations
        for test_data in test_recommendations_data:
            TestRecommendation.objects.create(prescription=prescription, **test_data)
        
        return prescription

    def update(self, instance, validated_data):
        prescribed_drugs_data = validated_data.pop('prescribed_drugs', [])
        test_recommendations_data = validated_data.pop('test_recommendations', [])
        
        # Update prescription fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update prescribed drugs
        instance.prescribed_drugs.all().delete()
        for drug_data in prescribed_drugs_data:
            PrescribedDrug.objects.create(prescription=instance, **drug_data)
        
        # Update test recommendations
        instance.test_recommendations.all().delete()
        for test_data in test_recommendations_data:
            TestRecommendation.objects.create(prescription=instance, **test_data)
        
        return instance 