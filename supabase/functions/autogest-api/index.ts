import { neon } from '@neondatabase/serverless';
import { createNeonAdapter } from '../_shared/neon-adapter.js';
import { handleApiRequest } from '../_shared/handlers.js';

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
  return await handleApiRequest(req, adapter, { corsOrigin });
});
