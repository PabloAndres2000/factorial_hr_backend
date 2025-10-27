# Registro de Usuarios y Sistema de Emails

## Descripción General

Este documento describe el sistema de registro de usuarios locales y el servicio de envío de correos electrónicos implementado en Factorial HR Backend.

## Endpoint de Registro

### URL

```
POST /api/auth/register/
```

### Características

- ✅ No requiere autenticación (AllowAny)
- ✅ Valida todos los campos requeridos
- ✅ Verifica que el email no esté ya registrado
- ✅ Valida que las contraseñas coincidan
- ✅ Hashea la contraseña de forma segura
- ✅ Envía correo de bienvenida automáticamente
- ✅ Retorna tokens de autenticación (access y refresh)

### Campos Requeridos

| Campo                   | Tipo   | Descripción                | Validaciones                           |
| ----------------------- | ------ | -------------------------- | -------------------------------------- |
| `name`                  | string | Nombre del usuario         | Requerido, máximo 100 caracteres       |
| `last_name`             | string | Apellido del usuario       | Requerido, máximo 100 caracteres       |
| `family_name`           | string | Apellido familiar          | Requerido, máximo 100 caracteres       |
| `email`                 | string | Email único del usuario    | Requerido, formato email válido, único |
| `password`              | string | Contraseña del usuario     | Requerido, mínimo 8 caracteres         |
| `password_confirmation` | string | Confirmación de contraseña | Requerido, debe coincidir con password |

### Ejemplo de Petición

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan",
    "last_name": "Pérez",
    "family_name": "García",
    "email": "juan.perez@example.com",
    "password": "MiContraseña123!",
    "password_confirmation": "MiContraseña123!"
  }'
```

### Respuesta Exitosa (201 Created)

```json
{
  "detail": "Usuario registrado exitosamente",
  "email_sent": true,
  "user": {
    "id": 1,
    "email": "juan.perez@example.com",
    "name": "Juan",
    "last_name": "Pérez",
    "family_name": "García",
    "full_name": "Juan García Pérez"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "refresh": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

### Respuestas de Error

#### Email ya registrado (400 Bad Request)

```json
{
  "detail": "Error en los datos proporcionados",
  "errors": {
    "email": ["Este email ya está registrado"]
  }
}
```

#### Contraseñas no coinciden (400 Bad Request)

```json
{
  "detail": "Error en los datos proporcionados",
  "errors": {
    "password_confirmation": ["Las contraseñas no coinciden"]
  }
}
```

#### Campos faltantes (400 Bad Request)

```json
{
  "detail": "Error en los datos proporcionados",
  "errors": {
    "name": ["El nombre es requerido"],
    "email": ["El email es requerido"]
  }
}
```

#### Contraseña muy corta (400 Bad Request)

```json
{
  "detail": "Error en los datos proporcionados",
  "errors": {
    "password": ["La contraseña debe tener al menos 8 caracteres"]
  }
}
```

## Sistema de Envío de Emails

### Servicio de Email

El servicio de email está implementado en:

```
factorial_hr/apps/auth/services/email_service.py
```

### Configuración

Las configuraciones de email se encuentran en `settings/base.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('SENDER_APPLICATION_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', '')
```

### Métodos Disponibles

#### 1. `send_welcome_email(user_email: str, user_name: str) -> bool`

Envía un correo de bienvenida cuando se registra un nuevo usuario.

**Parámetros:**

- `user_email`: Email del usuario registrado
- `user_name`: Nombre del usuario para personalizar el mensaje

**Retorna:**

- `True` si el email se envió exitosamente
- `False` si hubo un error al enviar

**Plantilla del Email:**

- HTML responsive con estilos inline
- Fallback a texto plano
- Diseño moderno con colores de marca

**Ejemplo de uso:**

```python
from factorial_hr.apps.auth.services.email_service import EmailService

email_sent = EmailService.send_welcome_email(
    user_email="juan@example.com",
    user_name="Juan"
)
```

#### 2. `send_password_reset_email(user_email: str, reset_token: str) -> bool`

Método de ejemplo para enviar correos de recuperación de contraseña (funcionalidad futura).

**Parámetros:**

- `user_email`: Email del usuario
- `reset_token`: Token de recuperación

**Nota:** Este método está preparado para implementación futura.

### Plantilla de Email de Bienvenida

El email incluye:

- Saludo personalizado con el nombre del usuario
- Confirmación de cuenta creada
- Email del usuario destacado
- Diseño responsive
- Colores corporativos (#4CAF50 para acentos)

**Vista previa del HTML:**

```html
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #4CAF50;">¡Bienvenido a Factorial HR, Juan!</h2>
      <p>Tu cuenta ha sido creada exitosamente.</p>
      <p>
        Ahora puedes acceder a nuestra plataforma con tu correo electrónico:
      </p>
      <p style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">
        <strong>juan@example.com</strong>
      </p>
      <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
      <p style="font-size: 12px; color: #777;">
        Este es un correo automático, por favor no respondas a este mensaje.
      </p>
    </div>
  </body>
</html>
```

## Configuración de Gmail para Desarrollo

### Paso a Paso

1. **Habilitar verificación en 2 pasos**

   - Ve a https://myaccount.google.com/security
   - Activa la verificación en dos pasos

2. **Generar contraseña de aplicación**

   - Ve a https://myaccount.google.com/apppasswords
   - Selecciona "Correo" como aplicación
   - Selecciona tu dispositivo
   - Copia la contraseña de 16 caracteres generada

3. **Configurar en .env**
   ```bash
   EMAIL_HOST="smtp.gmail.com"
   EMAIL_PORT="587"
   EMAIL_USE_TLS="True"
   EMAIL_HOST_USER="tu-email@gmail.com"
   SENDER_APPLICATION_PASSWORD="xxxx xxxx xxxx xxxx"
   ```

### Troubleshooting

#### Error: "SMTPAuthenticationError"

- Verifica que la contraseña de aplicación sea correcta
- Asegúrate de que la verificación en 2 pasos esté habilitada
- Verifica que el email en `EMAIL_HOST_USER` sea correcto

#### Error: "SMTPServerDisconnected"

- Verifica la configuración de `EMAIL_HOST` y `EMAIL_PORT`
- Asegúrate de que `EMAIL_USE_TLS` esté en "True"

#### El email no llega

- Revisa la carpeta de spam
- Verifica que el servidor esté ejecutándose correctamente
- Revisa los logs de Django para ver errores

## Proveedores de Email Alternativos

### Outlook/Hotmail

```bash
EMAIL_HOST="smtp-mail.outlook.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="tu-email@outlook.com"
SENDER_APPLICATION_PASSWORD="tu-contraseña"
```

### SendGrid

```bash
EMAIL_HOST="smtp.sendgrid.net"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="apikey"
SENDER_APPLICATION_PASSWORD="tu-api-key-de-sendgrid"
```

### Amazon SES

```bash
EMAIL_HOST="email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="tu-smtp-username"
SENDER_APPLICATION_PASSWORD="tu-smtp-password"
```

## Extender el Sistema

### Agregar Nuevos Tipos de Email

Para agregar un nuevo tipo de email, edita `email_service.py`:

```python
@staticmethod
def send_account_verification_email(user_email: str, verification_token: str) -> bool:
    """
    Envía un correo de verificación de cuenta
    """
    try:
        subject = 'Verifica tu cuenta - Factorial HR'
        verification_link = f"{settings.FRONT_URL}/verify?token={verification_token}"

        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Verifica tu cuenta</h2>
                <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
                <a href="{verification_link}">Verificar cuenta</a>
            </body>
        </html>
        """

        plain_message = f"Verifica tu cuenta: {verification_link}"

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )

        return True

    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False
```

### Usar Plantillas de Django

Para emails más complejos, puedes usar el sistema de plantillas de Django:

1. Crear directorio de plantillas:

```bash
mkdir -p factorial_hr/apps/auth/templates/emails
```

2. Crear plantilla HTML:

```html
<!-- factorial_hr/apps/auth/templates/emails/welcome.html -->
<html>
  <body>
    <h2>¡Bienvenido, {{ user_name }}!</h2>
    <p>Tu email es: {{ user_email }}</p>
  </body>
</html>
```

3. Usar en el servicio:

```python
from django.template.loader import render_to_string

html_message = render_to_string('emails/welcome.html', {
    'user_name': user_name,
    'user_email': user_email
})
```

## Testing del Sistema de Emails

### Backend de Consola (Desarrollo)

Para pruebas sin enviar emails reales:

```python
# En settings/local.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Los emails se mostrarán en la consola donde corre el servidor.

### Backend de Archivo

Para guardar emails en archivos:

```python
# En settings/local.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-emails'
```

### Probar el Endpoint con curl

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "last_name": "User",
    "family_name": "Testing",
    "email": "test@example.com",
    "password": "TestPassword123",
    "password_confirmation": "TestPassword123"
  }'
```

### Probar el Endpoint con Python

```python
import requests

response = requests.post(
    'http://localhost:8000/api/auth/register/',
    json={
        'name': 'Test',
        'last_name': 'User',
        'family_name': 'Testing',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'password_confirmation': 'TestPassword123'
    }
)

print(response.status_code)
print(response.json())
```

## Mejores Prácticas

1. **Seguridad**

   - Nunca guardes contraseñas de email en el código
   - Usa variables de entorno para credenciales
   - Implementa rate limiting para prevenir spam

2. **Rendimiento**

   - Considera usar Celery para enviar emails de forma asíncrona
   - Implementa un sistema de colas para grandes volúmenes

3. **Manejo de Errores**

   - Registra errores de email en logs
   - Implementa reintentos automáticos
   - Notifica al equipo si hay fallos persistentes

4. **Contenido**
   - Incluye siempre versión texto plano
   - Prueba en múltiples clientes de email
   - Mantén el diseño simple y responsive

## Próximas Funcionalidades

- [ ] Email de verificación de cuenta
- [ ] Email de recuperación de contraseña
- [ ] Email de cambio de contraseña confirmado
- [ ] Email de cambio de email
- [ ] Sistema de notificaciones por email
- [ ] Plantillas personalizables por empresa
- [ ] Envío asíncrono con Celery
- [ ] Dashboard de emails enviados
