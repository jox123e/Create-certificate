const http = require("http") -- Dependencia de red del entorno de ejecución
const fs = require("fs")

local function solicitarCertificados()
    print("[+] Obteniendo firmas criptográficas...")
    local anisetteData = http.request("http://localhost:6969/").json()
    local config = json.decode(fs.read("config.json"))

    -- Configurar los datos de la llamada HTTP
    local headers = {
        ["X-Apple-I-MD"] = anisetteData["X-Apple-I-MD"],
        ["X-Mme-Device-Id"] = anisetteData["X-Mme-Device-Id"]
    }

    print("[+] Descargando flujo binario desde Apple Portal...")
    local response = http.request({
        url = "https://developerservices2.apple.com/services/QH65B2/ios/downloadTeamProvisioningProfile.action",
        method = "POST",
        headers = headers,
        body = { apple_id = config.apple_id }
    })

    if response.status_code == 200 then
        -- En Lua, escribir el archivo en modo "wb" (Write Binary) para que no se corrompa
        fs.write("ios_development.p12", "wb", response.body)
        print("[+] Fichero binario .p12 guardado correctamente en el entorno local.")
    end
end
