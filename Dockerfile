# ============================================================
# 1CRYPTEN GUARDIAN — Dockerfile (Build Definitivo)
# Usa pip puro — sem uv sync --frozen, sem Node.js, sem Playwright
# ============================================================

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HERMES_HOME=/opt/data
ENV HERMES_WEB_DIST=/opt/hermes/hermes_cli/web_dist
ENV PATH="/opt/data/.local/bin:${PATH}"

# Dependências de sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc python3-dev libffi-dev \
        libpq-dev curl procps git ripgrep tini gosu && \
    rm -rf /var/lib/apt/lists/*

# Usuário não-root
RUN useradd -u 10000 -m -d /opt/data hermes

WORKDIR /opt/hermes

# ---------- Dependências Python (camada cacheada) ----------
# Copiar apenas o pyproject.toml primeiro para cache eficiente
COPY pyproject.toml ./
RUN touch ./README.md

# Instalar dependências core + messaging via pip (sem uv.lock)
RUN pip install --no-cache-dir \
    openai==2.24.0 \
    python-dotenv==1.2.2 \
    fire==0.7.1 \
    "httpx[socks]==0.28.1" \
    rich==14.3.3 \
    tenacity==9.1.4 \
    pyyaml==6.0.3 \
    "ruamel.yaml==0.18.17" \
    requests==2.33.0 \
    "jinja2==3.1.6" \
    pydantic==2.13.4 \
    "prompt_toolkit==3.0.52" \
    croniter==6.0.0 \
    "PyJWT[crypto]==2.12.1" \
    psutil==7.2.2 \
    sqlalchemy==2.0.28 \
    asyncpg==0.31.0 \
    "python-telegram-bot[webhooks]==22.6" \
    "aiohttp==3.13.3" \
    tzdata

# ---------- Código-fonte ----------
COPY --chown=hermes:hermes . .

# ---------- Instalar o hermes-agent em modo editável ----------
RUN pip install --no-cache-dir --no-deps -e .

# ---------- Permissões ----------
RUN chmod -R a+rX /opt/hermes && \
    chown -R hermes:hermes /opt/hermes

# ---------- Diretório de dados ----------
RUN mkdir -p /opt/data && chown hermes:hermes /opt/data

ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/opt/hermes/docker/entrypoint.sh"]
CMD ["gateway"]
