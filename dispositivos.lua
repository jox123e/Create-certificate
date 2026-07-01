local http = require("http")
local fs = require("fs")

local function solicitarCertificados()
    print("[+] Obteniendo firmas criptográficas...")
    local anisetteData = http.request("http://localhost:6969/").json()
    local config = json.decode(fs.read("config.json"))

    local headers = {
        ["X-Apple-I-MD"] = anisetteData["X-Apple-I-MD"],
        ["X-Mme-Device-Id"] = anisetteData["X-MMe-Device-Id"]
    }

    print("[+] Descargando desde Apple Portal (Omitiendo Verificación SSL)...")
    local response = http.request({
        url = "https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action",
        method = "POST",
        headers = headers,
        ssl_verify = false, -- Fuerza al motor HTTP de Lua a ignorar el error del certificado chain
        body = { apple_id = config.apple_id }
    })

    if response.status_code == 200 then
        fs.write("ios_development.p12", "wb", response.body)
        print("[+] Fichero .p12 guardado en el entorno local.")
    end
end
