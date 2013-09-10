from rest_framework import serializers
from models import Mint

class MintSerializer(serializers.ModelSerializer):
    country = serializers.Field(source='country.name')
    marks = serializers.RelatedField(many=True)

    class Meta:
        model = Mint
        fields = ('id', 'name', 'country', 'marks')