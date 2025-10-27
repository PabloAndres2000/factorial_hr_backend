# Factorial HR Backend

Backend del sistema Factorial HR construido con Django y Django REST Framework.

## Características

- 🔐 **Autenticación Multi-proveedor OAuth** (Google, Microsoft, GitHub)
- 👤 **Registro de usuarios local** con validación de campos
- 📧 **Sistema de envío de correos electrónicos** automático
- 🔑 **Autenticación con tokens** (Access y Refresh tokens)
- 📊 **Gestión de usuarios** con permisos y roles
- 🔒 **Validación de contraseñas** seguras

## Configuración

### Variables de Entorno

Copia el archivo `env/example.env` a `env/local.env` y configura las siguientes variables:

```bash
# Seguridad
SECRET_KEY="tu-clave-secreta-django"

# Base de datos PostgreSQL
POSTGRES_NAME="nombre_db"
POSTGRES_USER="usuario_db"
POSTGRES_PASSWORD="contraseña_db"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"

# Configuración de Email (para Gmail)
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="tu-email@gmail.com"
SENDER_APPLICATION_PASSWORD="tu-contraseña-de-aplicación"

# Frontend URL
FRONT_URL="http://localhost:3000"
```

### Configuración de Email con Gmail

Para usar Gmail como servidor de correo:

1. Activa la verificación en dos pasos en tu cuenta de Google: https://myaccount.google.com/security
2. Genera una contraseña de aplicación:
   - Ve a [Contraseñas de aplicaciones de Google](https://myaccount.google.com/apppasswords)
   - Selecciona "Correo" y el dispositivo que uses
   - Copia la contraseña generada (16 caracteres)
   - Pégala en `SENDER_APPLICATION_PASSWORD` (sin espacios)

**📘 Guía Detallada:** Ver [CONFIGURACION_EMAIL.md](CONFIGURACION_EMAIL.md) para instrucciones completas paso a paso.

## Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## API Endpoints

### Autenticación

#### 1. Registro de Usuario

**POST** `/api/auth/register/`

Registra un nuevo usuario local y envía un correo de confirmación.

**Body:**

```json
{
  "name": "Juan",
  "last_name": "Pérez",
  "family_name": "García",
  "email": "juan.perez@example.com",
  "password": "contraseña123",
  "password_confirmation": "contraseña123"
}
```

**Respuesta exitosa (201):**

```json
{
  "detail": "Usuario registrado exitosamente. Por favor verifica tu correo electrónico.",
  "email_sent": true,
  "email_verified": false,
  "user": {
    "id": 1,
    "email": "juan.perez@example.com",
    "name": "Juan",
    "last_name": "Pérez",
    "family_name": "García",
    "full_name": "Juan García Pérez"
  },
  "token": "token_de_acceso",
  "refresh": "token_de_refresh"
}
```

**¿Qué sucede al registrarse?**

1. Se crea el usuario con `email_verified: false`
2. Se genera un token de verificación (válido por 24 horas)
3. Se envía un email con un link de verificación
4. El usuario debe hacer clic en el link para verificar su cuenta

**Validaciones:**

- Todos los campos son requeridos
- El email debe ser válido y único
- La contraseña debe tener al menos 8 caracteres
- La contraseña y su confirmación deben coincidir

#### 2. Login con Email y Password

**POST** `/api/auth/login/`

**Body:**

```json
{
  "email": "juan.perez@example.com",
  "password": "contraseña123"
}
```

#### 3. Login con OAuth (Google, Microsoft)

**POST** `/api/auth/external-login/`

**Body:**

```json
{
  "access_token": "token_de_google_o_microsoft",
  "provider": "google"
}
```

#### 4. Refresh Token

**POST** `/api/auth/refresh/`

**Body:**

```json
{
  "refresh": "tu_refresh_token"
}
```

#### 5. Logout

**POST** `/api/auth/logout/`

**Headers:**

```
Authorization: Token tu_token_de_acceso
```

#### 6. Verificar Email

**POST** `/api/auth/verify-email/`

Verifica el email del usuario usando el token enviado por correo.

**Body:**

```json
{
  "token": "token_recibido_por_email"
}
```

**Respuesta exitosa (200):**

```json
{
  "detail": "Email verificado exitosamente",
  "user": {
    "id": 1,
    "email": "juan.perez@example.com",
    "name": "Juan",
    "email_verified": true
  }
}
```

#### 7. Reenviar Verificación

**POST** `/api/auth/resend-verification/`

Reenvía el correo de verificación si el usuario no lo recibió o expiró.

**Body:**

```json
{
  "email": "juan.perez@example.com"
}
```

#### 8. Listar Proveedores OAuth

**GET** `/api/auth/providers/`

## Arquitectura del Proyecto

```
factorial_hr/
├── apps/
│   ├── auth/               # Autenticación y autorización
│   │   ├── api/           # Endpoints de la API
│   │   │   ├── serializers.py
│   │   │   └── view.py
│   │   ├── services/      # Lógica de negocio
│   │   │   ├── auth_service.py
│   │   │   ├── email_service.py
│   │   │   ├── oauth_provider_client.py
│   │   │   └── token_verifier.py
│   │   ├── repositories/  # Acceso a datos
│   │   └── models.py
│   └── users/             # Gestión de usuarios
│       ├── models.py
│       ├── repositories/
│       └── utils/
├── settings/              # Configuración
│   ├── base.py
│   └── local.py
└── utils/                 # Utilidades comunes
```

## Características del Sistema de Email

El sistema de email incluye:

- ✅ **Email de bienvenida** con link de verificación al registrar un usuario
- 🔗 **Verificación de cuenta** mediante link único (expira en 24 horas)
- 🔄 **Reenvío de verificación** si el email no llegó o expiró
- 📧 **Plantillas HTML** con estilos modernos y botones destacados
- 🔄 **Fallback a texto plano** para clientes de email que no soportan HTML
- 🎨 **Diseño responsive** optimizado para móviles
- 🔒 **Manejo de errores** robusto
- ⏰ **Tokens con expiración** para mayor seguridad

### Extender el Sistema de Email

Para agregar nuevos tipos de email, edita `factorial_hr/apps/auth/services/email_service.py`:

```python
@staticmethod
def send_custom_email(user_email: str, custom_data: dict) -> bool:
    subject = 'Asunto del correo'
    html_message = f"""
    <html>
        <body>
            <!-- Tu plantilla HTML aquí -->
        </body>
    </html>
    """
    plain_message = "Versión en texto plano"

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=html_message,
        fail_silently=False,
    )
    return True
```

## Seguridad

- Las contraseñas se hashean usando el sistema de Django
- Validación de contraseñas según las políticas de Django
- Tokens de autenticación seguros
- Protección CSRF activada
- CORS configurado

## Tecnologías

- **Django 4.2+**
- **Django REST Framework**
- **PostgreSQL**
- **Simple History** (para auditoría)
- **Python-Jose & PyJWT** (para tokens OAuth)

## Desarrollo

Para contribuir al proyecto:

1. Crea una rama desde `main`
2. Implementa tus cambios
3. Asegúrate de que las pruebas pasen
4. Crea un Pull Request

## Licencia

[Especificar licencia]
