#!/bin/bash

# CONFIGURACIÓN
MIRTH_HOST="https://192.168.1.98:8443"
USERNAME="admin"
PASSWORD="admin"
CANAL_XML="hl7_listener_channel.xml"
LOG_FILE="mirth_upload.log"

# Función para registrar mensajes
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Iniciar proceso
log "Iniciando carga de canal a NextGen Connect 4.5.2"

# Validar XML primero
if ! xmllint --noout "$CANAL_XML"; then
  log "❌ Error: El archivo XML del canal no es válido"
  exit 1
fi

# LOGIN y guardar cookies
log "[1] Haciendo login en NextGen Connect..."
LOGIN_RESPONSE=$(curl -v -k -c cookies.txt -X POST "$MIRTH_HOST/api/users/_login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Requested-With: OpenAPI" \
  -d "username=$USERNAME&password=$PASSWORD" 2>&1)

echo "$LOGIN_RESPONSE" >> "$LOG_FILE"

# Verificar login
if ! grep -q "JSESSIONID" cookies.txt; then
  log "❌ Error: No se pudo obtener la cookie de sesión. Verifica:"
  log "   - Credenciales correctas"
  log "   - Conexión al servidor"
  log "   - Certificados SSL (prueba con -k para ignorar SSL)"
  exit 1
fi

log "[2] Autenticación exitosa. Cookie obtenida."

# SUBIR CANAL
log "[3] Subiendo canal desde $CANAL_XML..."
RESPONSE=$(curl -v -k -b cookies.txt -X POST "$MIRTH_HOST/api/channels" \
  -H "Content-Type: application/xml" \
  -H "X-Requested-With: OpenAPI" \
  --data-binary @"$CANAL_XML" 2>&1)

echo "$RESPONSE" >> "$LOG_FILE"

# Verificar respuesta
if echo "$RESPONSE" | grep -q "HTTP ERROR"; then
  log "❌ Error del servidor al subir el canal:"
  log "$RESPONSE"
  log "Consulta los logs de NextGen Connect para más detalles."
  exit 1
fi

# Extraer ID del canal
CHANNEL_ID=$(echo "$RESPONSE" | grep -oPm1 '(?<=<id>)[^<]+')
if [ -z "$CHANNEL_ID" ]; then
  log "❌ No se pudo extraer el ID del canal. Respuesta del servidor:"
  log "$RESPONSE"
  exit 1
fi

log "[4] Canal creado con ID: $CHANNEL_ID"

# HABILITAR E INICIAR CANAL (opcional, ya que el XML tiene initialState=STARTED)
log "[5] Verificando estado del canal..."
curl -v -k -b cookies.txt -X POST "$MIRTH_HOST/api/channels/$CHANNEL_ID/_enable" \
  -H "X-Requested-With: OpenAPI" >> "$LOG_FILE" 2>&1
curl -v -k -b cookies.txt -X POST "$MIRTH_HOST/api/channels/$CHANNEL_ID/_start" \
  -H "X-Requested-With: OpenAPI" >> "$LOG_FILE" 2>&1

log "✅ Proceso completado. Canal $CHANNEL_ID configurado correctamente."