import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = async ({ url }) => {
  const imageUrl = url.searchParams.get('url');

  if (!imageUrl) {
    return new Response('Missing url parameter', { status: 400 });
  }

  if (!imageUrl.startsWith('https://image.91tutu.cc/')) {
    return new Response('Forbidden', { status: 403 });
  }

  try {
    const response = await fetch(imageUrl, {
      headers: {
        'User-Agent': '91tutu-ImageProxy/1.0',
      },
    });

    if (!response.ok) {
      return new Response('Upstream error', { status: response.status });
    }

    const contentType = response.headers.get('Content-Type') || 'image/webp';

    return new Response(response.body, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=604800',
      },
    });
  } catch (error) {
    return new Response('Fetch failed', { status: 502 });
  }
};
