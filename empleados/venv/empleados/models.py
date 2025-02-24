from django.db import models
from django.contrib.auth.hashers import make_password

class Empleado(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
