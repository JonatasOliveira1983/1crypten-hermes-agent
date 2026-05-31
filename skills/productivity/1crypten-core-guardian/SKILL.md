---
name: 1crypten-core-guardian
description: "Use when you need to audit, secure, or monitor the 1Crypten Sniper trading database (PostgreSQL) including bankroll, active slots, moonbags, or to manual-trigger a protective Knife-Drop."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [1crypten, trading, guardian, bankroll, slots, database, audit]
    related_skills: [writing-plans, systematic-debugging]
---

# 1Crypten Core Guardian Skill (Portfolio Guard & Compliance Auditor)

## Overview

This skill teaches the Hermes Agent how to act as the supreme guardian of the 1Crypten ecosystem. It enables safe, real-time auditing and compliance checks on the active PostgreSQL database running on Railway. By using dedicated, read-only and transactional scripts, the agent can fetch live bankroll metrics, active slot allocations, emancipated moonbags, and trade history. It also enables manual triggers for emergency portfolio protection (Knife-Drop).

---

## When to Use

- When the user asks for a system balance update or balance sheet: *"Hermes, /banca"* or *"como está a banca?"*.
- When you need to check which tokens are currently allocated in the 4 active Sniper slots: *"quais moedas estão nos slots?"*.
- When the user wants to audit the list of emancipated high-ROI Altcoins: *"mostre as moonbags"*.
- When executing a manual emergency rescue or immediate position closure: *"Hermes, acione o facão no par SOLUSDT"*.

### Do Not Use For:
- Writing arbitrary, untrusted data directly to the operational database tables.
- Running heavy analytical loops that could slow down the production Postgres engine.

---

## Operational Recipes

The skill leverages pre-compiled Python scripts located in `skills/productivity/1crypten-core-guardian/scripts/` to ensure safe database interactions using the system `DATABASE_URL`.

### Recipe 1: Bankroll Audit (`/banca`)
To fetch total equity, accumulated PnL, and general system health, execute:
```bash
python skills/productivity/1crypten-core-guardian/scripts/auditar_banca.py
```

### Recipe 2: Active Slots Inspection
To audit the 4 active Sniper slots and verify structural targets:
```bash
python skills/productivity/1crypten-core-guardian/scripts/auditar_slots.py
```

### Recipe 3: Manual Knife-Drop Execution (Emergency Close)
To close all active positions of a symbol immediately and reset its slot:
```bash
python skills/productivity/1crypten-core-guardian/scripts/knife_drop.py --symbol <SYMBOL>
```

---

## Common Pitfalls

1. **Missing DATABASE_URL**: If the environment variable `DATABASE_URL` is not set or accessible in the shell, connection to the Railway instance will fail. Always verify the `.env` configuration first.
2. **Direct Schema Alteration**: Never try to run direct `DROP` or `ALTER` SQL queries on production tables. Use the designated Python scripts to ensure transactional integrity.

---

## Verification Checklist

- [ ] DB connection is established using the system-wide `DATABASE_URL`.
- [ ] Read operations do not interfere with live websocket feeds in the main Sniper process.
- [ ] Telegram notifications are triggered upon emergency manual closures.
- [ ] Slots are successfully hard-reset to "LIVRE" after a Knife-Drop execution.
