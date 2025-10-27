# ⚡ Guía Rápida - Configuración de Mailsender en 5 Minutos

## 🎯 Objetivo

Configurar Gmail para que tu aplicación pueda enviar emails automáticamente.

---

## 📋 Paso a Paso

### ✅ PASO 1: Habilitar Verificación en 2 Pasos (2 minutos)

1. Abre esta URL en tu navegador:

   ```
   https://myaccount.google.com/security
   ```

2. Busca la sección **"Acceso a Google"**

3. Haz clic en **"Verificación en 2 pasos"**

4. Sigue las instrucciones (necesitarás tu teléfono):
   - Ingresa tu número de teléfono
   - Recibirás un código por SMS
   - Ingresa el código
   - ✅ ¡Listo!

---

### ✅ PASO 2: Generar Contraseña de Aplicación (2 minutos)

1. Abre esta URL:

   ```
   https://myaccount.google.com/apppasswords
   ```

2. Si te pide iniciar sesión, hazlo

3. Verás dos selectores:

   - En **"Seleccionar app"**: Elige **"Correo"**
   - En **"Seleccionar dispositivo"**: Elige **"Otro (nombre personalizado)"**

4. Escribe: **"Factorial HR Backend"**

5. Haz clic en **"Generar"**

6. Google te mostrará una contraseña de 16 caracteres:

   ```
   Ejemplo: abcd efgh ijkl mnop
   ```

7. **¡MUY IMPORTANTE!**
   - Copia esta contraseña AHORA
   - Solo se muestra una vez
   - Guárdala en un lugar seguro

---

### ✅ PASO 3: Configurar el Archivo .env (1 minuto)

1. Abre o crea el archivo: `env/local.env`

2. Si no existe, copia el archivo de ejemplo:

   ```bash
   cp env/example.env env/local.env
   ```

3. Edita `env/local.env` y agrega:

   ```bash
   # ==========================================
   # CONFIGURACIÓN DE EMAIL
   # ==========================================
   EMAIL_HOST="smtp.gmail.com"
   EMAIL_PORT="587"
   EMAIL_USE_TLS="True"

   # CAMBIA ESTO: Tu email de Gmail
   EMAIL_HOST_USER="tu-email@gmail.com"

   # CAMBIA ESTO: La contraseña de aplicación (SIN ESPACIOS)
   SENDER_APPLICATION_PASSWORD="abcdefghijklmnop"

   # OPCIONAL: URL de tu frontend
   FRONT_URL="http://localhost:3000"
   ```

4. **Reemplaza:**
   - `tu-email@gmail.com` → Tu email real de Gmail
   - `abcdefghijklmnop` → La contraseña que copiaste (¡sin espacios!)

---

### ✅ PASO 4: Aplicar Migraciones (30 segundos)

Abre la terminal en la carpeta del proyecto y ejecuta:

```bash
python manage.py makemigrations
python manage.py migrate
```

**Salida esperada:**

```
Running migrations:
  Applying users.0004_user_email_verified... OK
  Applying authentication.0002_emailverificationtoken... OK
```

---

### ✅ PASO 5: Probar que Funciona (30 segundos)

1. **Inicia el servidor:**

   ```bash
   python manage.py runserver
   ```

2. **En otra terminal, ejecuta el script de prueba:**

   ```bash
   python test_register.py
   ```

3. **Revisa tu email** (el que configuraste)
   - Debería llegar un email de "¡Bienvenido a Factorial HR!"
   - Con un botón verde para verificar tu cuenta
   - Si no está en la bandeja principal, revisa **Spam**

---

## ✅ ¡Listo! Tu Mailsender está Configurado

---

## 🎨 Ejemplo Visual del Email

El usuario recibirá algo así:

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ¡Bienvenido a Factorial HR, Juan!                     ║
║                                                          ║
║  Tu cuenta ha sido creada exitosamente.                ║
║                                                          ║
║  Tu correo electrónico registrado es:                   ║
║  ┌────────────────────────────────────┐                ║
║  │  juan.perez@example.com            │                ║
║  └────────────────────────────────────┘                ║
║                                                          ║
║  ⚠️  VERIFICACIÓN REQUERIDA                            ║
║  Para activar tu cuenta debes verificar tu email        ║
║                                                          ║
║  ┌─────────────────────────────────────────┐           ║
║  │  ✓ Verificar mi correo electrónico     │           ║
║  └─────────────────────────────────────────┘           ║
║                                                          ║
║  Este enlace expirará en 24 horas                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🧪 Probar con tu Propio Email

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi",
    "last_name": "Nombre",
    "family_name": "Real",
    "email": "MI-EMAIL-REAL@gmail.com",
    "password": "MiPassword123",
    "password_confirmation": "MiPassword123"
  }'
```

**Cambia:** `MI-EMAIL-REAL@gmail.com` por tu email real.

---

## ❌ Solución de Problemas

### Problema: "SMTPAuthenticationError"

**Causa:** La contraseña está mal

**Solución:**

1. Verifica que uses la **contraseña de aplicación** (no tu contraseña de Gmail)
2. Asegúrate de que NO tenga espacios: `abcdefghijklmnop`
3. Verifica que `EMAIL_HOST_USER` tenga tu email completo

---

### Problema: No llega el email

**Solución:**

1. ✅ Revisa la carpeta de **Spam**
2. ✅ Verifica que el servidor esté corriendo
3. ✅ Mira los logs en la terminal donde corre Django
4. ✅ Prueba con el backend de consola primero:

En `factorial_hr/settings/local.py`:

```python
from .base import *

# Solo para pruebas - muestra emails en consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

### Problema: "No module named 'dotenv'"

**Solución:**

```bash
pip install python-dotenv
```

---

## 📱 Verificar la Configuración

Ejecuta este comando para verificar que las variables se cargaron:

```bash
python manage.py shell
```

Luego escribe:

```python
from django.conf import settings
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email TLS: {settings.EMAIL_USE_TLS}")
# No imprimas la contraseña por seguridad
print("Contraseña configurada:", "✅" if settings.EMAIL_HOST_PASSWORD else "❌")
```

**Salida esperada:**

```
Email Host: smtp.gmail.com
Email User: tu-email@gmail.com
Email Port: 587
Email TLS: True
Contraseña configurada: ✅
```

---

## 🎯 Checklist Final

- [ ] Verificación en 2 pasos activada en Gmail
- [ ] Contraseña de aplicación generada
- [ ] Archivo `env/local.env` creado y configurado
- [ ] `EMAIL_HOST_USER` = tu email completo
- [ ] `SENDER_APPLICATION_PASSWORD` = contraseña sin espacios
- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Servidor corriendo (`python manage.py runserver`)
- [ ] Prueba ejecutada (`python test_register.py`)
- [ ] Email recibido (revisar spam)

---

## 🎉 ¡Felicitaciones!

Tu sistema de emails está configurado y funcionando. Ahora tu aplicación puede:

✅ Registrar usuarios  
✅ Enviar emails automáticos  
✅ Verificar cuentas por email  
✅ Reenviar emails de verificación  
✅ Gestionar tokens seguros

---

## 📚 Más Información

- **Guía completa:** `CONFIGURACION_EMAIL.md`
- **Documentación API:** `REGISTRO_Y_EMAILS.md`
- **Resumen técnico:** `RESUMEN_FINAL_VERIFICACION.md`

---

**¿Necesitas ayuda?** Revisa los archivos de documentación o verifica los logs del servidor.
