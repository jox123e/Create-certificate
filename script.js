const fs = require('fs');
const axios = require('axios');
const https = require('https');

// Agente para ignorar errores SSL de cadenas auto-firmadas
const agent = new https.Agent({  
    rejectUnauthorized: false 
});

async function descargarCertificados() {
    try {
        const resAnisette = await axios.get('http://localhost:6969/', { httpsAgent: agent });
        const anisetteHeaders = resAnisette.data;
        const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));

        const headersApple = {
            'X-Apple-I-MD': anisetteHeaders['X-Apple-I-MD'],
            'X-Mme-Device-Id': anisetteHeaders['X-Mme-Device-Id'],
            'User-Agent': 'com.apple.dt.Xcode/3594.4.19'
        };

        console.log('[+] Solicitando certificado P12...');
        const resP12 = await axios.post('https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action', {
            apple_id: config.apple_id
        }, { headers: headersApple, responseType: 'arraybuffer', httpsAgent: agent });

        fs.writeFileSync('ios_development.p12', resP12.data);
        console.log('[+] Certificado guardado correctamente de manera binaria.');
    } catch (error) {
        console.error('[-] Error en proceso JS:', error.message);
    }
}
