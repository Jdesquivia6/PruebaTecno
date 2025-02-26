from rest_framework import serializers
from empleados.models import Empleado

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'cedula', 'fecha_nacimiento', 'email', 'telefono']
