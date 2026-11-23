import { neon } from '@neondatabase/serverless';
import { createNeonAdapter } from './_shared/neon-adapter.js';
import { handleApiRequest } from './_shared/handlers.js';

async function touchSupabaseHeartbeat() {
  const sbUrl = Deno.env.get('SUPABASE_URL');
  const sbKey = Deno.env.get('SUPABASE_ANON_KEY');
  if (!sbUrl || !sbKey) return;
  try {
    await fetch(`${sbUrl}/rest/v1/autogest_heartbeat?select=id&limit=1`, {
      headers: { apikey: sbKey, Authorization: `Bearer ${sbKey}` },
    });
  } catch {
    // Heartbeat no bloqueante
  }
}

Deno.serve(async (req: Request) => {
  const databaseUrl = Deno.env.get('NEON_DATABASE_URL');
  const corsOrigin = Deno.env.get('CORS_ORIGIN') || '*';

  if (!databaseUrl) {
    return new Response(
      JSON.stringify({
        error: 'NEON_DATABASE_URL no configurada en los secretos de Supabase Edge Functions.',
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Access-Control-Allow-Origin': corsOrigin,
        },
      }
    );
  }

  const sql = neon(databaseUrl);
  const adapter = createNeonAdapter(sql);
  const response = await handleApiRequest(req, adapter, { corsOrigin });

  // Si el servicio sigue vigente y respondió /health con 200, mantiene activo el proyecto Supabase
  const url = new URL(req.url);
  if (response.status === 200 && (url.pathname.endsWith('/health') || url.pathname.endsWith('/autogest-api'))) {
    await touchSupabaseHeartbeat();
  }

  return response;
});
