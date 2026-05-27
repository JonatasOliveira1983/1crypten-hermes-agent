# ============================================================
# 1CRYPTEN GUARDIAN — Dockerfile
# Baseado no start.sh original do projeto
# ============================================================

FROM ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie@sha256:b3c543b6c4f23a5f2df22866bd7857e5d304b67a564f4feab6ac22044dde719b AS uv_source

FROM debian:trixie-slim

ENV PYTHONUNBUFFERED=1
ENV HERMES_HOME=/opt/data
ENV HERMES_WEB_DIST=/opt/hermes/hermes_cli/web_dist
ENV PATH="/opt/hermes/.venv/bin:/opt/data/.local/bin:${PATH}"

# Copiar uv
COPY --chmod=0755 --from=uv_source /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

# Instalar dependências mínimas do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc python3-dev libffi-dev libpq-dev \
        curl git procps tini && \
    rm -rf /var/lib/apt/lists/*

# Criar usuário
RUN useradd -u 10000 -m -d /opt/data hermes

WORKDIR /opt/hermes

# Instalar dependências Python com uv (SEM --frozen, resolve na hora)
COPY pyproject.toml ./
RUN touch ./README.md && \
    uv venv /opt/hermes/.venv --python 3.13 && \
    uv pip install --python /opt/hermes/.venv/bin/python \
        openai==2.24.0 python-dotenv==1.2.2 fire==0.7.1 \
        "httpx[socks]==0.28.1" rich==14.3.3 tenacity==9.1.4 \
        pyyaml==6.0.3 "ruamel.yaml==0.18.17" requests==2.33.0 \
        "jinja2==3.1.6" pydantic==2.13.4 "prompt_toolkit==3.0.52" \
        croniter==6.0.0 "PyJWT[crypto]==2.12.1" psutil==7.2.2 \
        sqlalchemy==2.0.36 asyncpg==0.31.0 greenlet==3.1.1 tzdata \
        "python-telegram-bot==22.6" "aiohttp==3.13.3" \
        "fastapi==0.133.1" "uvicorn[standard]==0.41.0"

# Copiar código-fonte
COPY --chown=hermes:hermes . .

# Instalar o hermes-agent em modo editável
RUN uv pip install --python /opt/hermes/.venv/bin/python --no-deps -e .

# Permissões
RUN chown -R hermes:hermes /opt/hermes/.venv /opt/data

EXPOSE 8080

ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/opt/hermes/start.sh"]
