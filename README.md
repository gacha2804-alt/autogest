# AutoGest · Backend (Supabase Edge Functions + NeonDB)

API REST y esquema PostgreSQL de **AutoGest**, preparado para desplegarse como **Supabase Edge Function** (`autogest-api`) conectado a **NeonDB** desde la rama `deploy/backend`.

## Estructura
- `supabase/functions/autogest-api/`: Edge Function (Deno/TypeScript) con `verify_jwt = false`.
- `supabase/functions/_shared/`: Lógica compartida (`handlers.js`, `math.js`, `neon-adapter.js`, `static-catalog.js`).
- `db/`: Esquema SQL (`schema.sql`), migración (`migrate.mjs`) y carga inicial idempotente (`seed.mjs`).
- `dataset/`: Únicamente los 2 CSV consolidados (`dataset_integrado.csv` y `dataset_reducido.csv`, < 140 KB en total).
- `server.mjs`: Servidor de desarrollo local en Node 22.
- `tests/api.test.mjs` y `scripts/cdp-report.mjs`: Pruebas automatizadas y auditoría Chrome Remote Debugging (CDP).

## Uso rápido en local
```bash
npm install
cp .env.example .env   # Configura tu NEON_DATABASE_URL
npm run db:setup       # Crea las 5 tablas y carga los 507 registros en NeonDB
npm test               # Ejecuta pruebas automatizadas
npm run dev            # Levanta la API local en http://127.0.0.1:3000/api/health
```
