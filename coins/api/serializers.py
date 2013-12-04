from rest_framework import serializers
from coins.models import DeviceToken, CoinSet, BanknoteSet

'''
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
            fields = ('id', 'name', 'iso', 'sign',
                      'url', 'date_from', 'date_to')

    currencies = CurrencyHistorySerializer(many=True,
                                           source='currencyhistory_set')
    url = serializers.HyperlinkedIdentityField(view_name='country-detail')
    current = CurrencySerializer(source='current_currency')

    class Meta:
        model = Country
        fields = ('id', 'name', 'iso', 'url', 'currencies', 'current')


class CollectionSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField('get_owner_name')
    url = serializers.HyperlinkedIdentityField(view_name='collection-detail')

    class Meta:
        model = Collection
        fields = ('id', 'name', 'owner', 'url')

    def get_owner_name(self, obj):
        name = None

        if obj.owner:
            name = obj.owner.get_full_name().strip()
            if not name:
                name = obj.owner.username

        return name
'''


class DeviceTokenSerializer(serializers.ModelSerializer):
    user = serializers.Field(source='user.username')

    class Meta:
        model = DeviceToken
        fields = ('device', 'token', 'created_at')


class CoinSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinSet


class BanknoteSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BanknoteSet
