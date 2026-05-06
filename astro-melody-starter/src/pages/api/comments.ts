import type { APIRoute } from 'astro';

export const prerender = false;

interface Comment {
  id: string;
  nickname: string;
  content: string;
  ip: string;
  timestamp: number;
  status: string;
}

interface CommentBody {
  content: string;
}

function getKV(context: any): KVNamespace | null {
  const runtime = context.locals?.runtime;
  if (runtime?.env?.GUESTBOOK) {
    return runtime.env.GUESTBOOK;
  }
  
  if (context.env?.GUESTBOOK) {
    return context.env.GUESTBOOK;
  }
  
  const globalEnv = (globalThis as any).env;
  if (globalEnv?.GUESTBOOK) {
    return globalEnv.GUESTBOOK;
  }
  
  return null;
}

function sanitizeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}

function containsMaliciousContent(str: string): boolean {
  const lower = str.toLowerCase();
  const patterns = [
    /<\s*script/i,
    /<\s*img[^>]*onerror/i,
    /<\s*iframe/i,
    /<\s*object/i,
    /<\s*embed/i,
    /<\s*svg[^>]*onload/i,
    /<\s*body[^>]*onload/i,
    /<\s*input[^>]*onfocus/i,
    /<\s*details[^>]*on toggle/i,
    /<\s*marquee[^>]*onstart/i,
    /<\s*video[^>]*onerror/i,
    /<\s*audio[^>]*onerror/i,
    /javascript\s*:/i,
    /on\w+\s*=/i,
    /data\s*:\s*text\/html/i,
    /vbscript\s*:/i,
    /expression\s*\(/i,
    /url\s*\(\s*javascript/i,
    /document\.(cookie|location|write|domain)/i,
    /window\.(location|open|eval)/i,
    /eval\s*\(/i,
    /setTimeout\s*\(\s*['"]/i,
    /setInterval\s*\(\s*['"]/i,
    /new\s+Function\s*\(/i,
  ];
  return patterns.some(pattern => pattern.test(lower));
}

export const GET: APIRoute = async (context) => {
  try {
    const GUESTBOOK = getKV(context);
    
    if (!GUESTBOOK) {
      return new Response(JSON.stringify({ 
        error: 'KV not available', 
        debug: 'GUESTBOOK binding not found',
        locals: Object.keys(context.locals || {})
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const url = new URL(context.request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');
    
    const allComments = await GUESTBOOK.get('comments:all', 'json') as Comment[] || [];
    const total = allComments.length;
    const totalPages = Math.ceil(total / limit);
    
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const comments = allComments.slice(startIndex, endIndex);
    
    return new Response(JSON.stringify({
      comments,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasMore: page < totalPages
      }
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, no-cache, must-revalidate'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to fetch comments', details: String(error) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

export const POST: APIRoute = async (context) => {
  try {
    const GUESTBOOK = getKV(context);
    
    if (!GUESTBOOK) {
      return new Response(JSON.stringify({ 
        error: 'KV not available', 
        debug: 'GUESTBOOK binding not found',
        locals: Object.keys(context.locals || {})
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const request = context.request;
    const body = await request.json() as CommentBody;
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';

    if (!body.content || body.content.trim().length < 2) {
      return new Response(JSON.stringify({ error: '内容太短了，至少2个字' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (body.content.length > 500) {
      return new Response(JSON.stringify({ error: '内容太长了，最多500字' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (containsMaliciousContent(body.content)) {
      return new Response(JSON.stringify({ error: '内容包含不允许的代码' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const lastSubmit = await GUESTBOOK.get(`rate_limit:${ip}`);
    if (lastSubmit && Date.now() - parseInt(lastSubmit) < 60000) {
      return new Response(JSON.stringify({ error: '提交太快了，请稍后再试' }), {
        status: 429,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const comments = await GUESTBOOK.get('comments:all', 'json') as Comment[] || [];
    
    const anonymousNames = ['匿名用户', '游客', '路人甲', '过客', '访客', '神秘人'];
    const randomName = anonymousNames[Math.floor(Math.random() * anonymousNames.length)];
    
    const newComment: Comment = {
      id: Date.now().toString(),
      nickname: randomName,
      content: sanitizeHtml(body.content.substring(0, 500)),
      ip,
      timestamp: Date.now(),
      status: 'approved'
    };

    comments.unshift(newComment);

    await GUESTBOOK.put('comments:all', JSON.stringify(comments));
    await GUESTBOOK.put(`rate_limit:${ip}`, Date.now().toString(), {
      expirationTtl: 60
    });

    return new Response(JSON.stringify({ success: true, comment: newComment }), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, no-cache, must-revalidate'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to submit comment', details: String(error) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
