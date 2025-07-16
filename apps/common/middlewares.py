import logging
import time


logger = logging.getLogger(__name__)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        ip = request.META.get("REMOTE_ADDR", "")
        method = request.method
        path = request.get_full_path()

        response = self.get_response(request)

        duration = time.time() - start_time
        status_code = response.status_code

        logger.info(f"[{method}] {path} | IP: {ip} | Status: {status_code} | Time: {duration:.3f}s")

        return response
