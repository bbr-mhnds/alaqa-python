from rest_framework import serializers
from .models import Drug, DrugCategory, DrugDosageForm


class DrugCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugCategory
        fields = ["id", "name", "name_arabic", "status"]


class DrugDosageFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugDosageForm
        fields = ["id", "name", "name_arabic", "status"]


class DrugListSerializer(serializers.ModelSerializer):
    category = DrugCategorySerializer(read_only=True)
    dosage_form = DrugDosageFormSerializer(read_only=True)

    class Meta:
        model = Drug
        fields = [
            "id",
            "name",
            "name_arabic",
            "description",
            "description_arabic",
            "category",
            "dosage_form",
            "strength",
            "manufacturer",
            "status",
            "created_at",
            "updated_at",
        ]


class DrugCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = [
            "name",
            "name_arabic",
            "description",
            "description_arabic",
            "category",
            "dosage_form",
            "strength",
            "manufacturer",
            "status",
        ]

    def validate(self, attrs):
        # Add any custom validation here if needed
        return attrs


class DrugUpdateSerializer(DrugCreateSerializer):
    pass


class DrugStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ["status"]


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = [
            'id', 'name', 'description', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 