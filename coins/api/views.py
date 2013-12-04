from datetime import datetime
from django.utils.timezone import utc

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from coins.models import DeviceToken, CoinSet, BanknoteSet
from serializers import *


class DeviceTokenView(APIView):
    model = DeviceToken
    serializer_class = DeviceTokenSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = DeviceToken.objects.get_or_create(
                token=serializer.object.token,
                user=self.request.user,
                defaults={'device': serializer.object.device}
            )

            if created:
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenView(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(
                user=serializer.object['user']
            )

            if not created:
                token.created = datetime.utcnow().replace(tzinfo=utc)
                token.save()

            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CoinSetViewSet(viewsets.ModelViewSet):
    serializer_class = CoinSetSerializer
    model = CoinSet


class BanknoteSetViewSet(viewsets.ModelViewSet):
    serializer_class = BanknoteSetSerializer
    model = BanknoteSet


'''
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects \
                      .select_related('current_currency') \
                      .prefetch_related('currencyhistory_set') \
                      .prefetch_related('currencyhistory_set__currency') \
                      .order_by('iso')
    serializer_class = serializers.CountrySerializer

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
'''
