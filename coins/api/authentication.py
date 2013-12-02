import datetime
from django.utils.timezone import utc
from constance import config
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication \
    as DefaultTokenAuthentication


class TokenAuthentication(DefaultTokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        utc_now = datetime.datetime.utcnow().replace(tzinfo=utc)
        lifetime = config.API_TOKEN_LIFETIME

        if token.created < utc_now - datetime.timedelta(minutes=lifetime):
            raise exceptions.AuthenticationFailed('Token has expired')

        return (token.user, token)
