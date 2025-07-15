from rest_framework_json_api import serializers


class HealthCheckSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, default="singleton")
    attributes = serializers.DictField(
        child=serializers.CharField(), help_text="Service health status dictionary"
    )

    class JSONAPIMeta:
        resource_name = "healthcheck"
