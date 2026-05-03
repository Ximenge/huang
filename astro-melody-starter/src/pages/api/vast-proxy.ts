import type { APIRoute } from 'astro';

export const prerender = false;

const ALLOWED_HOSTS = ['s.magsrv.com'];

export const GET: APIRoute = async ({ url }) => {
  const vastUrl = url.searchParams.get('url');

  if (!vastUrl) {
    return new Response('Missing url parameter', { status: 400 });
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(vastUrl);
  } catch {
    return new Response('Invalid url parameter', { status: 400 });
  }

  if (!ALLOWED_HOSTS.includes(parsedUrl.hostname)) {
    return new Response('Forbidden', { status: 403 });
  }

  try {
    const response = await fetch(vastUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; 91tutu-VastProxy/1.0)',
        'Accept': 'application/xml, text/xml, */*',
      },
    });

    if (!response.ok) {
      return new Response('Upstream error', { status: response.status });
    }

    const xml = await response.text();

    return new Response(xml, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml; charset=utf-8',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    return new Response('Proxy error', { status: 502 });
  }
};
