# AutoGest · Frontend (Netlify)

Dashboard analítico interactivo de **AutoGest** (Minería de Datos y Métodos Numéricos · UNIMINUTO Ibagué), preparado para publicación directa en **Netlify** desde la rama `deploy/frontend`.

## Archivos incluidos
- `index.html`: Dashboard principal (EDA, Torneo ML, Clustering K-Means, Regresión Lineal Semestral $N=25$ y Anual $N=13$, Interpolación de Lagrange, filtros dinámicos e historial de predicciones).
- `metodos.html`: Vista detallada paso a paso de Métodos Numéricos y calculadora interactiva.
- `chart.umd.min.js`: Chart.js empaquetado localmente.
- `config.js` y `api-client.js`: Cliente HTTP que consume `/api/*` (redirigido vía `netlify.toml` a Supabase Edge Functions → NeonDB).
- `netlify.toml`: Configuración de publicación (`.`), cabeceras de seguridad y proxy `/api/*`.

## Despliegue en Netlify
- **Rama de producción:** `deploy/frontend`
- **Build command:** *(vacío — sitio estático puro)*
- **Publish directory:** `.`
