from django.contrib.auth.hashers import check_password, make_password
from empleados.models import Empleado, Usuario
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics, filters
from django.db.utils import IntegrityError
from empleados.serializers import EmpleadoSerializer
from django_filters.rest_framework import DjangoFilterBackend

class EmpleadoListView(generics.ListAPIView):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nombre', 'cedula', 'email']
    search_fields = ['nombre', 'cedula', 'email']
    ordering_fields = ['nombre', 'cedula', 'email']

@api_view(['POST'])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    
    try:

        usuario = Usuario.objects.filter(username=username).first()

        if usuario and check_password(password, usuario.password):
            refresh = RefreshToken.for_user(usuario)

            return Response({
                "message": "Inicio de sesión exitoso",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "username": usuario.username
            }, status=200)

        return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_400_BAD_REQUEST)
    
    except IntegrityError:
        return Response({"error": "Error de integridad"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def registro_empleados(request):
    data = request.data

    try:
        if Empleado.objects.filter(cedula=data.get('cedula')).exists():
            return Response({
                "error": "La cédula que intentas agregar ya está registrada",
                "success": False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Empleado.objects.filter(email=data.get('email')).exists():
            return Response({
                "error": "El correo que intentas ingresar ya está registrado",
                "success": False
            }, status=status.HTTP_400_BAD_REQUEST)
                        
        serializer = EmpleadoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Empleado registrado exitosamente",
                "empleado": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Error inesperado: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    
@api_view(['GET'])
def empleados_list(request):
    ordering = request.GET.get('ordering', 'nombre') 
    valid_fields = ['nombre', '-nombre', 'cedula', '-cedula', 'fecha_nacimiento', '-fecha_nacimiento', 'email', '-email']

    if ordering not in valid_fields:  
        return Response({"error": "Parámetro de ordenación no válido"}, status=status.HTTP_400_BAD_REQUEST)

    empleados = Empleado.objects.all().order_by(ordering) 
    serializer = EmpleadoSerializer(empleados, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

    
@api_view(['GET', 'PUT', 'DELETE'])
def empleado_detail(request, pk):
    try:
        empleado = Empleado.objects.get(pk=pk)
    except Empleado.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EmpleadoSerializer(empleado)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        try:
            data = request.data
            print(f"Datos recibidos en backend: {data}") 

            if not data:
                return Response({"error": "No se enviaron datos para actualizar"}, status=status.HTTP_400_BAD_REQUEST)

            if 'nombre' in data and Empleado.objects.exclude(id=empleado.id).filter(nombre=data['nombre']).exists():
                return Response({"error": "El nombre ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

            if 'email' in data and Empleado.objects.exclude(id=empleado.id).filter(email=data['email']).exists():
                return Response({"error": "El correo ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = EmpleadoSerializer(empleado, data=data, partial=True)

            if serializer.is_valid():
                empleado = serializer.save()  
                print(f"Empleado actualizado correctamente: {empleado}")  
                return Response(serializer.data, status=status.HTTP_200_OK)

            print(f"Errores en la validación: {serializer.errors}")  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error inesperado: {str(e)}")  
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        try:
            empleado.delete()
            return Response({"message": "Empleado eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['POST'])
def registro_usuario(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Response({"error": "Se requieren username y password"}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(username=username).exists():
        return Response({"error": "El nombre de usuario ya existe"}, status=status.HTTP_400_BAD_REQUEST)

    usuario = Usuario(username=username)
    usuario.set_password(password)
    usuario.save()

    return Response({"message": "Usuario registrado con éxito"}, status=status.HTTP_201_CREATED)
