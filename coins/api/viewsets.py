from rest_framework import viewsets, mixins
from rest_framework.viewsets import generics
from rest_framework.permissions import IsAuthenticated

import serializers
from coins.models import Mint, Country, Currency, Collection, DeviceToken


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


class DeviceTokenViewSet(viewsets.ViewSetMixin, generics.CreateAPIView):
    model = DeviceToken
    serializer_class = serializers.DeviceTokenSerializer
    permission_classes = (IsAuthenticated,)

    def pre_save(self, obj):
        obj.user = self.request.user
