# api/events_serializers.py
from rest_framework import serializers
from .models import Event, CustomUser

class EventSerializer(serializers.ModelSerializer):
    # Opcional: hacerlo explícito (DRF lo puede inferir, pero así queda claro)
    organizer_user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True
    )

    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    gold_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    vip_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "published_at"]

    def validate(self, attrs):
        start = attrs.get("start_datetime", getattr(self.instance, "start_datetime", None))
        end = attrs.get("end_datetime", getattr(self.instance, "end_datetime", None))
        if start and end and end <= start:
            raise serializers.ValidationError({"end_datetime": "Debe ser posterior a start_datetime."})
            for k in ("price", "gold_price", "vip_price"):
                v = attrs.get(k, getattr(self.instance, k, None))
            if v is None:
                raise serializers.ValidationError({k: "Este valor es requerido."})
            if v < 0:
                raise serializers.ValidationError({k: "No puede ser negativo."})
        return attrs
