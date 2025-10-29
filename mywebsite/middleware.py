import re
from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    """
    Redirect anonymous users to LOGIN_URL unless path matches LOGIN_EXEMPT_URLS.
    Place after AuthenticationMiddleware in MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        patterns = getattr(settings, 'LOGIN_EXEMPT_URLS', ())
        self.exempt_patterns = [re.compile(p) for p in patterns]

    def __call__(self, request):
        # Allow if already authenticated or for exempted paths
        if request.user.is_authenticated:
            return self.get_response(request)

        path = request.path_info or '/'
        for pattern in self.exempt_patterns:
            if pattern.match(path):
                return self.get_response(request)

        return redirect(settings.LOGIN_URL)

