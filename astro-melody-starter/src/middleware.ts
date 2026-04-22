import type { MiddlewareHandler } from 'astro';

export const onRequest: MiddlewareHandler = async (context, next) => {
  const response = await next();
  
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'SAMEORIGIN');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'geolocation=(), microphone=()');
  
  const url = new URL(context.request.url);
  const pathname = url.pathname;
  
  // Set Content-Type for XML files
  if (pathname.endsWith('.xml')) {
    response.headers.set('Content-Type', 'application/xml; charset=utf-8');
  }
  
  const cacheControl = pathname.match(/\.(jpg|jpeg|png|gif|webp|svg|mp4|webm|avif|css|js|xml)$/i)
    ? 'public, max-age=31536000, immutable'
    : 'public, max-age=3600';
  
  response.headers.set('Cache-Control', cacheControl);
  
  return response;
};
