"""
Serializers for the inventory app using Django REST Framework
"""
from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.Serializer):
    """
    Serializer for Item model
    """
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    quantity = serializers.IntegerField(min_value=0, default=0)
    price = serializers.FloatField(min_value=0.0)
    category = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """Create and return a new Item instance"""
        return Item.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update and return an existing Item instance"""
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Convert instance to representation"""
        if hasattr(instance, 'to_dict'):
            return instance.to_dict()
        return super().to_representation(instance)
