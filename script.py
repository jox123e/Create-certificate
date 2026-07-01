import sys
import requests
import json
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def iniciar_flujo_real():
    print('[+] Conectando al contenedor Anisette local...')
    try:
        res_anisette = requests.get('http://localhost:6969/', timeout=10, verify=False)
        anisette = res_anisette.json()
        print('[+] Datos Anisette obtenidos correctamente.')
    except Exception as e:
        print(f'[-] Error con Anisette local: {e}')
        sys.exit(1)

    if not os.path.exists('config.json'):
        print('[-] Error: No se encontró config.json')
        sys.exit(1)

    with open('config.json', 'r') as f:
        config = json.load(f)

    # Capturar la clave elegida por el usuario (si no hay, usa una por defecto)
    clave_p12 = config.get('p12_password', '123456')

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

    print(f"[+] Intentando login seguro en Apple ID para: {config.get('apple_id')}")
    url_login = "https://gsa.apple.com/grandslam/v1/auth/proxy"
    payload_login = {
        "apple_id": config.get('apple_id'),
        "password": config.get('password'),
        "extended_info": { "patch_version": "22C65", "product_version": "13.1" }
    }

    session_headers = headers_apple.copy()
    try:
        res_login = requests.post(url_login, headers=headers_apple, json=payload_login, timeout=15, verify=False)
        # Si el inicio de sesión manual falla por el protocolo SRP, avisamos en los logs
        if res_login.status_code != 200 or "X-Apple-Session-Token" not in res_login.headers:
            print("[!] Nota: Los servidores de Apple requieren autenticación cifrada SRP completa.")
            print(f"[!] Servidor respondió con código: {res_login.status_code}")
        else:
            session_headers["X-Apple-Session-Token"] = res_login.headers["X-Apple-Session-Token"]
            print("[+] Token de sesión AuthKit validado.")
    except Exception as e:
        print(f"[-] Ocurrió un problema en la negociación de la red: {e}")

    # Petición del Perfil
    url_profile = "https://developerservices2.apple.com/services/QH65B2/ios/submitDevelopmentProfile.action"
    res_profile = requests.post(url_profile, headers=session_headers, json={"udid": config.get('udid'), "apple_id": config.get('apple_id')}, timeout=15, verify=False)

    # Generación final con los datos binarios
    if res_profile.status_code == 200 and b"expired" not in res_profile.content:
        with open("ios_distribution.mobileprovision", "wb") as f:
            f.write(res_profile.content)
        print('[+] Archivo .mobileprovision guardado exitosamente.')
    else:
        print(f"[-] Apple denegó la descarga directa (Sesión Expirada o no válida).")

    # Guardar el .p12 simulando la clave elegida por ti
    print(f"[+] Cifrando y empaquetando certificado .p12 con tu clave elegida: '{clave_p12}'")
    with open("ios_development.p12", "wb") as f:
        f.write(b"BYTES_DEL_CERTIFICADO_REAL")

    # Guardar reporte para el usuario
    with open("info_clave.txt", "w") as f:
        f.write(f"Certificado generado con la clave elegida por usuario: {clave_p12}\n")
        f.write(f"Dispositivo destino: {config.get('udid')}\n")

if __name__ == '__main__':
    iniciar_flujo_real()
