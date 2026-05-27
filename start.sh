#!/bin/bash
# 1Crypten Guardian — Start Script
# Inicializa o gateway do Telegram + Dashboard Kanban ADM

set -e

HERMES_HOME="${HERMES_HOME:-/opt/data}"
INSTALL_DIR="/opt/hermes"

# Ativar o venv
source "${INSTALL_DIR}/.venv/bin/activate"

echo "┌─────────────────────────────────────────────────────────┐"
echo "│           ⚕ Hermes Gateway Starting...                 │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│  Identidade: Agente Guardião 1Crypten                  │"
echo "└─────────────────────────────────────────────────────────┘"

# ────────────────────────────────────────────────────────
# Criar estrutura de diretórios do HERMES_HOME
# ────────────────────────────────────────────────────────
mkdir -p "$HERMES_HOME"/{cron,sessions,logs,hooks,memories,skills,skins,plans,workspace,home}

# ────────────────────────────────────────────────────────
# Bootstrap de configuração (só na primeira execução)
# ────────────────────────────────────────────────────────
if [ ! -f "$HERMES_HOME/.env" ] && [ -f "$INSTALL_DIR/.env.example" ]; then
    cp "$INSTALL_DIR/.env.example" "$HERMES_HOME/.env"
fi

if [ ! -f "$HERMES_HOME/config.yaml" ] && [ -f "$INSTALL_DIR/cli-config.yaml.example" ]; then
    cp "$INSTALL_DIR/cli-config.yaml.example" "$HERMES_HOME/config.yaml"
fi

# ────────────────────────────────────────────────────────
# IDENTIDADE DO GUARDIÃO — Forçar a cada restart
# ────────────────────────────────────────────────────────
echo "🛡️  Injetando identidade do Agente Guardião 1Crypten..."

# SOUL.md = Identidade principal do Hermes
if [ -f "$INSTALL_DIR/GUARDIAN_PROMPT.md" ]; then
    cp "$INSTALL_DIR/GUARDIAN_PROMPT.md" "$HERMES_HOME/SOUL.md"
    echo "✅ SOUL.md injetado a partir de GUARDIAN_PROMPT.md"
fi

# USER.md = Perfil do Jonatas + diretrizes operacionais
cat > "$HERMES_HOME/USER.md" << 'EOF'
# Perfil do Usuário (Jonatas)

## Nome e Comunicação
- O nome do usuário é **Jonatas** (Jhon Oliver).
- Você deve falar com ele estritamente em **Português do Brasil** (pt-br).
- Use um tom de voz cirúrgico, técnico, direto e de elite.

## Repositório e Sistema do 1Crypten
- O repositório oficial do sistema 1Crypten é: https://github.com/JonatasOliveira1983/1C-7.0/commits/main/
- Você atua como o **Agente Guardião do 1Crypten**, protegendo o capital institucional da OKX.
- O sistema opera 4 slots ativos (frota de 40 pares altcoins Elite mais eixos BTC e ETH).

## Doutrina e Diretrizes
- **Knife-Drop (O Facão):** monitorar ROI consolidado. Ativa em 70% de ROI. Fechamento concorrente imediato em drawdown de 15% a partir do pico alcançado.
- **Blitz:** emancipação de Moonbags em 150% de ROI.
- Use o comando `/banca` para auditar a banca e os slots operacionais lidos em tempo real do banco de dados PostgreSQL.
EOF
echo "✅ USER.md do Jonatas injetado com sucesso"

# ────────────────────────────────────────────────────────
# Sync de skills (se disponível)
# ────────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/skills" ] && [ -f "$INSTALL_DIR/tools/skills_sync.py" ]; then
    python3 "$INSTALL_DIR/tools/skills_sync.py" 2>/dev/null || true
fi

# ────────────────────────────────────────────────────────
# Iniciar o Gateway do Telegram (em background)
# ────────────────────────────────────────────────────────
export HERMES_GUARDIAN=1
export HERMES_ALLOW_ROOT_GATEWAY=1
echo "📡 Iniciando o 1Crypten Guardian Agent (Telegram Gateway)..."
hermes gateway &
GATEWAY_PID=$!
echo "✅ Gateway iniciado (PID: $GATEWAY_PID)"

# ────────────────────────────────────────────────────────
# Iniciar o Dashboard Kanban ADM (processo principal)
# ────────────────────────────────────────────────────────
echo "📊 Iniciando o Dashboard (Kanban ADM) na porta ${PORT:-8080}..."
exec hermes dashboard --host 0.0.0.0 --port "${PORT:-8080}" --insecure
