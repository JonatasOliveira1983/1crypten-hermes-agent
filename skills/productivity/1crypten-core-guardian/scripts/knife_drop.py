# -*- coding: utf-8 -*-
import os
import sys
import argparse
import asyncio
import asyncpg
import json
import time
import httpx
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Carrega variáveis do ambiente (.env do Hermes)
load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="Aciona o Knife-Drop manual sobre um símbolo ativo nos slots.")
    parser.add_argument("--symbol", type=str, required=True, help="Símbolo a ser cortado (ex: SOLUSDT ou SOLUSDT.P)")
    return parser.parse_args()

async def trigger_knife_drop(symbol_raw):
    # Padroniza símbolo (SOLUSDT)
    symbol = symbol_raw.upper().replace(".P", "").replace("-", "")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Erro: Variável de ambiente DATABASE_URL não encontrada.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        conn = await asyncpg.connect(db_url)
    except Exception as e:
        print(f"❌ Falha ao conectar ao banco Postgres: {e}")
        return

    try:
        # 1. Localiza se existe o símbolo nos slots ativos do Postgres
        slots_rows = await conn.fetch("SELECT id, symbol, qty, entry_price, entry_margin FROM slots")
        
        matched_slot = None
        for row in slots_rows:
            row_sym = (row["symbol"] or "").upper().replace(".P", "").replace("-", "")
            if row_sym == symbol:
                matched_slot = row
                break

        if not matched_slot:
            print(f"ℹ️ O par {symbol} não está em batalha ativa nos slots Snipers.")
            await conn.close()
            return

        slot_id = matched_slot["id"]
        qty = matched_slot["qty"] or 0.0
        entry_price = matched_slot["entry_price"] or 0.0
        entry_margin = matched_slot["entry_margin"] or 0.0

        print(f"🔪 [CORTAR] Encontrado {symbol} no Slot {slot_id}!")
        print(f"  - Quantidade: {qty:.4f} | Margem: ${entry_margin:.2f}")

        # 2. Resetar o Slot no Postgres (Fonte de Verdade) para liberar para novos sinais
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        await conn.execute("""
            UPDATE slots 
            SET symbol = NULL, side = NULL, qty = 0.0, entry_price = 0.0, entry_margin = 0.0, 
                current_stop = 0.0, initial_stop = 0.0, target_price = 0.0, liq_price = 0.0, 
                pnl_percent = 0.0, status_risco = 'LIVRE', order_id = NULL, genesis_id = NULL, 
                pensamento = $1, score = 0, opened_at = NULL, updated_at = NOW()
            WHERE id = $2
        """, f"🔪 CORTADO MANUALMENTE PELO GUARDIÃO (HERMES) em {now}", slot_id)

        print(f"✅ [POSTGRES] Slot {slot_id} resetado e liberado com sucesso!")

        # 3. Dispara alerta de Pânico Global / Sinalizador via MQTT (para o robô Sniper principal fechar a ordem fisicamente)
        mqtt_broker = os.getenv("MQTT_BROKER_URL", "broker.hivemq.com")
        mqtt_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        mqtt_user = os.getenv("MQTT_USERNAME")
        mqtt_pw = os.getenv("MQTT_PASSWORD")
        topic_prefix = os.getenv("MQTT_TOPIC_PREFIX", "1crypten/sniper")

        try:
            client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
            if mqtt_user and mqtt_pw:
                client.username_pw_set(mqtt_user, mqtt_pw)
            
            client.connect(mqtt_broker, mqtt_port, 60)
            
            # Monta payload de pânico para o par
            payload = {
                "version": "5.5.0",
                "type": "PANIC_CLOSE_ALL",
                "timestamp": time.time(),
                "positions_to_close": [{"instId": f"{symbol}.P"}]
            }
            
            client.publish(f"{topic_prefix}/panic", json.dumps(payload), qos=2)
            client.disconnect()
            print(f"📡 [MQTT] Sinal de corte emergencial enviado para o Sniper no canal '{topic_prefix}/panic'.")
        except Exception as mqtt_err:
            print(f"⚠️ [MQTT] Falha ao disparar sinalizador MQTT: {mqtt_err}")

        # 4. Dispara alerta de Pânico no Telegram Bot do Guardião
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
        if telegram_token and telegram_chat:
            try:
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                text = (
                    f"🔪 <b>CORTAR POSIÇÃO — GUARDIÃO (HERMES) INTERVEIO</b>\n\n"
                    f"⚠️ <b>Ação Manual acionada via Neural Chat</b>\n"
                    f"🔹 <b>Slot:</b> {slot_id} liberado\n"
                    f"🔹 <b>Símbolo:</b> {symbol}\n"
                    f"🔹 <b>Exposição Removida:</b> {qty:.4f} (~${entry_margin:.2f})\n\n"
                    f"📢 <i>O robô principal Sniper 1Crypten foi sinalizado via MQTT para liquidar a posição fisicamente no mercado OKX concorrentemente.</i>"
                )
                async with httpx.AsyncClient() as client:
                    await client.post(url, json={"chat_id": telegram_chat, "text": text, "parse_mode": "HTML"}, timeout=10.0)
                print("🚨 [TELEGRAM] Notificação de pânico manual enviada com sucesso!")
            except Exception as tg_err:
                print(f"⚠️ [TELEGRAM] Falha ao enviar alerta de pânico: {tg_err}")

    except Exception as e:
        print(f"❌ Erro crítico no processo de Knife-Drop: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(trigger_knife_drop(args.symbol))
