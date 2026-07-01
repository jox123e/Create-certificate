local fs = require("fs")
local http = require("http")

local function ejecutarFirma()
    local config = json.decode(fs.read("config.json"))
    local claveP12 = config.p12_password or "123456"

    print("[+] Inicializando empaquetado desde entorno Lua...")
    print("[+] Clave elegida por el usuario: " .. claveP12)

    -- Guardar logs del estado del proceso
    fs.write("registro_firma.txt", "wb", "UDID: " .. config.udid .. "\nClave P12: " .. claveP12)
    print("[+] Archivos de registro actualizados con éxito.")
end
