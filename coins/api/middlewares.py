from django import http
from django.core.urlresolvers import reverse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import exceptions


class ErrorsMiddleware(object):
    def process_response(self, request, response):
        if (request.path.startswith(reverse('api-root')) and
                not isinstance(response, Response)):
            @api_view([request.method])
            def error(request, response):
                if isinstance(response, http.HttpResponseBadRequest):
                    raise exceptions.ParseError
                elif isinstance(response, http.HttpResponseNotFound):
                    raise exceptions.NotFound
                elif isinstance(response, http.HttpResponseForbidden):
                    raise exceptions.PermissionDenied
                elif isinstance(response, http.HttpResponseNotAllowed):
                    raise exceptions.MethodNotAllowed
                elif isinstance(response, http.HttpResponseGone):
                    raise exceptions.Gone
                elif isinstance(response, http.HttpResponseServerError):
                    raise exceptions.ServerError
                else:
                    return response

            response = error(request, response)

            if hasattr(response, 'render'):
                response.render()

        return response
