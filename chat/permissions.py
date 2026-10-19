from rest_framework_api_key.permissions import HasAPIKey
import logging

logger = logging.getLogger('django')

class LoggingHasAPIKey(HasAPIKey):
    def has_permission(self, request, view):
        has_perm = super().has_permission(request, view)
        if not has_perm:
            logger.warning(f"API Key denied: {request.method} {request.path}")
            try:
                logger.warning(f"Headers: {dict(request.headers)}")
                logger.warning(f"Query params: {request.query_params}")
                logger.warning(f"Body: {request.body.decode('utf-8')}")
            except Exception as e:
                logger.error(f"Error logging request body: {e}")
        return has_perm
