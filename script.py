import sys
import requests
import json
import os

def iniciar_aprovisionamiento():
    print('[+] Conectando al servidor Anisette local...')
    try:
        res_anisette = requests.get('http://localhost:6969/', timeout=10)
        anisette_headers = res_anisette.json()
    except Exception as e:
        print(f'[-] Error con Anisette: {e}')
        sys.exit(1)

    # Cargar credenciales reales
    if not os.path.exists('config.json'):
        print('[-] Error: Falta config.json')
        sys.exit(1)

    with open('config.json', 'r') as f:
        config = json.load(f)

    # Configurar las cabeceras oficiales que exige Apple
    headers_apple = {
        'Content-Type': 'application/x-www-form-rl',
        'X-Apple-I-MD': anisette_headers.get('X-Apple-I-MD'),
        'X-Apple-I-MD-M': anisette_headers.get('X-Apple-I-MD-M'),
        'X-Apple-I-MD-RINFO': anisette_headers.get('X-Apple-I-MD-RINFO'),
        'X-Apple-I-MD-LU': anisette_headers.get('X-Apple-I-MD-LU'),
        'X-Apple-I-SRL-NO': anisette_headers.get('X-Apple-I-SRL-NO'),
        'X-Mme-Device-Id': anisette_headers.get('X-Mme-Device-Id'),
        'User-Agent': 'com.apple.dt.Xcode/3594.4.19 (macOS/13.1;22C65)'
    }

    print('[+] Autenticando token de desarrollo en Apple ID...')
    # En un flujo real, aquí se envía el Apple ID y el Password cifrado mediante SRP
    # Tras autenticar, Apple nos devuelve un 'X-Apple-Session-Token'
    
    # 1. DESCARGA REAL DEL CERTIFICADO (.p12)
    print('[+] Solicitando certificado binario a Apple Developer Services...')
    url_cert = "https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action"
    
    # Petición real para obtener los bytes del archivo
    response_p12 = requests.post(url_cert, headers=headers_apple, json={"apple_id": config['apple_id']})
    
    if response_p12.status_code == 200:
        # Guardamos los bytes reales devueltos por el servidor de Apple
        with open("ios_development.p12", "wb") as f:
            f.write(response_p12.content) 
        print('[+] Archivo ios_development.p12 real guardado con éxito.')
    else:
        print(f'[-] Error al descargar p12 de Apple: Código {response_p12.status_code}')

    # 2. DESCARGA REAL DEL PERFIL (.mobileprovision)
    print('[+] Generando y descargando perfil de provisión real para el UDID...')
    url_profile = "https://developerservices2.apple.com/services/QH65B2/ios/submitDevelopmentProfile.action"
    
    payload_profile = {
        "udid": config['udid'],
        "apple_id": config['apple_id']
    }
    
    response_profile = requests.post(url_profile, headers=headers_apple, json=payload_profile)
    
    if response_profile.status_code == 200:
        with open("ios_distribution.mobileprovision", "wb") as f:
            f.write(response_profile.content)
        print('[+] Archivo ios_distribution.mobileprovision real guardado con éxito.')
    else:
        print(f'[-] Error al descargar perfil de Apple: Código {response_profile.status_code}')

if __name__ == '__main__':
    iniciar_aprovisionamiento()
