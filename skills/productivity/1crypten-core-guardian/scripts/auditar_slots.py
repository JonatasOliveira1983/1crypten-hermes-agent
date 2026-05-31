# -*- coding: utf-8 -*-
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env local ou de sistema
load_dotenv()

async def audit_slots():
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
        # Busca slots no banco Postgres
        slots_rows = await conn.fetch("SELECT id, symbol, side, qty, entry_price, entry_margin, current_stop, target_price, leverage, status_risco, pnl_percent, pensamento, score, unified_confidence FROM slots ORDER BY id")
        
        print("⚡ **AUDITORIA DOS SLOTS OPERACIONAIS 1CRYPTEN**")
        print("==================================================")

        ativas = 0
        for row in slots_rows:
            slot_id = row["id"]
            symbol = row["symbol"]
            status = row["status_risco"] or "LIVRE"
            
            if symbol and status != "LIVRE":
                ativas += 1
                side = row["side"] or "LONG"
                qty = row["qty"] or 0.0
                entry = row["entry_price"] or 0.0
                margin = row["entry_margin"] or 0.0
                stop = row["current_stop"] or 0.0
                target = row["target_price"] or 0.0
                leverage = row["leverage"] or 50.0
                pnl = row["pnl_percent"] or 0.0
                score = row["score"] or 0.0
                confidence = row["unified_confidence"] or 50.0
                pensamento = row["pensamento"] or "Nenhum pensamento registrado."
                
                emoji = "🟢" if pnl >= 0 else "🔴"
                
                print(f"🔹 **SLOT {slot_id} | {symbol} - {side.upper()} {leverage:.0f}x**")
                print(f"  - **Status:** `ATIVO` | **PnL:** {emoji} `{pnl:.2f}%` (Margem: ${margin:.2f})")
                print(f"  - **Entrada:** ${entry:.6f} | **Target:** ${target:.6f}")
                print(f"  - **Stop Loss:** ${stop:.6f} | **Quantidade:** {qty:.4f}")
                print(f"  - **Pontuação (Score):** {score:.1f} | **Confiança:** {confidence:.1f}%")
                print(f"  - 💭 **Pensamento IA:** *\"{pensamento}\"*")
                print("")
            else:
                print(f"🔹 **SLOT {slot_id} | LIVRE**")
                print("  - *Aguardando sinal qualificado do radar da frota.*")
                print("")

        print("==================================================")
        print(f"🛸 **Resumo:** {ativas} de 4 slots em batalha ativa.")

    except Exception as e:
        print(f"❌ Erro ao executar auditoria de slots: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(audit_slots())
