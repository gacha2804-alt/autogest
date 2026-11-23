/**
 * Configuración del frontend AutoGest.
 * - En local (node back/server.mjs): '/api' apunta al servidor local en el mismo origen.
 * - En Netlify (producción): '/api' se redirige mediante netlify.toml a Supabase Edge Functions,
 *   o puedes sobreescribir API_BASE_URL con la URL directa de tu Edge Function.
 */
window.AUTOGEST_CONFIG = {
  API_BASE_URL: '/api',
};
