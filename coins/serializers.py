from rest_framework import serializers
from models import Mint, Currency, CurrencyHistory, Country

class MintSerializer(serializers.ModelSerializer):
    country = serializers.Field(source='country.name')
    marks = serializers.RelatedField(many=True)

    class Meta:
        model = Mint
        fields = ('id', 'name', 'country', 'marks')

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name', 'iso', 'sign')

class CurrencyHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='currency.id')
    name = serializers.Field(source='currency.name')
    iso = serializers.Field(source='currency.iso')
    sign = serializers.Field(source='currency.sign')

    class Meta:
        model = CurrencyHistory
        fields = ('id', 'name', 'iso', 'sign', 'date_from', 'date_to')

class CountrySerializer(serializers.ModelSerializer):
    currencies = CurrencyHistorySerializer(many=True, source='currencyhistory_set')
    current = CurrencySerializer(source='current_currency')

    class Meta:
        model = Country
        fields = ('id', 'name', 'iso', 'currencies', 'current')