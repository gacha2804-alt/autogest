/**
 * Configuración del frontend AutoGest.
 * - En local (node back/server.mjs): '/api' apunta al servidor local en el mismo origen.
 * - En Netlify (producción): '/api' se redirige mediante netlify.toml a Supabase Edge Functions.
 * - ACTIVE_UNTIL: fecha de cierre automático (5 de diciembre de 2026, 23:59:59 COT / UTC-5).
 */
window.AUTOGEST_CONFIG = {
  API_BASE_URL: '/api',
  ACTIVE_UNTIL: '2026-12-06T04:59:59.000Z',
};
