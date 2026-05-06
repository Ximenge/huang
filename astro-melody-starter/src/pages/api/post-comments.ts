import type { APIRoute } from 'astro';

export const prerender = false;

interface PostComment {
  id: string;
  postId: string;
  nickname: string;
  content: string;
  ip: string;
  timestamp: number;
  likes: number;
  likedBy: string[];
  status: string;
}

interface CommentBody {
  postId: string;
  nickname?: string;
  content: string;
}

interface LikeBody {
  commentId: string;
  postId: string;
  fingerprint: string;
}

function getKV(context: any): KVNamespace | null {
  const runtime = context.locals?.runtime;
  if (runtime?.env?.POST_COMMENTS) {
    return runtime.env.POST_COMMENTS;
  }
  if (context.env?.POST_COMMENTS) {
    return context.env.POST_COMMENTS;
  }
  const globalEnv = (globalThis as any).env;
  if (globalEnv?.POST_COMMENTS) {
    return globalEnv.POST_COMMENTS;
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
    const KV = getKV(context);
    if (!KV) {
      return new Response(JSON.stringify({ error: 'KV not available' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const url = new URL(context.request.url);
    const postId = url.searchParams.get('postId');
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');

    if (!postId) {
      return new Response(JSON.stringify({ error: 'postId is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const key = `comments:${postId}`;
    const allComments = await KV.get(key, 'json') as PostComment[] || [];
    const total = allComments.length;
    const totalPages = Math.ceil(total / limit);

    const startIndex = (page - 1) * limit;
    const comments = allComments.slice(startIndex, startIndex + limit);

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
    const KV = getKV(context);
    if (!KV) {
      return new Response(JSON.stringify({ error: 'KV not available' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const request = context.request;
    const body = await request.json() as CommentBody;
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';

    if (!body.postId || body.postId.trim().length === 0) {
      return new Response(JSON.stringify({ error: '博文ID不能为空' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

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

    if (body.nickname && containsMaliciousContent(body.nickname)) {
      return new Response(JSON.stringify({ error: '昵称包含不允许的代码' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const rateLimitKey = `rate_limit:${ip}:${body.postId}`;
    const lastSubmit = await KV.get(rateLimitKey);
    if (lastSubmit && Date.now() - parseInt(lastSubmit) < 60000) {
      return new Response(JSON.stringify({ error: '提交太快了，请稍后再试' }), {
        status: 429,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    let nickname = body.nickname?.trim();
    if (!nickname || nickname.length === 0) {
      nickname = generateRandomNickname();
    }
    if (nickname.length > 20) {
      nickname = nickname.substring(0, 20);
    }

    const key = `comments:${body.postId}`;
    const comments = await KV.get(key, 'json') as PostComment[] || [];

    const newComment: PostComment = {
      id: Date.now().toString() + Math.random().toString(36).substring(2, 6),
      postId: body.postId,
      nickname: sanitizeHtml(nickname),
      content: sanitizeHtml(body.content.substring(0, 500)),
      ip,
      timestamp: Date.now(),
      likes: 0,
      likedBy: [],
      status: 'approved'
    };

    comments.unshift(newComment);

    await KV.put(key, JSON.stringify(comments));
    await KV.put(rateLimitKey, Date.now().toString(), {
      expirationTtl: 60
    });

    const responseComment = { ...newComment };
    delete (responseComment as any).ip;
    delete (responseComment as any).likedBy;

    return new Response(JSON.stringify({ success: true, comment: responseComment }), {
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

export const PUT: APIRoute = async (context) => {
  try {
    const KV = getKV(context);
    if (!KV) {
      return new Response(JSON.stringify({ error: 'KV not available' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const body = await context.request.json() as LikeBody;

    if (!body.commentId || !body.postId || !body.fingerprint) {
      return new Response(JSON.stringify({ error: '参数不完整' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const likeLimitKey = `like_limit:${body.fingerprint}:${body.commentId}`;
    const alreadyLiked = await KV.get(likeLimitKey);
    if (alreadyLiked) {
      return new Response(JSON.stringify({ error: '已经点过赞了' }), {
        status: 429,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const key = `comments:${body.postId}`;
    const comments = await KV.get(key, 'json') as PostComment[] || [];
    const comment = comments.find(c => c.id === body.commentId);

    if (!comment) {
      return new Response(JSON.stringify({ error: '评论不存在' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    comment.likes = (comment.likes || 0) + 1;
    if (!comment.likedBy) comment.likedBy = [];
    comment.likedBy.push(body.fingerprint);

    await KV.put(key, JSON.stringify(comments));
    await KV.put(likeLimitKey, '1', {
      expirationTtl: 86400 * 365
    });

    return new Response(JSON.stringify({ success: true, likes: comment.likes }), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store, no-cache, must-revalidate'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to like comment', details: String(error) }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

function generateRandomNickname(): string {
  const adjectives = ['快乐', '聪明', '勇敢', '可爱', '温柔', '阳光', '潇洒', '灵动', '悠闲', '活泼', '淡定', '酷帅', '甜美', '机智', '呆萌'];
  const nouns = ['小熊', '猫咪', '兔子', '企鹅', '海豚', '松鼠', '狐狸', '熊猫', '小鹿', '考拉', '鹦鹉', '浣熊', '水獭', '刺猬', '仓鼠'];
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
  const noun = nouns[Math.floor(Math.random() * nouns.length)];
  const letter = String.fromCharCode(65 + Math.floor(Math.random() * 26));
  const num = Math.floor(Math.random() * 100);
  return `${adj}${noun}${letter}${num}`;
}
