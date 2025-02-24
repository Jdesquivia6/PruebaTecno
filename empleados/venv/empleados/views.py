from django.contrib.auth.hashers import check_password, make_password
from empleados.models import Empleado
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

        empleado = Empleado.objects.filter(username=username).first()

        if empleado and check_password(password, empleado.password):
            refresh = RefreshToken.for_user(empleado)

            return Response({
                "message": "Inicio de sesión exitoso",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "username": empleado.username
            }, status=200)

        return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_400_BAD_REQUEST)
    
    except IntegrityError:
        return Response({"error": "Error de integridad"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def registro(request):
    data = request.data

    try:
        if Empleado.objects.filter(username=data.get('username')).exists():
            return Response({
                "error":"El nombre de usuario ya se encuentra registrado"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Empleado.objects.filter(email=data.get('email')).exists():
            return Response({
                "error": "El correo que intentas ingresar ya se encuentra registrado"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = EmpleadoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except IntegrityError:
        return Response({"error": "Error de integridad, posible dato duplicado"}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
def empleados_list(request):
    if request.method == 'GET':
        empleados = Empleado.objects.all()
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
            
            if 'username' in data and Empleado.objects.exclude(id=empleado.id).filter(username=data['username']).exists():
                return Response({"error": "El nombre de usuario ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

            if 'email' in data and Empleado.objects.exclude(id=empleado.id).filter(email=data['email']).exists():
                return Response({"error": "El correo ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = EmpleadoSerializer(empleado, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        try:
            empleado.delete()
            return Response({"message": "Empleado eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
