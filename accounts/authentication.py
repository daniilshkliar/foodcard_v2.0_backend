from django.conf import settings

from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        cookie = self.get_cookie(request)
        if cookie is None:
            return None

        token = self.get_validated_token(cookie)

        return (self.get_user(token), token)

    def get_cookie(self, request):
        """
        Extracts the COOKIE containing the JSON web token from the given
        request.
        """
        cookie = request.COOKIES.get(settings.ACCESS_COOKIE_NAME)

        return cookie