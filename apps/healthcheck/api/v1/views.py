from django.core.cache import cache
from django.db import connection

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Healthcheck endpoint for monitoring application status.
    Checks:
    - Redis (via Django cache)
    - Postgres (simple SELECT)
    Returns 200 if all services respond correctly.
    """

    def get(self, request):
        health = {
            "redis": "ok",
            "postgres": "ok",
        }

        try:
            cache.set("healthcheck", "ok", timeout=5)
            if cache.get("healthcheck") != "ok":
                raise Exception("Redis did not return expected value")
        except Exception as e:
            health["redis"] = f"error: {str(e)}"

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result is None or result[0] != 1:
                    raise Exception("DB did not return 1")
        except Exception as e:
            health["postgres"] = f"error: {str(e)}"

        status_code = (
            status.HTTP_200_OK
            if all(v == "ok" for v in health.values())
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(
            data={
                "type": "healthcheck",
                "id": "singleton",
                "attributes": health,
            },
            status=status_code,
        )
