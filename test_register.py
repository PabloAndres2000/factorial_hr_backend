#!/usr/bin/env python
"""
Script de prueba para el endpoint de registro de usuarios
Uso: python test_register.py
"""

import requests
import json
from datetime import datetime


def test_register_user():
    """Prueba el endpoint de registro de usuarios"""
    
    # URL del endpoint (ajusta según tu configuración)
    url = "http://localhost:8000/api/auth/register/"
    
    # Datos del usuario a registrar (genera email único usando timestamp)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        "name": "Usuario",
        "last_name": "Prueba",
        "family_name": "Test",
        "email": f"test.user.{timestamp}@example.com",
        "password": "TestPassword123!",
        "password_confirmation": "TestPassword123!"
    }
    
    print("=" * 60)
    print("PROBANDO ENDPOINT DE REGISTRO")
    print("=" * 60)
    print(f"\n📤 Enviando petición a: {url}")
    print(f"\n📋 Datos enviados:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("\n" + "-" * 60)
    
    try:
        # Realizar la petición
        response = requests.post(url, json=data)
        
        # Mostrar resultado
        print(f"\n✅ Código de estado: {response.status_code}")
        
        if response.status_code == 201:
            print("\n🎉 ¡REGISTRO EXITOSO!")
            print("\n📨 Respuesta del servidor:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            
            # Guardar tokens para uso posterior
            response_data = response.json()
            if 'token' in response_data:
                print("\n🔑 Token de acceso guardado en: tokens.txt")
                with open('tokens.txt', 'w') as f:
                    f.write(f"Access Token: {response_data['token']}\n")
                    f.write(f"Refresh Token: {response_data['refresh']}\n")
                    f.write(f"Email: {response_data['user']['email']}\n")
                    f.write(f"User ID: {response_data['user']['id']}\n")
        else:
            print("\n❌ ERROR EN EL REGISTRO")
            print("\n📨 Respuesta del servidor:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("Asegúrate de que el servidor Django esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
    
    print("\n" + "=" * 60)


def test_register_with_errors():
    """Prueba casos de error comunes"""
    
    url = "http://localhost:8000/api/auth/register/"
    
    print("\n" + "=" * 60)
    print("PROBANDO CASOS DE ERROR")
    print("=" * 60)
    
    # Test 1: Contraseñas no coinciden
    print("\n🧪 Test 1: Contraseñas no coinciden")
    data = {
        "name": "Test",
        "last_name": "User",
        "family_name": "Error",
        "email": "test@example.com",
        "password": "Password123",
        "password_confirmation": "DifferentPassword123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Código: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 2: Email inválido
    print("\n🧪 Test 2: Email inválido")
    data = {
        "name": "Test",
        "last_name": "User",
        "family_name": "Error",
        "email": "email-invalido",
        "password": "Password123",
        "password_confirmation": "Password123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Código: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 3: Contraseña muy corta
    print("\n🧪 Test 3: Contraseña muy corta")
    data = {
        "name": "Test",
        "last_name": "User",
        "family_name": "Error",
        "email": "test2@example.com",
        "password": "123",
        "password_confirmation": "123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Código: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 4: Campos faltantes
    print("\n🧪 Test 4: Campos faltantes")
    data = {
        "name": "Test",
        "email": "test3@example.com",
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Código: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n🚀 Script de Prueba - Endpoint de Registro de Usuarios\n")
    
    # Prueba registro exitoso
    test_register_user()
    
    # Pregunta si quiere probar casos de error
    print("\n¿Deseas probar casos de error? (s/n): ", end="")
    try:
        choice = input().lower()
        if choice == 's':
            test_register_with_errors()
    except:
        pass
    
    print("\n✅ Pruebas completadas\n")

