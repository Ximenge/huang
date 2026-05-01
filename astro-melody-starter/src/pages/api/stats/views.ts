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
  const slugsParam = url.searchParams.get('slugs') || '';
  const slugs = slugsParam.split(',').filter(Boolean);

  if (slugs.length === 0) {
    return new Response(JSON.stringify({}), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const limitedSlugs = slugs.slice(0, 50);

  const results: Record<string, number> = {};
  await Promise.all(limitedSlugs.map(async (slug) => {
    const count = await STATS.get(`views:${slug}`);
    results[slug] = parseInt(count || '0');
  }));

  return new Response(JSON.stringify(results), {
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

  const ip = context.request.headers.get('CF-Connecting-IP') || 'unknown';
  const rateLimitKey = `rate_limit:view:${ip}:${slug}`;
  const lastView = await STATS.get(rateLimitKey);

  let views: number;
  if (lastView) {
    views = parseInt(await STATS.get(`views:${slug}`) || '0');
    return new Response(JSON.stringify({ slug, views, throttled: true }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const currentViews = parseInt(await STATS.get(`views:${slug}`) || '0');
  views = currentViews + 1;
  await STATS.put(`views:${slug}`, views.toString());
  await STATS.put(rateLimitKey, Date.now().toString(), { expirationTtl: 60 });

  return new Response(JSON.stringify({ slug, views }), {
    headers: { 'Content-Type': 'application/json' }
  });
};
