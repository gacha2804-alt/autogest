import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { getNeonClient } from './env-utils.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runMigrate() {
  const sql = await getNeonClient();
  const schemaPath = path.join(__dirname, 'schema.sql');
  const rawSql = fs.readFileSync(schemaPath, 'utf8');

  // Separar sentencias SQL eliminando comentarios de línea
  const statements = rawSql
    .split(/;\s*(?:\r?\n|$)/)
    .map((s) =>
      s
        .split(/\r?\n/)
        .filter((line) => !line.trim().startsWith('--'))
        .join('\n')
        .trim()
    )
    .filter((s) => s.length > 0);

  console.log(`[db:migrate] Aplicando ${statements.length} sentencias SQL en NeonDB...`);
  for (let i = 0; i < statements.length; i++) {
    await sql.query(statements[i]);
  }
  console.log('[db:migrate] Esquema creado/verificado correctamente en NeonDB.');
}

runMigrate().catch((err) => {
  console.error('[db:migrate] Error:', err.message);
  process.exit(1);
});
