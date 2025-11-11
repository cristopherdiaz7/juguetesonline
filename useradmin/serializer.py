from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    # is_staff maps directly to the model field; don't set `source` when it matches the field name
    is_staff = serializers.BooleanField(read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'tipo', 'direccion', 'is_staff', 'role']

    def get_role(self, obj):
        # Mapear is_staff a 'admin', si no tomar el campo tipo
        if obj.is_staff:
            return 'admin'
        return obj.tipo or 'comprador'
