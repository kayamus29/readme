from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class AllowExtensionIframeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Replace with your actual Chrome extension ID
        extension_id = getattr(settings, 'CHROME_EXTENSION_ID', None)
        origin = request.headers.get("Origin", "")
        if extension_id and origin == f"chrome-extension://{extension_id}":
            response['X-Frame-Options'] = 'ALLOW-FROM ' + origin
        return response
