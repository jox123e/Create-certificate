const fs = require('fs');
const axios = require('axios');

async function descargarCertificados() {
    try {
        // 1. Obtener firmas del hardware desde el contenedor Docker
        const resAnisette = await axios.get('http://localhost:6969/');
        const anisetteHeaders = resAnisette.data;
        const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));

        const headersApple = {
            'X-Apple-I-MD': anisetteHeaders['X-Apple-I-MD'],
            'X-Apple-I-MD-M': anisetteHeaders['X-Apple-I-MD-M'],
            'X-Mme-Device-Id': anisetteHeaders['X-Mme-Device-Id'],
            'User-Agent': 'com.apple.dt.Xcode/3594.4.19'
        };

        print('[+] Descargando binario P12 real...');
        // Especificamos 'arraybuffer' para recibir datos binarios puros, no texto
        const resP12 = await axios.post('https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action', {
            apple_id: config.apple_id
        }, { headers: headersApple, responseType: 'arraybuffer' });

        fs.writeFileSync('ios_development.p12', resP12.data);
        console.log('[+] Certificado .p12 binario guardado de forma real.');

    } catch (error) {
        console.error('[-] Error en el proceso de red:', error.message);
    }
}
