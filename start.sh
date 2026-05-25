#!/bin/bash

echo "Iniciando o 1Crypten Guardian Agent (Telegram Gateway)..."
# Inicia o bot no Telegram em background (usando a Doutrina Knife-Drop/Elite)
hermes gateway start telegram &

echo "Iniciando o Dashboard (Kanban ADM)..."
# Inicia a interface WEB do Hermes na porta exposta pelo Railway
# Para proteção adicional de acesso, recomenda-se usar Cloudflare Access ou Basic Auth via Railway Proxy
exec hermes dashboard --host 0.0.0.0 --port $PORT
