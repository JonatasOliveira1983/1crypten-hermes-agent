# ===========================
# 1CRYPTEN GUARDIAN — Dockerfile
# Gateway-only build (sem Node.js/Playwright desnecessários)
# ===========================

FROM ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie@sha256:b3c543b6c4f23a5f2df22866bd7857e5d304b67a564f4feab6ac22044dde719b AS uv_source
FROM tianon/gosu:1.19-trixie@sha256:3b176695959c71e123eb390d427efc665eeb561b1540e82679c15e992006b8b9 AS gosu_source
FROM debian:trixie-slim

# Sem buffer Python para logs imediatos
ENV PYTHONUNBUFFERED=1
ENV HERMES_WEB_DIST=/opt/hermes/hermes_cli/web_dist
ENV HERMES_HOME=/opt/data
ENV PATH="/opt/data/.local/bin:${PATH}"

# Dependências do sistema — apenas o necessário para o gateway
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc python3-dev libffi-dev \
        curl procps git tini gosu && \
    rm -rf /var/lib/apt/lists/*

# Usuário não-root
RUN useradd -u 10000 -m -d /opt/data hermes

# Copiar binários auxiliares
COPY --chmod=0755 --from=gosu_source /gosu /usr/local/bin/
COPY --chmod=0755 --from=uv_source /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /opt/hermes

# ---------- Instalar dependências Python (camada cacheada) ----------
COPY pyproject.toml uv.lock ./
RUN touch ./README.md
RUN uv sync --frozen --no-install-project --extra messaging

# ---------- Código-fonte ----------
COPY --chown=hermes:hermes . .

# ---------- Permissões ----------
USER root
RUN chmod -R a+rX /opt/hermes && \
    chown -R hermes:hermes /opt/hermes/.venv

# ---------- Instalar o hermes-agent em modo editável ----------
RUN uv pip install --no-cache-dir --no-deps -e "."

# ---------- Diretório de dados ----------
RUN mkdir -p /opt/data

ENTRYPOINT [ "/usr/bin/tini", "-g", "--", "/opt/hermes/docker/entrypoint.sh" ]
CMD [ "gateway" ]
