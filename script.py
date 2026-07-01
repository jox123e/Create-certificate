import sys
import requests
import json
import os
# Deshabilitar las advertencias visuales de SSL inseguro en la consola de GitHub
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def iniciar_flujo_real():
    print('[+] Solicitando firmas dinámicas al contenedor Anisette...')
    try:
        # Añadimos verify=False también aquí por si acaso
        res_anisette = requests.get('http://localhost:6969/', timeout=10, verify=False)
        anisette = res_anisette.json()
        print('[+] Datos Anisette obtenidos con éxito.')
    except Exception as e:
        print(f'[-] Error al conectar con Anisette local: {e}')
        sys.exit(1)

    if not os.path.exists('config.json'):
        print('[-] Error: Falta config.json en el repositorio.')
        sys.exit(1)

    with open('config.json', 'r') as f:
        config = json.load(f)

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
        # CORRECCIÓN CRÍTICA: verify=False ignora el error del certificado auto-firmado
        res_login = requests.post(url_login, headers=headers_apple, json=payload_login, timeout=15, verify=False)
        session_headers = headers_apple.copy()
        
        if "X-Apple-Session-Token" in res_login.headers:
            session_headers["X-Apple-Session-Token"] = res_login.headers["X-Apple-Session-Token"]
            print("[+] Token de sesión AuthKit obtenido con éxito.")
        else:
            print("[!] Alerta: Continuando flujo sin token explícito...")
    except Exception as e:
        print(f"[-] Error durante el login en los servidores de Apple: {e}")
        sys.exit(1)

    # Descarga del Perfil
    print('[+] Registrando dispositivo y descargando perfil desde Apple...')
    url_profile = "https://developerservices2.apple.com/services/QH65B2/ios/submitDevelopmentProfile.action"
    payload_profile = {"udid": config.get('udid'), "apple_id": config.get('apple_id')}
    
    res_profile = requests.post(url_profile, headers=session_headers, json=payload_profile, timeout=15, verify=False)
    if res_profile.status_code == 200:
        with open("ios_distribution.mobileprovision", "wb") as f:
            f.write(res_profile.content)
        print('[+] Archivo ios_distribution.mobileprovision real guardado.')
    else:
        print(f'[-] Error al procesar perfil: {res_profile.status_code}')

    # Descarga del Certificado
    print('[+] Descargando certificado criptográfico final...')
    url_cert = "https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action"
    
    res_cert = requests.post(url_cert, headers=session_headers, json={"apple_id": config.get('apple_id')}, timeout=15, verify=False)
    if res_cert.status_code == 200:
        with open("ios_development.p12", "wb") as f:
            f.write(res_cert.content)
        print('[+] Archivo ios_development.p12 real guardado.')
    else:
        print(f'[-] Error al procesar certificado: {res_cert.status_code}')

if __name__ == '__main__':
    iniciar_flujo_real()
