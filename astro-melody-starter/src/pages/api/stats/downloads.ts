import type { APIRoute } from 'astro';

export const prerender = false;

function getStatsKV(context: any): KVNamespace | null {
  const runtime = context.locals?.runtime;
  if (runtime?.env?.STATS) return runtime.env.STATS;
  if (context.env?.STATS) return context.env.STATS;
  const globalEnv = (globalThis as any).env;
  if (globalEnv?.STATS) return globalEnv.STATS;
  return null;
}

export const GET: APIRoute = async (context) => {
  const STATS = getStatsKV(context);
  if (!STATS) {
    return new Response(JSON.stringify({ error: 'KV not available' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const url = new URL(context.request.url);
  const slug = url.searchParams.get('slug') || '';

  if (!slug) {
    return new Response(JSON.stringify({ error: 'Missing slug' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const downloads = parseInt(await STATS.get(`downloads:${slug}`) || '0');

  return new Response(JSON.stringify({ slug, downloads }), {
    headers: { 'Content-Type': 'application/json' }
  });
};

export const POST: APIRoute = async (context) => {
  const STATS = getStatsKV(context);
  if (!STATS) {
    return new Response(JSON.stringify({ error: 'KV not available' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const body = await context.request.json() as { slug: string };
  const { slug } = body;

  if (!slug) {
    return new Response(JSON.stringify({ error: 'Missing slug' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const currentDownloads = parseInt(await STATS.get(`downloads:${slug}`) || '0');
  const downloads = currentDownloads + 1;
  await STATS.put(`downloads:${slug}`, downloads.toString());

  return new Response(JSON.stringify({ slug, downloads }), {
    headers: { 'Content-Type': 'application/json' }
  });
};
