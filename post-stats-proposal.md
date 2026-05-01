# 博文浏览量与下载量统计功能技术方案

## 1. 需求概述

| 需求 | 描述 | 展示位置 |
|------|------|----------|
| 浏览量统计 | 统计每个博文的点击/浏览次数 | 首页/列表页博文卡片封面右下角 |
| 下载量统计 | 统计每个博文的 ZIP 下载次数 | 博文详情页下载按钮旁边（已下载 XXX 次） |

---

## 2. 现有代码分析

### 2.1 数据库现状

项目使用 **Cloudflare KV** 作为数据库，已在 `wrangler.toml` 中配置：

```toml
[[kv_namespaces]]
binding = "GUESTBOOK"
id = "98545db89c3a4b0191d8daff2471ae87"
```

留言板 API（`comments.ts`）的 KV 使用模式：

```typescript
// 获取 KV 实例
function getKV(context: any): KVNamespace | null {
  const runtime = context.locals?.runtime;
  if (runtime?.env?.GUESTBOOK) return runtime.env.GUESTBOOK;
  if (context.env?.GUESTBOOK) return context.env.GUESTBOOK;
  const globalEnv = (globalThis as any).env;
  if (globalEnv?.GUESTBOOK) return globalEnv.GUESTBOOK;
  return null;
}

// 读取
const comments = await GUESTBOOK.get('comments:all', 'json');

// 写入
await GUESTBOOK.put('comments:all', JSON.stringify(comments));

// 带过期时间写入
await GUESTBOOK.put(`rate_limit:${ip}`, Date.now().toString(), { expirationTtl: 60 });
```

**关键点**：
- 当前只有一个 KV namespace（`GUESTBOOK`），用于留言板
- KV 的 `get/put` 是最终一致性，不适合高并发计数（但有变通方案）
- API 路由必须设置 `export const prerender = false` 才能访问 KV

### 2.2 博文卡片组件

博文卡片在 3 个组件中渲染：

| 组件 | 用途 | 特点 |
|------|------|------|
| `CommonCard.astro` | 首页/列表页普通卡片 | `h-[300px]`，封面+底部渐变遮罩+标题 |
| `HeroCard.astro` | 首页第一个大卡片 | `min-h-[500px]`，封面+描述 |
| `RelatedPostsCard.astro` | 详情页相关推荐 | 简单卡片列表 |

**CommonCard 当前结构**（需要添加浏览量的位置）：

```html
<div class="relative h-[300px] ...">
  <a href={`/posts/${post.id}/`}>
    <figure class="h-full">
      <OptimizedCover ... />
    </figure>
    <div class="absolute bottom-0 left-0 right-0 p-4 text-white bg-gradient-to-t from-black/70 to-transparent">
      <!-- tags -->
      <!-- date -->
      <!-- title -->
      ← 这里需要添加浏览量（右下角）
    </div>
  </a>
</div>
```

**使用 CommonCard 的页面**：
- `src/pages/index.astro`（首页）
- `src/pages/page/[page].astro`（分页）
- `src/pages/category/[category]/[page].astro`（分类页）
- `src/pages/tags/[tag]/[page].astro`（标签页）

### 2.3 下载按钮组件

`DownloadAllImages.astro` 当前结构：

```html
<div class="not-prose my-6">
  <div class="flex items-center gap-3 p-4 ...">
    <svg>...</svg>
    <span>下载本页全部图片：</span>
    <button id="download-all-images">下载 ZIP</button>
    <span id="download-status">...</span>
    ← 这里需要添加下载次数
  </div>
</div>
```

### 2.4 博文详情页

`[...slug].astro` 是静态预渲染页面（`output: "static"`），通过 `getStaticPaths()` 生成。

**关键约束**：静态页面无法在构建时获取 KV 中的实时统计数据，必须在客户端通过 API 获取。

### 2.5 Astro 配置

```javascript
output: "static",    // 静态站点生成
adapter: cloudflare(),  // Cloudflare Pages 部署
prefetch: {
  prefetchAll: true,     // 预取所有链接
  defaultStrategy: "viewport",  // 视口内预取
},
```

---

## 3. 核心技术决策

### 3.1 数据存储：复用 GUESTBOOK KV vs 新建 KV

| 方案 | 优势 | 劣势 |
|------|------|------|
| 复用 GUESTBOOK KV | 无需修改 wrangler.toml，零配置 | 命名不语义化，与留言板数据混存 |
| **新建 STATS KV** | **语义清晰，独立管理，可单独清理** | **需修改 wrangler.toml，需部署配置** |

**决策：新建 STATS KV**

理由：
1. 浏览量/下载量数据与留言板数据生命周期不同
2. 统计数据可能很大（1400+篇博文），独立存储便于管理
3. KV 的 key 前缀隔离虽然可行，但语义上不够清晰
4. 新建 KV 只需在 wrangler.toml 加一行配置

### 3.2 KV 计数方案

Cloudflare KV 是最终一致性存储，直接 `get → +1 → put` 在高并发下会丢失计数。

**方案对比**：

| 方案 | 原理 | 精度 | 复杂度 | 成本 |
|------|------|------|--------|------|
| 简单 get+put | 读取→加1→写入 | 低（并发丢数） | 最低 | 免费 |
| **分片计数** | 按时间段分片，读取时合并 | 中（秒级精度） | 中 | 免费 |
| Cloudflare Durable Objects | 强一致性原子计数 | 高 | 高 | 付费 |
| Workers Analytics Engine | 专门的分析引擎 | 高 | 中 | 免费额度 |

**决策：分片计数方案**

理由：
1. 免费，无需额外付费
2. 精度足够（博客场景并发量不高，偶尔丢1-2次可接受）
3. 实现简单，与现有 KV 模式一致
4. 可以后续升级到 Durable Objects

**分片计数原理**：

```
写入时：
  key = "views:{slug}:{分钟级时间戳}"
  value = 当前值 + 1（或新建为1）

读取时：
  列出所有 "views:{slug}:*" 的 key
  汇总所有分片的值 = 总浏览量
```

**简化方案（推荐）**：

考虑到博客的实际并发量极低（每分钟同一博文几乎不可能有2人同时浏览），采用**简单 get+put + 防抖**方案：

```typescript
// 写入浏览量
async function incrementView(slug: string, kv: KVNamespace): Promise<number> {
  const key = `views:${slug}`;
  const current = parseInt(await kv.get(key) || '0');
  const newCount = current + 1;
  await kv.put(key, newCount.toString());
  return newCount;
}

// 读取浏览量
async function getViewCount(slug: string, kv: KVNamespace): Promise<number> {
  const count = await kv.get(`views:${slug}`);
  return parseInt(count || '0');
}
```

> 博客场景下，简单方案完全够用。即使偶尔丢数，浏览量本身就是近似值，无需强一致性。

### 3.3 浏览量统计触发时机

| 方案 | 触发方式 | 精度 | 用户体验 |
|------|----------|------|----------|
| 卡片点击时 | 首页点卡片跳转时调用 API | 精确 | 无感知 |
| 详情页加载时 | 详情页 JS 调用 API | 精确 | 无感知 |
| **两者结合** | **详情页加载时调用，卡片展示读取** | **精确** | **无感知** |

**决策：详情页加载时触发**

理由：
1. 用户可能从搜索引擎/外链直接进入详情页，卡片点击无法覆盖
2. 详情页加载 = 真实浏览，更准确
3. 避免用户在首页快速划过卡片就计数的误统计

### 3.4 防刷机制

| 机制 | 实现 | 说明 |
|------|------|------|
| IP 频率限制 | 同一 IP 同一博文 60秒内只计1次 | 借鉴留言板 rate_limit 模式 |
| Session 去重 | localStorage 记录已浏览的博文 | 客户端去重，减少 API 调用 |

### 3.5 数据展示方式

**问题**：首页是静态生成的（SSG），构建时无法获取 KV 中的实时浏览量。

**方案**：客户端 JS 异步加载浏览量

```
首页静态 HTML 渲染卡片（无浏览量数据）
  ↓
页面加载完成后，JS 批量请求 /api/stats?type=views&slugs=slug1,slug2,...
  ↓
API 从 KV 读取浏览量，返回 { slug1: 123, slug2: 456, ... }
  ↓
JS 将浏览量数字插入到每个卡片的指定位置
```

---

## 4. 详细设计

### 4.1 KV 数据结构

```
STATS KV Namespace
├── views:{slug}              → "123"         (浏览量计数)
├── downloads:{slug}          → "45"          (下载量计数)
├── rate_limit:view:{ip}:{slug} → timestamp   (浏览频率限制，TTL=60s)
└── rate_limit:download:{ip}:{slug} → timestamp (下载频率限制，TTL=60s)
```

**示例**：

```
views:gesheng-No014-aerweinaxiunv-50P-249MB → "358"
downloads:gesheng-No014-aerweinaxiunv-50P-249MB → "42"
rate_limit:view:1.2.3.4:gesheng-No014-aerweinaxiunv-50P-249MB → "1714100000000" (TTL=60)
```

### 4.2 API 设计

#### 4.2.1 浏览量 API — `/api/stats/views`

**POST /api/stats/views** — 记录一次浏览（详情页加载时调用）

```typescript
// 请求
POST /api/stats/views
Content-Type: application/json
Body: { "slug": "gesheng-No014-aerweinaxiunv-50P-249MB" }

// 响应（成功）
{ "slug": "gesheng-No014-...", "views": 359 }

// 响应（频率限制，不计入）
{ "slug": "gesheng-No014-...", "views": 358, "throttled": true }
```

**GET /api/stats/views** — 批量获取浏览量（首页/列表页调用）

```typescript
// 请求
GET /api/stats/views?slugs=slug1,slug2,slug3

// 响应
{
  "slug1": 123,
  "slug2": 456,
  "slug3": 0
}
```

#### 4.2.2 下载量 API — `/api/stats/downloads`

**POST /api/stats/downloads** — 记录一次下载（下载按钮点击时调用）

```typescript
// 请求
POST /api/stats/downloads
Content-Type: application/json
Body: { "slug": "gesheng-No014-aerweinaxiunv-50P-249MB" }

// 响应
{ "slug": "gesheng-No014-...", "downloads": 43 }
```

**GET /api/stats/downloads** — 获取单个博文下载量（详情页调用）

```typescript
// 请求
GET /api/stats/downloads?slug=gesheng-No014-aerweinaxiunv-50P-249MB

// 响应
{ "slug": "gesheng-No014-...", "downloads": 43 }
```

#### 4.2.3 合并 API — `/api/stats`（可选）

为减少 API 调用次数，可以合并为一个 API：

```typescript
// 详情页加载时：记录浏览 + 获取下载量
POST /api/stats
Body: { "slug": "xxx", "action": "view" }
Response: { "views": 359, "downloads": 43 }

// 首页：批量获取浏览量
GET /api/stats?slugs=slug1,slug2,slug3
Response: { "slug1": { "views": 123 }, "slug2": { "views": 456 } }
```

**决策：使用分离的 API**，职责更清晰，便于独立缓存和限流。

### 4.3 API 实现参考

#### `/api/stats/views.ts`

```typescript
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

  // 限制批量查询数量，防止滥用
  const limitedSlugs = slugs.slice(0, 50);

  const results: Record<string, number> = {};
  // KV 批量读取
  await Promise.all(limitedSlugs.map(async (slug) => {
    const count = await STATS.get(`views:${slug}`);
    results[slug] = parseInt(count || '0');
  }));

  return new Response(JSON.stringify(results), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=30'  // 缓存30秒
    }
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

  // IP 频率限制：同一 IP 同一博文 60秒内只计1次
  const ip = context.request.headers.get('CF-Connecting-IP') || 'unknown';
  const rateLimitKey = `rate_limit:view:${ip}:${slug}`;
  const lastView = await STATS.get(rateLimitKey);

  let views: number;
  if (lastView) {
    // 频率限制内，不计入，但返回当前浏览量
    views = parseInt(await STATS.get(`views:${slug}`) || '0');
    return new Response(JSON.stringify({ slug, views, throttled: true }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 计入浏览量
  const currentViews = parseInt(await STATS.get(`views:${slug}`) || '0');
  views = currentViews + 1;
  await STATS.put(`views:${slug}`, views.toString());
  await STATS.put(rateLimitKey, Date.now().toString(), { expirationTtl: 60 });

  return new Response(JSON.stringify({ slug, views }), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store'
    }
  });
};
```

#### `/api/stats/downloads.ts`

```typescript
import type { APIRoute } from 'astro';

export const prerender = false;

function getStatsKV(context: any): KVNamespace | null {
  // 同 views.ts
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
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=30'
    }
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

  // 下载量不做频率限制（每次真实下载都应计入）
  const currentDownloads = parseInt(await STATS.get(`downloads:${slug}`) || '0');
  const downloads = currentDownloads + 1;
  await STATS.put(`downloads:${slug}`, downloads.toString());

  return new Response(JSON.stringify({ slug, downloads }), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store'
    }
  });
};
```

### 4.4 前端组件改造

#### 4.4.1 CommonCard.astro — 添加浏览量展示

**当前结构**：

```html
<div class="relative h-[300px] ...">
  <a href={`/posts/${post.id}/`}>
    <figure>...</figure>
    <div class="absolute bottom-0 left-0 right-0 p-4 ...">
      <div class="flex items-center gap-1 text-xs"><!-- tags --></div>
      <p class="text-xs opacity-90"><!-- date --></p>
      <h3 class="card-title text-white"><!-- title --></h3>
    </div>
  </a>
</div>
```

**改造后**：

```html
<div class="relative h-[300px] ...">
  <a href={`/posts/${post.id}/`}>
    <figure>...</figure>
    <!-- 浏览量角标 - 右下角 -->
    <div class="absolute bottom-3 right-3 z-10 flex items-center gap-1
                bg-black/50 backdrop-blur-sm rounded-full px-2 py-0.5
                text-white text-xs">
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z">
        </path>
      </svg>
      <span data-view-count={post.id}>-</span>
    </div>
    <div class="absolute bottom-0 left-0 right-0 p-4 ...">
      <!-- 原有内容不变 -->
    </div>
  </a>
</div>
```

**关键**：使用 `data-view-count={post.id}` 属性标记需要填充浏览量的元素，JS 通过这个属性找到对应元素并填入数据。

#### 4.4.2 HeroCard.astro — 添加浏览量展示

与 CommonCard 类似，在封面右下角添加浏览量角标。

#### 4.4.3 DownloadAllImages.astro — 添加下载量展示

**当前结构**：

```html
<button id="download-all-images">下载 ZIP</button>
<span id="download-status">...</span>
```

**改造后**：

```html
<button id="download-all-images">下载 ZIP</button>
<span id="download-count" class="text-xs text-gray-500 dark:text-gray-400 ml-1">
  已下载 <span id="download-count-number">-</span> 次
</span>
<span id="download-status">...</span>
```

### 4.5 前端 JS 逻辑

#### 4.5.1 浏览量加载脚本（列表页）

在首页/列表页，页面加载后批量获取所有卡片的浏览量：

```javascript
(function() {
  function loadViewCounts() {
    // 收集所有需要显示浏览量的 slug
    var elements = document.querySelectorAll('[data-view-count]');
    if (elements.length === 0) return;

    var slugs = [];
    elements.forEach(function(el) {
      var slug = el.getAttribute('data-view-count');
      if (slug && slugs.indexOf(slug) === -1) {
        slugs.push(slug);
      }
    });

    if (slugs.length === 0) return;

    // 批量请求浏览量（分批，每批50个）
    var batchSize = 50;
    for (var i = 0; i < slugs.length; i += batchSize) {
      var batch = slugs.slice(i, i + batchSize);
      fetch('/api/stats/views?slugs=' + batch.join(','))
        .then(function(res) { return res.json(); })
        .then(function(data) {
          // 填充浏览量
          elements.forEach(function(el) {
            var slug = el.getAttribute('data-view-count');
            if (data[slug] !== undefined) {
              el.textContent = formatCount(data[slug]);
            }
          });
        })
        .catch(function(err) {
          console.warn('浏览量加载失败:', err);
          elements.forEach(function(el) {
            el.textContent = '';
          });
        });
    }
  }

  function formatCount(count) {
    if (count >= 10000) return (count / 10000).toFixed(1) + '万';
    if (count >= 1000) return (count / 1000).toFixed(1) + 'k';
    return count.toString();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadViewCounts);
  } else {
    loadViewCounts();
  }

  document.addEventListener('astro:page-load', function() {
    setTimeout(loadViewCounts, 300);
  });
})();
```

#### 4.5.2 浏览量上报脚本（详情页）

在博文详情页加载时，上报一次浏览：

```javascript
(function() {
  function reportView() {
    var slugEl = document.getElementById('download-post-title');
    if (!slugEl) return;

    // 从 URL 中提取 slug
    var path = window.location.pathname;
    var match = path.match(/\/posts\/([^/]+)\//);
    if (!match) return;

    var slug = match[1];

    fetch('/api/stats/views', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slug: slug })
    }).catch(function(err) {
      console.warn('浏览量上报失败:', err);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', reportView);
  } else {
    reportView();
  }

  document.addEventListener('astro:page-load', function() {
    setTimeout(reportView, 500);
  });
})();
```

#### 4.5.3 下载量加载+上报脚本（详情页）

修改 `DownloadAllImages.astro` 中的下载逻辑：

```javascript
// 在 downloadAllImages() 函数开头添加下载量上报
function downloadAllImages() {
  // ... 原有逻辑 ...

  // 上报下载量
  reportDownload();
}

function reportDownload() {
  var path = window.location.pathname;
  var match = path.match(/\/posts\/([^/]+)\//);
  if (!match) return;
  var slug = match[1];

  fetch('/api/stats/downloads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ slug: slug })
  }).catch(function(err) {
    console.warn('下载量上报失败:', err);
  });
}

// 加载下载量
function loadDownloadCount() {
  var path = window.location.pathname;
  var match = path.match(/\/posts\/([^/]+)\//);
  if (!match) return;
  var slug = match[1];

  fetch('/api/stats/downloads?slug=' + encodeURIComponent(slug))
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var el = document.getElementById('download-count-number');
      if (el && data.downloads !== undefined) {
        el.textContent = data.downloads;
      }
    })
    .catch(function() {
      var el = document.getElementById('download-count-number');
      if (el) el.textContent = '0';
    });
}
```

### 4.6 wrangler.toml 配置变更

```toml
[[kv_namespaces]]
binding = "GUESTBOOK"
id = "98545db89c3a4b0191d8daff2471ae87"

# 新增：统计数据 KV
[[kv_namespaces]]
binding = "STATS"
id = "<需要创建后填入>"

[env.preview]
[[env.preview.kv_namespaces]]
binding = "GUESTBOOK"
id = "98545db89c3a4b0191d8daff2471ae87"
[[env.preview.kv_namespaces]]
binding = "STATS"
id = "<需要创建后填入>"
```

**创建 KV namespace 命令**：

```bash
npx wrangler kv namespace create STATS
# 输出: { id: "xxxx" } ← 填入 wrangler.toml

npx wrangler kv namespace create STATS --preview
# 输出: { id: "xxxx" } ← 填入 preview 配置
```

---

## 5. 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `wrangler.toml` | 修改 | 新增 STATS KV namespace 配置 |
| `src/pages/api/stats/views.ts` | **新增** | 浏览量 API（GET 批量查询 + POST 上报） |
| `src/pages/api/stats/downloads.ts` | **新增** | 下载量 API（GET 查询 + POST 上报） |
| `src/components/CommonCard.astro` | 修改 | 添加浏览量角标（右下角） |
| `src/components/HeroCard.astro` | 修改 | 添加浏览量角标（右下角） |
| `src/components/DownloadAllImages.astro` | 修改 | 添加下载量显示 + 上报逻辑 |
| `src/pages/posts/[...slug].astro` | 修改 | 添加浏览量上报脚本 |

---

## 6. UI 效果示意

### 6.1 首页博文卡片（CommonCard）

```
┌──────────────────────────────┐
│                              │
│        封面图片               │
│                              │
│                              │
│  ┌──────────────┐        👁 123 ── 右下角角标
│  │ tag1  tag2   │            │
│  │ 2026-04-26   │            │
│  │ 博文标题     │            │
│  └──────────────┘            │
└──────────────────────────────┘
```

角标样式：半透明黑底 + 毛玻璃效果 + 白色眼睛图标 + 数字

### 6.2 首页大卡片（HeroCard）

```
┌──────────────────────────────────────────┐
│                                          │
│              封面图片                     │
│                                          │
│  ┌──────────────────────┐        👁 1.2k │
│  │ tag1  tag2  tag3     │                │
│  │ 2026-04-26           │                │
│  │ 博文标题             │                │
│  │ 描述文字...          │                │
│  └──────────────────────┘                │
└──────────────────────────────────────────┘
```

### 6.3 详情页下载区域

```
┌──────────────────────────────────────────────────────────────┐
│ 📥 下载本页全部图片：  [📥 下载 ZIP]  已下载 42 次             │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. 数据流完整图

### 7.1 浏览量

```
                    首页/列表页                              详情页
                        │                                      │
                        ▼                                      ▼
               静态 HTML 渲染卡片                        静态 HTML 渲染页面
           （浏览量显示为 "-"）                        （下载量显示为 "-"）
                        │                                      │
                        ▼                                      ▼
              JS: loadViewCounts()                    JS: reportView()
              GET /api/stats/views                   POST /api/stats/views
              ?slugs=slug1,slug2,...                  { slug: "xxx" }
                        │                                      │
                        ▼                                      ▼
              API 从 KV 读取浏览量              API: 检查 IP 频率限制
              返回 { slug1: 123, ... }              │              │
                        │                     未限制 → +1 写入 KV    已限制 → 跳过
                        ▼                          返回 views 数    返回 views 数
              JS 填充浏览量数字                           │
              "123" 替换 "-"                             ▼
                                                   JS: loadDownloadCount()
                                                   GET /api/stats/downloads?slug=xxx
                                                        │
                                                        ▼
                                                   API 从 KV 读取下载量
                                                   返回 { downloads: 42 }
                                                        │
                                                        ▼
                                                   JS 填充 "已下载 42 次"
```

### 7.2 下载量

```
                    详情页
                      │
                      ▼
              用户点击"下载 ZIP"按钮
                      │
                      ▼
              JS: downloadAllImages()
              （原有下载逻辑不变）
                      │
                      ▼
              JS: reportDownload()  ← 新增
              POST /api/stats/downloads
              { slug: "xxx" }
                      │
                      ▼
              API: 下载量 +1 写入 KV
              返回 { downloads: 43 }
                      │
                      ▼
              JS 更新 "已下载 43 次"
```

---

## 8. 性能与成本分析

### 8.1 KV 读写量预估

| 操作 | 频率 | KV 读取/次 | KV 写入/次 |
|------|------|-----------|-----------|
| 详情页浏览上报 | 每次访问 | 2（views + rate_limit） | 2（views + rate_limit） |
| 首页批量获取浏览量 | 每次首页加载 | N（N=卡片数，最多50） | 0 |
| 下载量上报 | 每次下载 | 1 | 1 |
| 下载量查询 | 每次详情页加载 | 1 | 0 |

**假设日均 1000 PV**：
- KV 读取：~3000次/天（浏览上报 2000 + 首页批量 500 + 下载查询 500）
- KV 写入：~1500次/天（浏览上报 1000 + 下载上报 500）

**Cloudflare KV 免费额度**：10万次读取/天 + 1000次写入/天

⚠️ **写入可能超出免费额度**（1000次/天）。需要考虑：
1. 浏览上报的 rate_limit 机制已经减少了大量写入（同一 IP 60秒内只写1次）
2. 实际写入量 ≈ 独立访客数，远低于 PV
3. 如果仍超限，可增加 rate_limit TTL（如 300秒）
4. 超出后费用：$0.50/百万次写入，非常便宜

### 8.2 首页加载性能

- 批量浏览量 API 响应时间：~50-100ms（KV 批量读取）
- 可设置 `Cache-Control: public, max-age=30` 缓存30秒
- 浏览量数字初始显示为 "-"，加载后替换，不影响 LCP

### 8.3 详情页加载性能

- 浏览上报是异步 POST，不阻塞页面渲染
- 下载量查询是异步 GET，不阻塞下载按钮使用
- 两个请求可并行发出

---

## 9. 边界情况处理

| 场景 | 处理方式 |
|------|----------|
| KV 不可用 | API 返回错误，前端显示 "-" 或 "0"，不影响正常使用 |
| 首页有 50+ 卡片 | 分批请求，每批50个 slug |
| slug 包含特殊字符 | API 使用 `encodeURIComponent` 编码 |
| 爬虫访问 | 浏览上报 API 不做爬虫过滤（爬虫通常不执行 JS） |
| Astro 客户端路由 | 监听 `astro:page-load` 事件重新加载 |
| 广告拦截器拦截 /api/stats | 浏览量/下载量显示为 "-"，不影响核心功能 |
| localStorage 禁用 | 不影响，所有数据存在 KV 中 |

---

## 10. 实施步骤

1. **创建 KV namespace**：`npx wrangler kv namespace create STATS`
2. **更新 wrangler.toml**：添加 STATS KV 配置
3. **创建 API**：`/api/stats/views.ts` 和 `/api/stats/downloads.ts`
4. **修改 CommonCard.astro**：添加浏览量角标
5. **修改 HeroCard.astro**：添加浏览量角标
6. **修改 DownloadAllImages.astro**：添加下载量显示 + 上报逻辑
7. **修改 [...slug].astro**：添加浏览量上报脚本
8. **本地测试**：`npm run dev` 验证
9. **构建部署**：`npm run build` + `wrangler pages deploy`
10. **验证线上**：检查 KV 数据和页面展示

---

## 11. 未来扩展

### 11.1 热门博文排行

基于浏览量数据，可以实现：
- 首页"热门博文"板块
- 侧边栏"热门推荐"
- 独立的排行榜页面

### 11.2 管理后台

创建 `/admin/stats` 页面，展示：
- 全站浏览量趋势
- 各博文浏览量排名
- 下载量排名
- 实时访问数据

### 11.3 数据迁移到 D1

如果 KV 写入量超出免费额度，可迁移到 Cloudflare D1（SQLite 数据库）：
- 支持事务和原子计数
- 支持复杂查询（排行、趋势等）
- 免费额度：5百万次读取/天 + 10万次写入/天
