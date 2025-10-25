# Sistema de Autenticación OAuth Multi-Proveedor

## Descripción

El sistema de autenticación OAuth ha sido refactorizado para soportar múltiples proveedores de manera flexible y extensible. Actualmente soporta Google, Microsoft/Outlook y GitHub, con la capacidad de agregar fácilmente nuevos proveedores.

## Configuración

### Settings (factorial_hr/settings/base.py)

```python
OAUTH_PROVIDERS = {
    'google': {
        'well_known_url': 'https://accounts.google.com/.well-known/openid-configuration',
        'audience': 'tu-google-client-id',
        'display_name': 'Google',
        'enabled': True,
    },
    'microsoft': {
        'well_known_url': 'https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
        'audience': 'tu-microsoft-client-id',
        'display_name': 'Microsoft Outlook',
        'enabled': True,
    },
    'github': {
        'well_known_url': 'https://token.actions.githubusercontent.com/.well-known/openid-configuration',
        'audience': 'tu-github-client-id',
        'display_name': 'GitHub',
        'enabled': False,  # Deshabilitado por defecto
    }
}

DEFAULT_OAUTH_PROVIDER = 'google'
```

## Endpoints Disponibles

### 1. Listar Proveedores Disponibles

```
GET /api/authentications/providers/
```

**Respuesta:**

```json
{
  "providers": [
    {
      "name": "google",
      "display_name": "Google",
      "well_known_url": "https://accounts.google.com/.well-known/openid-configuration"
    },
    {
      "name": "microsoft",
      "display_name": "Microsoft Outlook",
      "well_known_url": "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
    }
  ],
  "default_provider": "google"
}
```

### 2. Login OAuth (Método 1: Proveedor en Body)

```
POST /api/authentications/external-login/
```

**Body:**

```json
{
  "access_token": "tu-access-token",
  "provider": "google" // Opcional, usa el proveedor por defecto si no se especifica
}
```

### 3. Login OAuth (Método 2: Proveedor en URL)

```
POST /api/authentications/external-login/google/
POST /api/authentications/external-login/microsoft/
POST /api/authentications/external-login/github/
```

**Body:**

```json
{
  "access_token": "tu-access-token"
}
```

**Respuesta (ambos métodos):**

```json
{
  "token": "django-auth-token",
  "refresh": "refresh-token",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "first_name": "Nombre"
  },
  "provider": "google",
  "external_claims": {
    // Claims del token OAuth
  }
}
```

### 4. Refresh Token

```
POST /api/authentications/refresh/
```

**Body:**

```json
{
  "refresh": "tu-refresh-token"
}
```

## Agregar Nuevos Proveedores

### 1. Crear la Clase del Proveedor

En `factorial_hr/apps/auth/services/oauth_provider_client.py`:

```python
class NuevoProveedorOAuth(OAuthProvider):
    """Proveedor OAuth para Nuevo Proveedor"""

    def extract_user_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'email': payload.get("email"),
            'name': payload.get("name"),
            'first_name': payload.get("given_name"),
            'last_name': payload.get("family_name"),
            'picture': payload.get("picture"),
        }

    def get_provider_name(self) -> str:
        return "nuevo_proveedor"
```

### 2. Registrar en el Factory

En la misma clase `OAuthProviderFactory`:

```python
_providers = {
    'google': GoogleOAuthProvider,
    'microsoft': MicrosoftOAuthProvider,
    'github': GitHubOAuthProvider,
    'nuevo_proveedor': NuevoProveedorOAuth,  # Agregar aquí
}
```

### 3. Configurar en Settings

En `factorial_hr/settings/base.py`:

```python
OAUTH_PROVIDERS = {
    # ... proveedores existentes ...
    'nuevo_proveedor': {
        'well_known_url': 'https://nuevo-proveedor.com/.well-known/openid-configuration',
        'audience': 'tu-client-id',
        'display_name': 'Nuevo Proveedor',
        'enabled': True,
    }
}
```

## Arquitectura

### Patrón Factory

- `OAuthProviderFactory`: Crea instancias de proveedores OAuth
- `OAuthProvider`: Clase base abstracta para todos los proveedores
- Implementaciones específicas: `GoogleOAuthProvider`, `MicrosoftOAuthProvider`, etc.

### Beneficios

1. **Extensibilidad**: Fácil agregar nuevos proveedores
2. **Mantenibilidad**: Cada proveedor maneja su propia lógica de extracción de datos
3. **Flexibilidad**: Múltiples formas de especificar el proveedor
4. **Compatibilidad**: Mantiene compatibilidad con el código existente
5. **Configurabilidad**: Proveedores pueden habilitarse/deshabilitarse dinámicamente

## Uso en el Frontend

### JavaScript/TypeScript

```javascript
// Listar proveedores disponibles
const providers = await fetch("/api/authentications/providers/").then((r) =>
  r.json()
);

// Login con Google
const loginWithGoogle = async (accessToken) => {
  const response = await fetch("/api/authentications/external-login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      access_token: accessToken,
      provider: "google",
    }),
  });
  return response.json();
};

// Login con Microsoft (usando URL)
const loginWithMicrosoft = async (accessToken) => {
  const response = await fetch(
    "/api/authentications/external-login/microsoft/",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        access_token: accessToken,
      }),
    }
  );
  return response.json();
};
```

## Migración desde el Sistema Anterior

El sistema es completamente compatible hacia atrás. El endpoint existente seguirá funcionando usando el proveedor por defecto (Google) si no se especifica ningún proveedor.
