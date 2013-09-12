from rest_framework import serializers
from models import Mint, Currency, CurrencyHistory, Country

class MintSerializer(serializers.ModelSerializer):
    country = serializers.Field(source='country.name')
    marks = serializers.RelatedField(many=True)

    class Meta:
        model = Mint
        fields = ('id', 'name', 'country', 'marks')

class CurrencySerializer(serializers.ModelSerializer):
    class CountrySerializer(serializers.ModelSerializer):
        url = serializers.HyperlinkedIdentityField(view_name='country-detail')

        class Meta:
            model = Country
            fields = ('id', 'name', 'iso', 'url')

    countries = CountrySerializer(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='currency-detail')

    class Meta:
        model = Currency
        fields = ('id', 'name', 'iso', 'sign', 'url', 'countries')

class CountrySerializer(serializers.ModelSerializer):
    class CurrencySerializer(serializers.ModelSerializer):
        url = serializers.HyperlinkedIdentityField(view_name='currency-detail')

        class Meta:
            model = Currency
            fields = ('id', 'name', 'iso', 'sign', 'url')

    class CurrencyHistorySerializer(serializers.ModelSerializer):
        id = serializers.IntegerField(source='currency.id')
        name = serializers.Field(source='currency.name')
        iso = serializers.Field(source='currency.iso')
        sign = serializers.Field(source='currency.sign')
        url = serializers.HyperlinkedIdentityField(view_name='currency-detail')

        class Meta:
            model = CurrencyHistory
            fields = ('id', 'name', 'iso', 'sign', 'url', 'date_from', 'date_to')

    currencies = CurrencyHistorySerializer(many=True, source='currencyhistory_set')
    url = serializers.HyperlinkedIdentityField(view_name='country-detail')
    current = CurrencySerializer(source='current_currency')

    class Meta:
        model = Country
        fields = ('id', 'name', 'iso', 'url', 'currencies', 'current')