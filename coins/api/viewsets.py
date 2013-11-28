from rest_framework import viewsets, mixins

import serializers
from coins.models import Mint, Country, Currency, Collection


class MintViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Mint.objects.select_related('country').prefetch_related('marks')
    serializer_class = serializers.MintSerializer


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects \
                      .select_related('current_currency') \
                      .prefetch_related('currencyhistory_set') \
                      .prefetch_related('currencyhistory_set__currency') \
                      .order_by('iso')
    serializer_class = serializers.CountrySerializer


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects \
                       .prefetch_related('countries') \
                       .order_by('iso')
    serializer_class = serializers.CurrencySerializer


class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Collection.objects.select_related('owner')
    serializer_class = serializers.CollectionSerializer
