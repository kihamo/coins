from rest_framework import viewsets, mixins
from serializers import MintSerializer, CountrySerializer, CurrencySerializer
from models import Mint, Country, Currency

class MintViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Mint.objects.select_related('country').prefetch_related('marks')
    serializer_class = MintSerializer

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects \
                      .select_related('current_currency') \
                      .prefetch_related('currencyhistory_set') \
                      .prefetch_related('currencyhistory_set__currency') \
                      .order_by('iso')
    serializer_class = CountrySerializer

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects \
                       .prefetch_related('countries') \
                       .order_by('iso')
    serializer_class = CurrencySerializer