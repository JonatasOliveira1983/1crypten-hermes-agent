# -*- coding: utf-8 -*-
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env local ou de sistema
load_dotenv()

async def audit_banca():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Erro: Variável de ambiente DATABASE_URL não está configurada.")
        return

    # Ajusta o esquema para o asyncpg (exige postgresql://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        conn = await asyncpg.connect(db_url)
    except Exception as e:
        print(f"❌ Falha ao conectar ao banco de dados PostgreSQL: {e}")
        return

    try:
        # 1. Busca status da banca
        banca_row = await conn.fetchrow("SELECT saldo_total, risco_real_percent, slots_disponiveis, status FROM banca_status WHERE id = 1")
        
        # 2. Busca totais históricos do trade_history
        trade_stats = await conn.fetchrow("SELECT COUNT(*) as qtd, SUM(pnl) as total_pnl FROM trade_history")
        
        # 3. Busca Moonbags
        moon_stats = await conn.fetchrow("SELECT COUNT(*) as qtd FROM moonbags")

        # Fallbacks
        saldo = banca_row["saldo_total"] if banca_row else 100.0
        risco = banca_row["risco_real_percent"] if banca_row else 0.0
        slots_disp = banca_row["slots_disponiveis"] if banca_row else 4
        status = banca_row["status"] if banca_row else "UNKNOWN"
        
        qtd_trades = trade_stats["qtd"] if trade_stats else 0
        total_pnl = trade_stats["total_pnl"] if trade_stats and trade_stats["total_pnl"] is not None else 0.0
        qtd_moons = moon_stats["qtd"] if moon_stats else 0

        # Formatação de saída elegante em Markdown
        print("🏦 **EXTRATO DE CUSTÓDIA DO AGENTE GUARDIÃO (HERMES)**")
        print(f"==================================================")
        print(f"💰 **Saldo Líquido da Banca:** ${saldo:.2f}")
        print(f"📊 **Resultado Consolidado Histórico:** ${total_pnl:.2f} (em {qtd_trades} trades)")
        print(f"🛡️ **Risco Real Alocado:** {risco:.2f}%")
        print(f"⚡ **Status de Operação:** `{status}`")
        print(f"🚀 **Moonbags Ativas (Emancipadas):** {qtd_moons}")
        print(f"🎯 **Slots Disponíveis no Cockpit:** {slots_disp} de 4")
        print(f"==================================================")
        print(f"ℹ️ *Dados lidos em tempo real da Fonte Única de Verdade (SSOT) no Postgres.*")

    except Exception as e:
        print(f"❌ Erro ao executar consultas de auditoria: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(audit_banca())
