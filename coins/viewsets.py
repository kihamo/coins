from rest_framework import viewsets, mixins
from serializers import MintSerializer, CountrySerializer
from models import Mint, Country

class MintViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Mint.objects.select_related('country').prefetch_related('marks')
    serializer_class = MintSerializer

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects \
                      .select_related('current_currency') \
                      .prefetch_related('currencyhistory_set') \
                      .prefetch_related('currencyhistory_set__currency') \
                      .all()

    serializer_class = CountrySerializer