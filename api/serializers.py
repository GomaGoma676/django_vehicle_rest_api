from rest_framework import serializers
from .models import Segment, Brand, Vehicle
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True, 'min_length': 5}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = ['id', 'segment_name']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'brand_name']


class VehicleSerializer(serializers.ModelSerializer):
    segment_name = serializers.ReadOnlyField(source='segment.segment_name', read_only=True)
    brand_name = serializers.ReadOnlyField(source='brand.brand_name', read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_name', 'release_year', 'price', 'segment', 'brand', 'segment_name', 'brand_name']
        extra_kwargs = {'user': {'read_only': True}}