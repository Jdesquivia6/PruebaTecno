from django.urls import path
from empleados.views import login, registro, empleados_list, empleado_detail, EmpleadoListView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login', login, name='login'),
    path('registro', registro, name='registro'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('empleados', empleados_list, name='empleados_list'),
    path('empleadosFilter/', EmpleadoListView.as_view(), name='empleados_list'),
    path('empleados/<int:pk>', empleado_detail, name='empleado_detail'),
]
