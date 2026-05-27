import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def test_banca():
    print("=== TESTE DE CONEXAO E LEITURA DA BANCA (1CRYPTEN) ===")
    print(f"Python Version: {sys.version}")
    
    # URL de producao do PostgreSQL (Railway)
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "sua_url" in db_url or "<" in db_url:
        db_url = "postgresql+asyncpg://postgres:JSLsEfBVPywKuYJSAypuNPVvIgYwGXzz@centerbeam.proxy.rlwy.net:54059/railway"
    
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
    print(f"Conectando a: {db_url.split('@')[-1]} (ocultando credenciais)")
    
    try:
        engine = create_async_engine(db_url, echo=False)
        async with engine.connect() as conn:
            print("OK: Conexao estabelecida com sucesso!")
            
            # 1. Obter Banca
            print("Lendo banca_status...")
            banca_result = await conn.execute(text("SELECT saldo_total, slots_disponiveis, status FROM banca_status WHERE id = 1"))
            banca_row = banca_result.fetchone()
            
            if banca_row:
                saldo, disponiveis, status = banca_row
                print(f"Banca: Saldo Total = ${saldo:,.2f}")
                print(f"Banca: Slots Disponiveis = {disponiveis} / 4")
                print(f"Banca: Status Geral = {status}")
            else:
                print("Aviso: Registro de banca_status nao encontrado (id=1).")
                
            # 2. Obter Slots
            print("\nLendo slots operacionais...")
            slots_result = await conn.execute(text("SELECT id, symbol, side, qty, entry_price, status_risco, slot_type, order_id FROM slots ORDER BY id"))
            slots_rows = slots_result.fetchall()
            
            print(f"Total de slots retornados: {len(slots_rows)}")
            for s in slots_rows:
                slot_id, symbol, side, qty, entry_price, status_risco, slot_type, order_id = s
                is_active = symbol and str(symbol).strip().upper() not in ["LIVRE", "NONE", "NULL", ""]
                status_slot = "ATIVO" if is_active else "LIVRE"
                print(f"Slot {slot_id}: {status_slot} | Symbol: {symbol} | Side: {side} | Qty: {qty} | Price: {entry_price} | Risco: {status_risco} | Type: {slot_type} | OrderID: {order_id}")
                
        print("\nSUCESSO: Teste concluido com sucesso total!")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"\nERRO DETECTADO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Configura saida padrao segura contra erros de encode no console do Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    success = asyncio.run(test_banca())
    sys.exit(0 if success else 1)
