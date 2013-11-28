from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from coins.models import DeviceToken
from serializers import DeviceTokenSerializer


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
            return Response(status=status.HTTP_201_CREATED if created
                   else status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
