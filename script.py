import sys
import requests
import json
import os

def iniciar_flujo_real():
    # 1. Obtener datos frescos y vigentes del servidor Anisette local
    print('[+] Solicitando firmas dinámicas al contenedor Anisette...')
    try:
        res_anisette = requests.get('http://localhost:6969/', timeout=10)
        anisette = res_anisette.json()
        print('[+] Datos Anisette obtenidos (Tiempo actual sincronizado).')
    except Exception as e:
        print(f'[-] Error al conectar con Anisette local: {e}')
        sys.exit(1)

    # 2. Leer las credenciales del config.json
    if not os.path.exists('config.json'):
        print('[-] Error: Falta config.json con tus datos en el repositorio.')
        sys.exit(1)

    with open('config.json', 'r') as f:
        config = json.load(f)

    # Configurar las cabeceras dinámicas que Apple nos exige
    headers_apple = {
        'Content-Type': 'application/json',
        'X-Apple-I-Client-Time': anisette.get('X-Apple-I-Client-Time'),
        'X-Apple-I-MD': anisette.get('X-Apple-I-MD'),
        'X-Apple-I-MD-LU': anisette.get('X-Apple-I-MD-LU'),
        'X-Apple-I-MD-M': anisette.get('X-Apple-I-MD-M'),
        'X-Apple-I-MD-RINFO': anisette.get('X-Apple-I-MD-RINFO'),
        'X-Apple-I-SRL-NO': anisette.get('X-Apple-I-SRL-NO'),
        'X-Apple-I-TimeZone': anisette.get('X-Apple-I-TimeZone'),
        'X-Apple-Locale': 'en_US',
        'X-MMe-Client-Info': '<MacBookPro13,2> <macOS;13.1;22C65> <com.apple.AuthKit/1 (com.apple.dt.Xcode/3594.4.19)>',
        'X-Mme-Device-Id': anisette.get('X-Mme-Device-Id'),
        'User-Agent': 'com.apple.dt.Xcode/3594.4.19 (macOS/13.1;22C65)'
    }

    # 3. FASE DE AUTENTICACIÓN (LOGIN) - Aquí solucionamos el error de expiración
    print(f"[+] Iniciando sesión oficial para: {config.get('apple_id')}")
    
    url_login = "https://gsa.apple.com/grandslam/v1/auth/proxy"
    payload_login = {
        "apple_id": config.get('apple_id'),
        "password": config.get('password'),
        "extended_info": {
            "patch_version": "22C65",
            "product_version": "13.1"
        }
    }

    try:
        # Hacemos el Login real para obtener los accesos válidos
        res_login = requests.post(url_login, headers=headers_apple, json=payload_login, timeout=15)
        
        # Guardamos las cabeceras de respuesta que contienen las nuevas cookies/tokens de Apple
        session_headers = headers_apple.copy()
        
        # Agregamos el token recibido a nuestras cabeceras para las siguientes descargas
        if "X-Apple-Session-Token" in res_login.headers:
            session_headers["X-Apple-Session-Token"] = res_login.headers["X-Apple-Session-Token"]
            print("[+] Token de sesión AuthKit obtenido con éxito.")
        else:
            print("[!] Alerta: Continuando con el flujo sin token de sesión explícito...")

    except Exception as e:
        print(f"[-] Error durante el login en los servidores de Apple: {e}")
        sys.exit(1)


    # 4. DESCARGA REAL DEL PERFIL (.mobileprovision)
    print('[+] Registrando dispositivo y descargando perfil desde Apple...')
    url_profile = "https://developerservices2.apple.com/services/QH65B2/ios/submitDevelopmentProfile.action"
    
    payload_profile = {
        "udid": config.get('udid'),
        "apple_id": config.get('apple_id')
    }
    
    res_profile = requests.post(url_profile, headers=session_headers, json=payload_profile, timeout=15)
    
    if res_profile.status_code == 200 and b"plist" in res_profile.content:
        with open("ios_distribution.mobileprovision", "wb") as f:
            f.write(res_profile.content)
        print('[+] Archivo ios_distribution.mobileprovision real guardado en disco.')
    else:
        print(f'[-] Error al procesar perfil. Respuesta de Apple: {res_profile.text}')


    # 5. DESCARGA REAL DEL CERTIFICADO (.p12)
    print('[+] Descargando certificado criptográfico final...')
    url_cert = "https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action"
    
    res_cert = requests.post(url_cert, headers=session_headers, json={"apple_id": config.get('apple_id')}, timeout=15)
    
    if res_cert.status_code == 200:
        with open("ios_development.p12", "wb") as f:
            f.write(res_cert.content)
        print('[+] Archivo ios_development.p12 real guardado en disco.')
    else:
        print(f'[-] Error al procesar certificado. Código: {res_cert.status_code}')

if __name__ == '__main__':
    iniciar_flujo_real()
