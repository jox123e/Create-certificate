local AdministradorCertificados = {}

-- Tabla base de datos para registrar los iPhones o iPads
local baseDatosDispositivos = {}

-- Función para registrar un nuevo iPhone en la lista
function AdministradorCertificados.registrarDispositivo(udid, correoApple)
    baseDatosDispositivos[udid] = {
        appleID = correoApple,
        estado = "Pendiente",
        archivos = {
            p12 = false,
            mobileprovision = false
        }
    }
    print("[Lua] Dispositivo registrado con éxito. UDID: " .. udid)
end

-- Función que marcas como ejecutada cuando GitHub Actions termine de generar los archivos
function AdministradorCertificados.marcarComoCompletado(udid)
    if baseDatosDispositivos[udid] then
        baseDatosDispositivos[udid].estado = "Certificado Listo"
        baseDatosDispositivos[udid].archivos.p12 = true
        baseDatosDispositivos[udid].archivos.mobileprovision = true
        print("[Lua] ¡Felicidades! Los archivos de firma ya están listos para el UDID: " .. udid)
    else
        print("[Lua] Error: El dispositivo no está registrado.")
    end
end

-- Función para revisar cómo va el proceso de un iPhone
function AdministradorCertificados.obtenerEstado(udid)
    if baseDatosDispositivos[udid] then
        return baseDatosDispositivos[udid].estado
    end
    return "No encontrado"
end

return AdministradorCertificados
