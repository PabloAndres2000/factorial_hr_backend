# 📧 Guía de Configuración del Sistema de Emails

## Pasos para Configurar el Envío de Emails

### Opción 1: Usar Gmail (Recomendado para desarrollo)

#### 1. Habilitar la Verificación en 2 Pasos

1. Ve a tu cuenta de Google: https://myaccount.google.com/security
2. En la sección "Acceso a Google", haz clic en "Verificación en 2 pasos"
3. Sigue las instrucciones para habilitarla (necesitarás tu teléfono)

#### 2. Generar una Contraseña de Aplicación

1. Una vez habilitada la verificación en 2 pasos, ve a: https://myaccount.google.com/apppasswords
2. En "Seleccionar app", elige "Correo"
3. En "Seleccionar dispositivo", elige el dispositivo que uses o "Otro" y escribe "Factorial HR"
4. Haz clic en "Generar"
5. Google te mostrará una contraseña de 16 caracteres (ejemplo: `abcd efgh ijkl mnop`)
6. **¡IMPORTANTE!** Copia esta contraseña, solo se muestra una vez

#### 3. Configurar las Variables de Entorno

Edita el archivo `env/local.env` (o créalo si no existe copiando `env/example.env`):

```bash
# ==========================================
# CONFIGURACIÓN DE EMAIL
# ==========================================
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"

# Tu correo de Gmail
EMAIL_HOST_USER="tu-email@gmail.com"

# La contraseña de aplicación que generaste (sin espacios)
SENDER_APPLICATION_PASSWORD="abcdefghijklmnop"

# URL del frontend (para los links en los emails)
FRONT_URL="http://localhost:3000"
```

**Notas importantes:**

- Usa tu email completo de Gmail en `EMAIL_HOST_USER`
- La contraseña de aplicación NO tiene espacios (quita los espacios si los copiaste)
- NO uses tu contraseña normal de Gmail, usa la contraseña de aplicación
- Si no tienes frontend, puedes dejarlo en `http://localhost:3000`

#### 4. Verificar la Configuración

Una vez configurado, ejecuta el servidor:

```bash
python manage.py runserver
```

Y prueba registrando un usuario. Deberías recibir el email de bienvenida.

---

### Opción 2: Usar Outlook/Hotmail

#### Configuración para Outlook:

```bash
EMAIL_HOST="smtp-mail.outlook.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="tu-email@outlook.com"
SENDER_APPLICATION_PASSWORD="tu-contraseña-de-outlook"
```

**Nota:** Con Outlook, generalmente puedes usar tu contraseña normal, pero si tienes verificación en 2 pasos activada, necesitarás una contraseña de aplicación similar a Gmail.

---

### Opción 3: Backend de Consola (Solo para Pruebas)

Si solo quieres probar el sistema sin configurar un email real, puedes usar el backend de consola que muestra los emails en la terminal:

1. Edita `factorial_hr/settings/local.py` (o créalo si no existe):

```python
from .base import *

# Mostrar emails en la consola en lugar de enviarlos
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

2. Ejecuta el servidor y verás los emails en la terminal donde corre Django.

---

## Ejemplo Completo de Archivo `env/local.env`

```bash
# ==========================================
# CONFIGURACIÓN DE SEGURIDAD
# ==========================================
SECRET_KEY="django-insecure-cambiar-en-produccion-abc123xyz"

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================
POSTGRES_NAME="factorial_hr_db"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="tu_password"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"

# ==========================================
# CONFIGURACIÓN DE EMAIL (GMAIL)
# ==========================================
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="tu-email@gmail.com"
SENDER_APPLICATION_PASSWORD="abcdefghijklmnop"

# ==========================================
# CONFIGURACIÓN DE FRONTEND
# ==========================================
FRONT_URL="http://localhost:3000"
```

---

## Troubleshooting - Problemas Comunes

### ❌ Error: "SMTPAuthenticationError (535)"

**Causa:** Credenciales incorrectas

**Solución:**

1. Verifica que `EMAIL_HOST_USER` sea tu email completo
2. Asegúrate de usar la **contraseña de aplicación**, no tu contraseña de Gmail
3. Verifica que la contraseña no tenga espacios
4. Confirma que la verificación en 2 pasos esté habilitada

### ❌ Error: "SMTPServerDisconnected"

**Causa:** Configuración de servidor incorrecta

**Solución:**

1. Verifica que `EMAIL_HOST` sea correcto: `smtp.gmail.com`
2. Verifica que `EMAIL_PORT` sea: `587`
3. Asegúrate de que `EMAIL_USE_TLS` esté en `"True"` (con comillas)

### ❌ No llega el email

**Solución:**

1. Revisa la carpeta de **Spam** en tu email
2. Verifica que el servidor Django esté corriendo
3. Mira los logs del servidor para ver si hay errores
4. Usa el backend de consola para probar primero

### ❌ Error: "No module named 'dotenv'"

**Solución:**

```bash
pip install python-dotenv
```

---

## Probar el Sistema de Emails

### 1. Usando el Script de Prueba

```bash
python test_register.py
```

Esto creará un usuario de prueba y enviará el email automáticamente.

### 2. Usando curl

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "last_name": "User",
    "family_name": "Testing",
    "email": "tu-email@gmail.com",
    "password": "TestPassword123",
    "password_confirmation": "TestPassword123"
  }'
```

**Importante:** Usa tu email real para recibir el correo de prueba.

### 3. Verificar el Email

Después de registrarte, revisa tu bandeja de entrada. Deberías recibir un email con:

- Saludo de bienvenida
- Tu email registrado
- Un botón grande verde "✓ Verificar mi correo electrónico"
- Un link de verificación
- Nota de que el link expira en 24 horas

---

## Nuevos Endpoints Implementados

### 1. Registro de Usuario (Ya existente, ahora mejorado)

```
POST /api/auth/register/
```

### 2. Verificar Email (NUEVO)

```
POST /api/auth/verify-email/
Body: { "token": "el-token-del-email" }
```

### 3. Reenviar Verificación (NUEVO)

```
POST /api/auth/resend-verification/
Body: { "email": "usuario@example.com" }
```

---

## Flujo Completo de Verificación

1. **Usuario se registra** → Recibe email con link
2. **Usuario hace clic en el link** → Frontend extrae el token de la URL
3. **Frontend llama al endpoint** `/api/auth/verify-email/` con el token
4. **Backend verifica** y marca el email como verificado
5. **Usuario puede acceder** a todas las funcionalidades

---

## Configuración para Producción

### Variables de Entorno en Producción

Nunca subas el archivo `local.env` a Git. En producción, configura las variables de entorno directamente:

**Heroku:**

```bash
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=tu-email@gmail.com
heroku config:set SENDER_APPLICATION_PASSWORD=tu-password-app
```

**AWS/DigitalOcean:**
Configura las variables de entorno en el archivo de configuración del servidor o usando el panel de control.

**Docker:**

```yaml
environment:
  - EMAIL_HOST=smtp.gmail.com
  - EMAIL_PORT=587
  - EMAIL_USE_TLS=True
  - EMAIL_HOST_USER=tu-email@gmail.com
  - SENDER_APPLICATION_PASSWORD=tu-password-app
```

---

## Servicios Alternativos (Para Producción)

### SendGrid (Recomendado para producción)

1. Regístrate en https://sendgrid.com/
2. Obtén tu API Key
3. Configura:

```bash
EMAIL_HOST="smtp.sendgrid.net"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="apikey"
SENDER_APPLICATION_PASSWORD="tu-sendgrid-api-key"
```

### Amazon SES

1. Configura AWS SES
2. Obtén credenciales SMTP
3. Configura:

```bash
EMAIL_HOST="email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="tu-smtp-username"
SENDER_APPLICATION_PASSWORD="tu-smtp-password"
```

---

## Checklist de Configuración

- [ ] Verificación en 2 pasos habilitada en Gmail
- [ ] Contraseña de aplicación generada
- [ ] Archivo `env/local.env` creado
- [ ] Variables EMAIL_HOST_USER y SENDER_APPLICATION_PASSWORD configuradas
- [ ] Contraseña sin espacios
- [ ] Servidor Django corriendo
- [ ] Email de prueba enviado exitosamente
- [ ] Email recibido (revisar spam)
- [ ] Link de verificación funciona

---

## Soporte

Si tienes problemas:

1. Verifica los logs del servidor Django
2. Usa el backend de consola primero para probar
3. Revisa que todas las variables estén correctamente escritas
4. Asegúrate de que no haya espacios extras en las variables
5. Confirma que la verificación en 2 pasos esté habilitada en Gmail

---

## 🎉 ¡Listo!

Una vez configurado, el sistema enviará automáticamente:

- ✉️ Email de bienvenida al registrarse
- 🔗 Link de verificación de cuenta
- ⏰ Token con expiración de 24 horas
- 🔒 Seguridad adicional en el proceso de registro
