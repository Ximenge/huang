# 91图图项目完整技术文档

## 一、项目概述

### 1.1 项目简介

本项目是一个基于 **Astro** 框架构建的二次元内容分享网站，主要提供 Cosplay 写真图片和视频内容的展示。网站采用现代化前端技术栈，部署于 **Cloudflare Pages** 平台，静态资源（图片、视频）存储于 **Cloudflare R2** 对象存储。

### 1.2 核心技术栈

| 类别 | 技术 |
|------|------|
| 前端框架 | Astro 5.5.2 |
| 样式方案 | Tailwind CSS 4.0 + DaisyUI 5.0 |
| 适配器 | @astrojs/cloudflare (Cloudflare Pages) |
| 图片处理 | Sharp |
| 视频播放 | HLS.js |
| 搜索功能 | PageFind |
| 内容管理 | Astro Content Collections (Markdown/MDX) |
| 部署平台 | Cloudflare Pages + Cloudflare R2 |
| 视频处理 | FFmpeg |
| 对象存储 | rclone (上传到 R2) |

### 1.3 目录结构

```
c:\huang\
├── astro-melody-starter/          # 主项目（Astro博客）
│   ├── src/
│   │   ├── components/            # Astro 组件
│   │   │   ├── AdWidget.astro         # 广告组件
│   │   │   ├── AdWidgetTriple.astro  # 三重广告组件
│   │   │   ├── BaseHead.astro         # 页面头部（SEO元数据）
│   │   │   ├── BottomAd.astro         # 底部广告
│   │   │   ├── CommonCard.astro       # 通用卡片组件
│   │   │   ├── ExoClickPopunder.astro # 弹窗广告
│   │   │   ├── Footer.astro           # 页脚
│   │   │   ├── FormattedDate.astro   # 日期格式化
│   │   │   ├── Header.astro          # 导航头部
│   │   │   ├── HeroCard.astro        # 英雄卡片
│   │   │   ├── Links.astro           # 链接组件
│   │   │   ├── OptimizedPicture.astro # 图片优化
│   │   │   ├── Pagination.astro       # 分页组件
│   │   │   ├── RelatedPostsCard.astro # 相关文章卡片
│   │   │   └── VideoCard.astro       # 视频卡片
│   │   ├── content/
│   │   │   ├── posts/                # 图片博文 (Markdown)
│   │   │   └── videos/               # 视频博文 (Markdown)
│   │   ├── layouts/
│   │   │   └── BaseLayout.astro      # 基础布局
│   │   ├── pages/                    # 页面路由
│   │   │   ├── api/
│   │   │   │   └── comments.ts       # 留言板API
│   │   │   ├── category/              # 分类页
│   │   │   ├── page/                  # 分页页
│   │   │   ├── posts/                 # 博文详情页
│   │   │   ├── tags/                  # 标签页
│   │   │   ├── videos/                # 视频页
│   │   │   ├── 404.astro             # 404页面
│   │   │   ├── guestbook.astro       # 留言板
│   │   │   ├── index.astro            # 首页
│   │   │   ├── rss.xml.js             # RSS订阅
│   │   │   ├── search.astro           # 搜索页
│   │   │   └── videos.astro           # 视频列表页
│   │   ├── assets/
│   │   │   └── app.css               # 全局样式
│   │   ├── consts.ts                 # 全局常量
│   │   └── middleware.ts              # 中间件（缓存、安全头）
│   ├── scripts/                       # 构建脚本
│   │   ├── r2_uploader.py            # R2上传脚本
│   │   └── video_processor.py        # 视频处理脚本
│   ├── public/                       # 静态资源
│   ├── astro.config.mjs              # Astro配置
│   ├── package.json                  # 依赖配置
│   ├── wrangler.toml                 # Cloudflare配置
│   ├── HLS_DEPLOYMENT.md             # HLS部署指南
│   └── R2_PROTECTION.md              # R2防护指南
│
├── Image/                            # 原始图片目录
│   └── [博主名] - [标题]/           # 图片文件夹
│       ├── *.jpg/png                 # 原始图片
│       └── post_metadata.json         # 元数据
│
├── Image-1/                          # 处理后的图片（WebP）
│   └── [博主名] - [标题]/
│       └── *.webp                    # 转换后的WebP图片
│
├── video/                            # 原始视频目录
│   └── [分组]/
│       └── [标题]/
│           └── *.mp4
│
├── video-1/                          # 处理后的视频（HLS）
│   └── [分组]/
│       └── [标题]/
│           ├── [视频名]/
│           │   ├── playlist.m3u8      # HLS播放列表
│           │   └── segment_*.ts       # 视频片段
│           ├── cover.jpg              # 视频封面
│           └── metadata.json          # 元数据
│
├── Python脚本/
│   ├── convert_to_webp_size_optimized.py    # 图片转WebP
│   ├── add_metadata_tags.py                # 添加元数据
│   ├── upload_to_r2.py                     # 上传图片到R2
│   ├── generate_markdown.py                 # 生成图片博文
│   ├── video_processor.py                   # 视频转HLS
│   ├── upload_video_to_r2.py               # 上传视频到R2
│   ├── generate_video_posts.py              # 生成视频博文
│   └── update_blog_record.py                # 更新博客记录
│
└── 配置文件/
    ├── wrangler.jsonc                       # Cloudflare Workers配置
    ├── wrangler.toml                        # Cloudflare Pages配置
    └── .gitignore                          # Git忽略配置
```

---

## 二、环境配置

### 2.1 基础环境要求

| 工具 | 版本要求 | 用途 |
|------|----------|------|
| Node.js | >= 18.0.0 | 运行 Astro |
| pnpm | >= 8.0.0 | 包管理工具 |
| Python | >= 3.8 | 运行脚本 |
| FFmpeg | 最新版 | 视频处理 |
| rclone | 最新版 | R2上传 |

### 2.2 安装步骤

#### 2.2.1 安装 Node.js 和 pnpm

```powershell
# 安装 Node.js (推荐使用 nvm 或直接下载安装)
# https://nodejs.org/

# 安装 pnpm
npm install -g pnpm
```

#### 2.2.2 安装 Python 依赖

```powershell
# 安装 Python (如果未安装)
# https://www.python.org/downloads/

# 安装项目所需Python库
pip install pypinyin pillow requests
```

#### 2.2.3 安装 FFmpeg

```powershell
# Windows: 下载 FFmpeg 并添加到 PATH
# https://ffmpeg.org/download.html

# 验证安装
ffmpeg -version
```

#### 2.2.4 安装和配置 rclone

```powershell
# 下载 rclone
# https://rclone.org/downloads/

# 初始化配置
rclone config

# 配置 Cloudflare R2 示例:
# n) New remote
# name> r2
# 4 / Amazon S3 (Compatible)
#   AWS_ACCESS_KEY_ID: (输入 R2 的 Access Key)
#   AWS_SECRET_ACCESS_KEY: (输入 R2 的 Secret Key)
#   endpoint> https://pub-58906530c3a643c1b5d1101b21b03114.r2.cloudflarestorage.com
#   location_constraint> 
#   acl> 
```

#### 2.2.5 安装项目依赖

```powershell
cd c:\huang\astro-melody-starter
pnpm install
```

---

## 三、项目运行

### 3.1 开发环境运行

```powershell
cd c:\huang\astro-melody-starter
pnpm run dev
```

访问地址: http://localhost:4321

### 3.2 生产环境构建

```powershell
cd c:\huang\astro-melody-starter
pnpm run build
```

构建输出: `dist/` 目录

### 3.3 预览构建结果

```powershell
cd c:\huang\astro-melody-starter
pnpm run preview
```

---

## 四、内容发布流程

本项目支持两种类型的内容发布：**图片博文** 和 **视频博文**。

### 4.1 图片博文发布流程

#### 步骤1: 准备原始图片

将图片放入 `c:\huang\Image\` 目录，按博文标题创建文件夹：

```
c:\huang\Image\
└── 眼镜妹/
    ├── photo_001.jpg
    ├── photo_002.png
    └── ...
```

#### 步骤2: 转换为 WebP 格式

```powershell
cd c:\huang\Image
python convert_to_webp_size_optimized.py
```

**脚本功能**:
- 遍历 `Image/` 目录下的所有子文件夹
- 将图片转换为 WebP 格式
- 目标文件大小: 200KB 以下
- 最大分辨率: 1440px (保持原始比例)
- 自动调整质量和分辨率以优化文件大小
- 输出到 `Image-1/` 目录
- 记录转换历史到 `conversion_record.json`

#### 步骤3: 添加元数据文件

```powershell
cd c:\huang\Image
python add_metadata_tags.py
```

**脚本功能**:
- 遍历 `Image/` 目录下的所有子文件夹
- 检查每个文件夹是否已存在 `post_metadata.json` 文件
- 如果不存在，自动创建元数据文件:

```json
{
  "category": "R18",
  "tags": ["眼镜妹", "Cosplay"]
}
```

#### 步骤4: 上传到 R2 存储

```powershell
cd c:\huang\Image-1
python upload_to_r2.py
```

**脚本功能**:
- 遍历 `Image-1/` 目录下的所有文件夹
- 使用 rclone 上传到 Cloudflare R2 存储
- 远程路径: `small/image/[文件夹名]/`
- R2 公开访问地址: `https://image.91tutu.cc/[文件夹名]/`

#### 步骤5: 生成博文 Markdown 文件

```powershell
cd c:\huang\Image-1
python generate_markdown.py
```

**脚本功能**:
- 遍历 `Image-1/` 目录下的所有文件夹
- 为每个文件夹生成对应的 `.md` 文件
- 输出到 `astro-melody-starter/src/content/posts/`
- 自动跳过已存在的博文

**生成的 Markdown 格式**:

```markdown
---
author: Image Gallery
category:
- Gallery
cover: https://image.91tutu.cc/眼镜妹/photo_001.webp
coverAlt: 眼镜妹 gallery image
description: 眼镜妹 Cosplay 写真集
pubDate: 2026-03-15 12:00:00
tags:
- images
- gallery
title: 眼镜妹
---

# 眼镜妹

![photo_001.webp](https://image.91tutu.cc/眼镜妹/photo_001.webp)
...
```

#### 步骤6: 验证发布

开发环境下，刷新页面即可看到新博文（无需重启）:
- 首页: http://localhost:4321/
- 分类页: http://localhost:4321/category/Gallery/1/

---

### 4.2 视频博文发布流程

#### 步骤1: 准备原始视频

将视频放入 `c:\huang\video\` 目录，按分组和博文标题组织:

```
c:\huang\video\
└── 紧急企划/                    # 视频分组
    └── 测试视频/                # 博文标题
        ├── video1.mp4
        └── video2.mp4
```

**支持的格式**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.wmv`

#### 步骤2: 转换为 HLS 格式

```powershell
cd c:\huang
python video_processor.py
```

**脚本功能**:
- 遍历 `video/` 目录下的所有分组和博文
- 使用 FFmpeg 将视频转换为 HLS 格式
- 视频编码: H.264
- 音频编码: AAC
- 分辨率限制: 1080P
- 切片时长: 10秒
- 输出 `.m3u8` 播放列表和 `.ts` 视频片段
- 自动提取视频封面（第1秒的画面）
- 生成 `metadata.json` 元数据文件
- 输出到 `video-1/` 目录

**输出结构**:

```
video-1/
└── 紧急企划/
    └── 测试视频/
        ├── 视频1/
        │   ├── playlist.m3u8
        │   ├── segment_000.ts
        │   └── ...
        ├── 视频2/
        │   └── ...
        ├── 视频1_cover.jpg
        └── metadata.json
```

#### 步骤3: 上传到 R2 存储

```powershell
cd c:\huang
python upload_video_to_r2.py
```

**脚本功能**:
- 遍历 `video-1/` 目录下的所有分组和博文
- 使用 rclone 上传到 Cloudflare R2
- 远程路径: `small/video/[分组]/[标题]/`
- R2 公开访问地址: `https://video.91tutu.cc/`
- 防止重复上传（通过 `video_upload_record.json` 记录）

#### 步骤4: 生成博文 Markdown 文件

```powershell
cd c:\huang
python generate_video_posts.py
```

**脚本功能**:
- 遍历 `video-1/` 目录下的所有分组和博文
- 读取 `metadata.json` 获取视频信息
- 生成 `.md` 文件到 `src/content/videos/[分组]/`
- 视频路径使用 R2 公开地址

**生成的 Markdown 格式**:

```markdown
---
title: 测试视频
series: 紧急企划
description: 测试视频 - 2个视频
pubDate: "2026-03-15"
videoCount: 2
videos:
  - name: "视频1"
    hlsUrl: https://video.91tutu.cc/紧急企划/测试视频/视频1/playlist.m3u8
  - name: "视频2"
    hlsUrl: https://video.91tutu.cc/紧急企划/测试视频/视频2/playlist.m3u8
---
```

#### 步骤5: 部署到生产环境

```powershell
cd c:\huang\astro-melody-starter

# 构建
npm run build

# 部署到 Cloudflare Pages (main 分支)
npx wrangler pages deploy dist --branch=main
```

#### 步骤6: 验证发布

- 视频列表页: http://localhost:4321/videos/
- 视频分组页: http://localhost:4321/videos/紧急企划/
- 视频详情页: http://localhost:4321/videos/紧急企划/测试视频/

---

## 五、部署指南

### 5.1 Cloudflare Pages 部署

#### 5.1.1 创建 Cloudflare 账户

1. 访问 https://cloudflare.com 注册账户
2. 完成邮箱验证

#### 5.1.2 创建 Pages 项目

1. 登录 Cloudflare Dashboard
2. 进入 "Pages" 页面
3. 点击 "创建项目"
4. 连接 Git 仓库或直接上传

#### 5.1.3 配置部署

```
项目名称: astro-melody-starter
生产分支: main
构建命令: npm run build
构建输出目录: dist
```

#### 5.1.4 绑定 R2 存储桶

在 Cloudflare Dashboard 中:
1. 进入 "R2" -> "管理 API 令牌"
2. 创建 API 令牌，授予 R2 读写权限
3. 在 Pages 项目的 "设置" -> "环境变量" 中添加:
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`

### 5.2 域名配置

1. 在 Cloudflare 添加自定义域名
2. 配置 DNS 解析指向 Pages
3. 启用 HTTPS (自动由 Cloudflare 提供)

### 5.3 R2 存储桶配置

#### 5.3.1 创建 R2 存储桶

1. 进入 Cloudflare Dashboard -> "R2"
2. 创建存储桶: `astro-melody-media`
3. 设置公共访问域: `image.91tutu.cc`

#### 5.3.2 配置 CORS

在存储桶设置中添加 CORS 策略:
```json
[
  {
    "AllowedOrigins": ["https://91tutu.cc"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"]
  }
]
```

### 5.4 wrangler.toml 配置说明

```toml
name = "astro-melody-starter"
compatibility_date = "2024-01-01"
pages_build_output_dir = "dist"

[build]
command = "npm run build"
cwd = "."
watch_dir = "src"

[build.upload]
format = "modules"
main = "./dist/_worker.js"

[[kv_namespaces]]
binding = "GUESTBOOK"
id = "98545db89c3a4b0191d8daff2471ae87"
```

---

## 六、核心组件说明

### 6.1 页面组件

| 组件 | 文件路径 | 功能说明 |
|------|----------|----------|
| BaseHead | `src/components/BaseHead.astro` | 页面头部，包含SEO元数据、Open Graph、Twitter Card、JSON-LD结构化数据、Google Analytics等 |
| Header | `src/components/Header.astro` | 导航头部，包含网站Logo、导航链接、搜索入口 |
| Footer | `src/components/Footer.astro` | 页脚，包含版权信息、社交链接 |
| CommonCard | `src/components/CommonCard.astro` | 通用卡片组件，用于展示图片/视频预览 |
| HeroCard | `src/components/HeroCard.astro` | 英雄卡片，用于首页大图展示 |
| VideoCard | `src/components/VideoCard.astro` | 视频卡片，用于视频列表展示 |
| Pagination | `src/components/Pagination.astro` | 分页组件，支持上下页跳转 |
| AdWidget | `src/components/AdWidget.astro` | 广告组件 |
| ExoClickPopunder | `src/components/ExoClickPopunder.astro` | 弹窗广告组件 |

### 6.2 页面路由

| 路由 | 文件 | 功能 |
|------|------|------|
| `/` | `index.astro` | 首页，展示最新博文 |
| `/posts/[...slug]` | `posts/[...slug].astro` | 博文详情页 |
| `/category/[category]/[page]` | `category/[category]/[page].astro` | 分类页 |
| `/tags/[tag]/[page]` | `tags/[tag]/[page].astro` | 标签页 |
| `/page/[page]` | `page/[page].astro` | 分页列表页 |
| `/videos` | `videos.astro` | 视频列表页 |
| `/videos/[series]` | `videos/[series]/index.astro` | 视频分组页 |
| `/videos/[series]/[slug]` | `videos/[series]/[slug].astro` | 视频详情页 |
| `/search` | `search.astro` | 搜索页面 |
| `/guestbook` | `guestbook.astro` | 留言板 |
| `/rss.xml` | `rss.xml.js` | RSS 订阅源 |
| `/robots.txt` | `robots.txt.ts` | robots.txt |

### 6.3 内容集合配置

项目使用 Astro Content Collections 管理内容:

```typescript
// src/content/config.ts

// 图片博文集合
const posts = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "src/content/posts" }),
  schema: z.object({
    title: z.string(),              // 标题
    pubDate: z.date(),              // 发布日期
    description: z.string(),        // 描述
    cover: z.string(),               // 封面图
    coverAlt: z.string(),           // 封面图描述
    category: z.array(z.string()),   // 分类
    tags: z.array(z.string()),      // 标签
  }),
});

// 视频博文集合
const videos = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "src/content/videos" }),
  schema: z.object({
    title: z.string(),              // 标题
    series: z.string(),              // 视频系列
    description: z.string(),         // 描述
    videoCount: z.number(),          // 视频数量
    videos: z.array(z.object({       // 视频列表
      name: z.string(),
      hlsUrl: z.string(),
    })),
  }),
});
```

### 6.4 中间件功能

`src/middleware.ts` 实现以下功能:

1. **安全头设置**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Permissions-Policy: geolocation=(), microphone=()`

2. **缓存策略**
   - 静态资源 (图片/视频/CSS/JS): 缓存1年
   - 其他页面: 缓存1小时

3. **搜索引擎识别**
   - 识别爬虫 User-Agent
   - 爬虫不展示广告（防止搜索引擎惩罚）

---

## 七、视频播放实现

### 7.1 HLS 视频流

项目使用 HLS (HTTP Live Streaming) 技术实现视频播放:

1. **视频切片**: 使用 FFmpeg 将视频分割为多个 `.ts` 文件
2. **播放列表**: 生成 `.m3u8` 播放列表文件
3. **播放器**: 使用 HLS.js 在浏览器中播放

### 7.2 视频播放器组件

```javascript
// 前端播放器初始化
const hls = new Hls({
  debug: false,
  enableWorker: true,
  lowLatencyMode: true,
  backBufferLength: 90
});

// 加载视频
hls.loadSource(hlsUrl);
hls.attachMedia(videoElement);

// 播放器事件处理
hls.on(Hls.Events.MANIFEST_PARSED, () => {
  videoElement.play();
});
```

### 7.3 视频元数据结构

```json
{
  "group_name": "紧急企划",
  "post_title": "测试视频",
  "video_count": 2,
  "cover": "视频1_cover.jpg",
  "videos": [
    {
      "name": "视频1",
      "original_file": "video1.mp4",
      "size": 12345678,
      "duration": 120.5,
      "width": 1920,
      "height": 1080,
      "codec": "h264",
      "hls_playlist": "视频1/playlist.m3u8"
    }
  ]
}
```

---

## 八、广告系统

本项目集成了多个广告平台，采用多种广告形式实现收益。

### 8.1 广告平台

| 广告平台 | 类型 | 广告形式 | 组件文件 |
|----------|------|----------|----------|
| ExoClick (magsrv.com) | 广告联盟 | 侧边栏图文广告 | `src/components/AdWidget.astro` |
| ExoClick (pemsrv.com) | 广告联盟 | 弹窗广告 (Popunder) | `src/components/ExoClickPopunder.astro` |
| ExoClick (magsrv.com) | 广告联盟 | 底部悬浮广告 | `src/components/BottomAd.astro` |
| Google Analytics | 数据分析 | 网站分析 | `src/components/BaseHead.astro` |
| 自定义 | 原生广告 | 内容卡片式广告 | `src/components/AdWidgetTriple.astro` |

---

### 8.2 广告相关文件清单

本项目的广告系统涉及以下核心文件：

| 文件路径 | 行数 | 功能描述 | 被引用位置 |
|----------|------|----------|------------|
| `src/components/AdWidget.astro` | 118 | 侧边栏横向广告组件 | 6个页面 |
| `src/components/AdWidgetTriple.astro` | 153 | 内容卡片式伪装广告组件 | 6个页面 |
| `src/components/ExoClickPopunder.astro` | ~350 | 弹窗广告组件 | 仅 `BaseLayout.astro` |
| `src/components/BottomAd.astro` | 121 | 底部悬浮广告组件 | 仅 `BaseLayout.astro` |
| `src/components/BaseHead.astro` | 75 | 页面头部（含Google Analytics） | 所有页面 |
| `src/layouts/BaseLayout.astro` | 180 | 基础布局（含年龄验证） | 所有页面 |
| `public/popunder.js` | ~150 | 本地弹窗广告备用脚本 | 未被引用 |

---

### 8.3 AdWidget 组件详解（侧边栏横向广告）

#### 8.3.1 文件信息

| 项目 | 内容 |
|------|------|
| 文件路径 | `src/components/AdWidget.astro` |
| 总行数 | 118 行 |
| 广告联盟 | ExoClick (magsrv.com) |
| 广告位ID | 5863494 |
| 广告尺寸 | 352px × 300px |

#### 8.3.2 核心代码结构

```astro
---
// AdWidget.astro - 横向广告组件
---

<!-- 广告容器 -->
<div class="ad-box relative shadow-xl rounded-xl overflow-hidden transition-transform duration-500 hover:-translate-y-1 hover:scale-105">
  
  <!-- 第1步: 加载广告提供商脚本 -->
  <script is:inline async type="application/javascript" src="https://a.magsrv.com/ad-provider.js"></script>
  
  <!-- 第2: 定义广告位容器 (ins标签是广告联盟标准) -->
  <ins class="eas6a97888e20" data-zoneid="5863494"></ins>
  
  <!-- 第3: 初始化广告请求 -->
  <script is:inline>(AdProvider = window.AdProvider || []).push({"serve": {}});</script>
  
</div>

<!-- 广告样式 -->
<style>
  /* 固定尺寸容器 */
  .ad-box {
    width: 352px !important;
    height: 300px !important;
    max-width: 100% !important;
    position: relative !important;
    overflow: hidden !important;
  }
  
  /* ins标签占满容器 */
  .ad-box > ins.eas6a97888e20 {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
  }
  
  /* 隐藏广告商生成的头部 */
  .eas6a97888e20 .exo-native-widget-header {
    display: none !important;
  }
  /* ... 更多样式见原文件 */
</style>
```

#### 8.3.3 代码作用解析

| 代码部分 | 作用 | 关键参数 |
|----------|------|----------|
| `src="https://a.magsrv.com/ad-provider.js"` | 加载 ExoClick 广告联盟 SDK | - |
| `<ins class="eas6a97888e20" data-zoneid="5863494">` | 定义广告展示容器，zoneid 标识广告位 | zoneid=5863494 |
| `(AdProvider = window.AdProvider \|\| []).push({"serve": {}})` | 向广告队列添加请求，触发广告加载 | - |
| `.ad-box` 样式 | 固定容器尺寸，防止布局偏移 | 352×300px |
| `.eas6a97888e20 .exo-native-widget-header { display: none }` | 隐藏广告商默认头部，提升美观 | - |

#### 8.3.4 依赖关系图

```
AdWidget.astro
    │
    ├── 依赖外部资源:
    │   └── https://a.magsrv.com/ad-provider.js (广告联盟SDK)
    │
    ├── 被以下文件引用 (import):
    │   ├── src/pages/index.astro
    │   ├── src/pages/page/[page].astro
    │   ├── src/pages/category/[category]/[page].astro
    │   ├── src/pages/tags/[tag]/[page].astro
    │   ├── src/pages/videos.astro
    │   └── src/pages/videos/[series]/index.astro
    │
    └── 在页面中的使用方式:
        <AdWidget />
```

#### 8.3.5 调用示例（以 index.astro 为例）

```astro
<!-- src/pages/index.astro -->
---
import AdWidget from "@components/AdWidget.astro";
import AdWidgetTriple from "@components/AdWidgetTriple.astro";
---

<!-- 在页面中使用广告组件 -->
<AdWidgetTriple posts={allPosts} />

<!-- 或直接使用单个广告组件 -->
<AdWidget />
```

---

### 8.4 AdWidgetTriple 组件详解（内容卡片式伪装广告）

#### 8.4.1 文件信息

| 项目 | 内容 |
|------|------|
| 文件路径 | `src/components/AdWidgetTriple.astro` |
| 总行数 | 153 行 |
| 广告联盟 | ExoClick (magsrv.com) |
| 广告位ID | 5863494 (与 AdWidget 相同) |
| 广告数量 | 3个卡片 |

#### 8.4.2 核心代码结构

```astro
---
import type { CollectionEntry } from "astro:content";
import FormattedDate from "@components/FormattedDate.astro";

interface Props {
  posts?: CollectionEntry<"posts">[];
}

const { posts = [] } = Astro.props;

// 将文章数据转换为轻量级对象
const postsData = posts.map(post => ({
  id: post.id,
  cover: post.data.cover,
  coverAlt: post.data.coverAlt,
  tags: post.data.tags,
  pubDate: post.data.pubDate,
  title: post.data.title
}));
---

<!-- 循环生成3个广告卡片 -->
{[1, 2, 3].map((_, index) => (
  <!-- 广告层: 加载真实广告 -->
  <div class="ad-box relative h-[300px]...">
    <div class="ad-layer absolute inset-0 z-0">
      <script is:inline src="https://a.magsrv.com/ad-provider.js"></script>
      <ins class="eas6a97888e20" data-zoneid="5863494"></ins>
      <script is:inline>(AdProvider = window.AdProvider || []).push({"serve": {}});</script>
    </div>
    
    <!-- 内容层: 覆盖真实文章内容 (伪装) -->
    <div class="content-layer absolute inset-0 z-10 pointer-events-none">
      <figure class="h-full">
        <img class="ad-cover h-full w-full object-cover" src="" alt="" />
      </figure>
      <div class="absolute bottom-0...">
        <div class="ad-tags..."></div>
        <p class="ad-date..."></p>
        <h3 class="ad-title..."></h3>
      </div>
    </div>
  </div>
))}

<!-- 客户端脚本: 动态填充伪装内容 -->
<script define:vars={{ postsData }}>
  // 随机打乱文章顺序
  function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  // 更新广告卡片内容
  function updateAdBoxes() {
    const adBoxes = document.querySelectorAll('.ad-box');
    const randomPosts = shuffleArray(postsData).slice(0, 3);  // 随机选3篇
    
    adBoxes.forEach((box, index) => {
      const post = randomPosts[index];
      // 用真实文章内容替换广告卡片内容
      box.querySelector('.ad-cover').src = post.cover;
      box.querySelector('.ad-title').textContent = post.title;
      // ... 更多替换
    });
  }

  document.addEventListener('DOMContentLoaded', updateAdBoxes);
</script>
```

#### 8.4.3 代码作用解析

| 代码部分 | 作用 | 详细说明 |
|----------|------|----------|
| `interface Props { posts?: CollectionEntry<"posts">[] }` | 定义组件props | 接收页面传入的文章列表 |
| `posts.map(post => ({...}))` | 提取文章数据 | 只提取需要的数据，减少传递大小 |
| `{[1,2,3].map(...)}` | 循环生成3个广告 | 广告卡片数量固定为3 |
| `ad-layer` (z-0) | 广告层 | 底层加载真实广告 |
| `content-layer` (z-10) | 内容层 | 上层覆盖伪装内容 |
| `pointer-events-none` | 穿透点击 | 让点击穿透到下层广告 |
| `shuffleArray(postsData)` | 随机排序 | 每次页面加载显示不同文章 |
| `.slice(0, 3)` | 取前3篇 | 作为广告伪装内容 |

#### 8.4.4 伪装原理图

```
┌─────────────────────────────────────┐
│         广告卡片容器                  │
│  ┌─────────────────────────────────┐│
│  │     content-layer (z-10)        ││  ← 上层: 显示伪装内容
│  │  ┌───────────────────────────┐  ││      (真实文章标题、封面)
│  │  │     真实文章封面图片        │  ││
│  │  │     真实文章标题           │  ││
│  │  │     真实文章标签           │  ││
│  │  └───────────────────────────┘  ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │       ad-layer (z-0)           ││  ← 下层: 加载真实广告
│  │  ┌───────────────────────────┐  ││      (ExoClick 广告)
│  │  │  <ins data-zoneid=5863494> │  ││
│  │  └───────────────────────────┘  ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
       ↓ 点击穿透 (pointer-events-none)
       实际点击广告，跳转到广告链接
```

#### 8.4.5 依赖关系图

```
AdWidgetTriple.astro
    │
    ├── 依赖:
    │   ├── @components/FormattedDate.astro (日期格式化)
    │   ├── astro:content (类型定义)
    │   └── https://a.magsrv.com/ad-provider.js (广告SDK)
    │
    ├── 接收props:
    │   └── posts: CollectionEntry<"posts">[]  (文章列表)
    │
    ├── 被以下文件引用 (import):
    │   ├── src/pages/index.astro
    │   ├── src/pages/page/[page].astro
    │   ├── src/pages/category/[category]/[page].astro
    │   ├── src/pages/tags/[tag]/[page].astro
    │   ├── src/pages/videos.astro
    │   └── src/pages/videos/[series]/index.astro
    │
    └── 调用示例:
        <AdWidgetTriple posts={allPosts} />
```

#### 8.4.6 调用示例（以 page/[page].astro 为例）

```astro
<!-- src/pages/page/[page].astro -->
---
import AdWidget from "@components/AdWidget.astro";
import AdWidgetTriple from "@components/AdWidgetTriple.astro";

// 获取所有文章
const allPosts = await getCollection("posts");
// ... 排序和分页逻辑
---

<main>
  <!-- 在文章网格上方插入广告 -->
  <AdWidgetTriple posts={allPosts} />
  
  <!-- 文章网格 -->
  <div class="grid...">
    {allPosts.map((post) => (
      <CommonCard post={post} />
    ))}
  </div>
  
  <!-- 在文章网格下方插入广告 -->
  <AdWidgetTriple posts={allPosts} />
</main>
```

---

### 8.5 ExoClickPopunder 组件详解（弹窗广告）

#### 8.5.1 文件信息

| 项目 | 内容 |
|------|------|
| 文件路径 | `src/components/ExoClickPopunder.astro` |
| 总行数 | ~350 行 (压缩后的商业SDK代码) |
| 广告联盟 | ExoClick/pemsrv.com |
| 广告位ID | 5866630 |
| 触发方式 | 用户点击时触发 |

#### 8.5.2 核心代码结构

```astro
---
// ExoClickPopunder.astro - 弹窗广告组件
---

<!-- 直接嵌入 ExoClick 官方 SDK 代码 -->
<script type="application/javascript">
// ExoClick Popunder SDK (版本 8.0.0)
// 代码经过压缩和混淆

(function() {
    // 广告配置
    var adConfig = {
        "ads_host": "a.pemsrv.com",        // 广告服务器
        "syndication_host": "s.pemsrv.com", // 同步服务器
        "idzone": 5866630,                  // 广告位ID
        "frequency_period": 60,             // 频率周期 (分钟)
        "frequency_count": 1,               // 周期内最多显示次数
        "trigger_method": 1,                // 触发方式: 1=点击触发
        "chrome_enabled": true,             // Chrome启用
        "popup_force": false,               // 不强制弹窗
        "popup_fallback": false,            // 不使用回退
        "capping_enabled": true,            // 启用频率限制
        "tcf_enabled": true,               // 启用GDPR同意
        "new_tab": false,                   // 当前窗口打开
    };
    
    // ... 更多SDK初始化代码 ...
    
    // 核心弹窗逻辑
    var popMagic = {
        version: 8,
        
        // 检测广告域是否授权
        isAdsDomainLicensed: function() {
            var licensedDomains = [
                "exdynsrv.com","exosrv.com","exoclick.com",
                "opoxv.com","exacdn.com","pemsrv.com"
            ];
            // 检查当前域名是否在授权列表
            // ...
        },
        
        // 初始化
        init: function(config) {
            // 配置合并
            // 检查TCF同意
            // 加载广告脚本
        },
        
        // 准备弹窗
        preparePopWait: function() {
            // 监听用户点击事件
            document.addEventListener('click', function(e) {
                // 触发弹窗
                popMagic.openPop();
            });
        },
        
        // 打开弹窗
        openPop: function() {
            // 检查频率限制
            // 创建弹窗
            // 加载广告内容
        }
    };
    
    // 启动
    popMagic.init(adConfig);
})();
</script>
```

#### 8.5.3 代码作用解析

| 代码部分 | 作用 | 关键参数 |
|----------|------|----------|
| `adConfig` 对象 | 广告配置参数 | 包含广告位、频率、触发方式等 |
| `idzone: 5866630` | 广告位标识 | ExoClick 分配的唯一ID |
| `frequency_period: 60` | 频率周期 | 60分钟内不重复显示 |
| `frequency_count: 1` | 显示次数 | 每个周期最多显示1次 |
| `trigger_method: 1` | 触发方式 | 1=点击触发, 2=页面加载触发 |
| `capping_enabled: true` | 频率限制 | 防止广告疲劳 |
| `tcf_enabled: true` | GDPR合规 | 启用TCF同意框架 |
| `isAdsDomainLicensed()` | 域名授权检查 | 确保广告在授权域名显示 |
| `preparePopWait()` | 事件监听 | 监听用户点击行为 |
| Cookie `popunder_cap_5866630` | 频率记录 | 记录用户已看广告次数 |

#### 8.5.4 弹窗触发流程图

```
用户访问页面
      │
      ↓
ExoClickPopunder 组件加载
      │
      ↓
popMagic.init(adConfig) 初始化
      │
      ↓
准备弹窗监听器 preparePopWait()
      │
      ↓
      ┌──────────────────────────────────────┐
      │         等待用户点击页面              │
      └──────────────────────────────────────┘
              │
              ↓ 点击
      ┌──────────────────────────────────────┐
      │  1. 检查 Cookie (popunder_cap_5866630)│
      │  2. 检查是否在授权域名               │
      │  3. 检查TCF同意状态                  │
      └──────────────────────────────────────┘
              │
              ↓ 全部通过
      ┌──────────────────────────────────────┐
      │  创建隐藏的弹窗iframe                 │
      │  加载广告: a.pemsrv.com/ads?zone=5866630│
      └──────────────────────────────────────┘
              │
              ↓
      ┌──────────────────────────────────────┐
      │  在当前页面底部打开广告               │
      │  (或新标签页，取决于配置)             │
      └──────────────────────────────────────┘
              │
              ↓
      记录Cookie: frequency_period=60分钟内不重复
```

#### 8.5.5 依赖关系图

```
ExoClickPopunder.astro
    │
    ├── 依赖外部资源:
    │   ├── a.pemsrv.com (广告服务器)
    │   └── s.pemsrv.com (同步服务器)
    │
    ├── 无import依赖 (纯客户端SDK)
    │
    ├── 被引用位置:
    │   └── src/layouts/BaseLayout.astro (第6行 import, 第45行使用)
    │
    └── 调用链路:
        BaseLayout.astro
            │
            ├── isBot 检测 (爬虫不显示)
            │
            └── {!isBot && <ExoClickPopunder />}
                    │
                    └── 页面所有路由都会加载
```

#### 8.5.6 BaseLayout.astro 中的集成代码

```astro
<!-- src/layouts/BaseLayout.astro -->
---
import ExoClickPopunder from "@components/ExoClickPopunder.astro";

// 爬虫检测
const userAgent = Astro.request.headers.get('user-agent') || '';
const botUserAgents = ['googlebot','bingbot','slurp','baiduspider',...];
const isBot = botUserAgents.some(bot => userAgent.toLowerCase().includes(bot));
---

<html>
  <body>
    <!-- 爬虫不加载弹窗广告 -->
    {!isBot && <ExoClickPopunder />}
    
    <!-- 页面内容 -->
    <slot />
  </body>
</html>
```

---

### 8.6 BottomAd 组件详解（底部悬浮广告）

#### 8.6.1 文件信息

| 项目 | 内容 |
|------|------|
| 文件路径 | `src/components/BottomAd.astro` |
| 总行数 | 121 行 |
| 广告联盟 | ExoClick (magsrv.com) |
| 广告位ID | 5863710 |
| 广告尺寸 | 300px × 100px |
| 位置 | 页面底部固定悬浮 |

#### 8.6.2 核心代码结构

```astro
---
// BottomAd.astro - 底部悬浮广告组件
---

<!-- 广告容器，默认隐藏 -->
<div id="bottomAdContainer" class="bottom-ad-wrapper hidden">
  
  <!-- 加载广告SDK -->
  <script is:inline async type="application/javascript" src="https://a.magsrv.com/ad-provider.js"></script>
  
  <!-- 广告位容器 -->
  <ins class="eas6a97888e17" data-zoneid="5863710" data-block-ad-types="92,45"></ins>
  
  <!-- 初始化广告 -->
  <script is:inline>(AdProvider = window.AdProvider || []).push({"serve": {}});</script>
  
</div>

<!-- 客户端脚本: 控制广告显示时机 -->
<script type="module">
  (function() {
    const adContainer = document.getElementById('bottomAdContainer');
    
    // 显示广告函数
    function showAd() {
      if (adContainer) {
        adContainer.classList.remove('hidden');
      }
    }
    
    // 初始化函数
    function init() {
      // 检查年龄验证弹窗是否显示
      const ageModal = document.getElementById('ageVerificationModal');
      const isAgeVerificationVisible = ageModal && !ageModal.classList.contains('hidden');
      
      if (isAgeVerificationVisible) {
        // 监听年龄验证关闭事件
        const observer = new MutationObserver(function(mutations) {
          mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
              if (ageModal.classList.contains('hidden')) {
                showAd();          // 弹窗关闭后显示广告
                observer.disconnect();
              }
            }
          });
        });
        observer.observe(ageModal, { attributes: true });
      } else {
        // 延迟1秒后显示广告
        setTimeout(showAd, 1000);
      }
    }
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
    
    // Astro 页面导航后重新显示 (SPA行为支持)
    document.addEventListener('astro:page-load', function() {
      setTimeout(function() {
        const ageModal = document.getElementById('ageVerificationModal');
        const isAgeVerificationVisible = ageModal && !ageModal.classList.contains('hidden');
        
        if (!isAgeVerificationVisible) {
          showAd();
        }
      }, 500);
    });
  })();
</script>

<!-- 样式 -->
<style>
  /* 底部固定定位 */
  .bottom-ad-wrapper [id^="exo-mobile-im-container-wrapper"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100%;
    z-index: 1999900 !important;
  }
  
  /* 关闭按钮 */
  .bottom-ad-wrapper [id^="exo-mobile-im-close-button"] {
    position: absolute;
    z-index: 1999999 !important;
    cursor: pointer;
  }
</style>
```

#### 8.6.3 代码作用解析

| 代码部分 | 作用 | 详细说明 |
|----------|------|----------|
| `<ins class="eas6a97888e17" data-zoneid="5863710">` | 广告位容器 | zoneid标识底部广告位 |
| `data-block-ad-types="92,45"` | 阻止特定广告 | 屏蔽某些类型广告 |
| `class="hidden"` | 默认隐藏 | 等待合适时机显示 |
| `showAd()` | 显示广告 | 移除hidden类 |
| `setTimeout(showAd, 1000)` | 延迟显示 | 页面加载1秒后显示 |
| `MutationObserver` | 监听DOM变化 | 检测年龄验证弹窗关闭 |
| `astro:page-load` | Astro导航事件 | SPA页面切换后重新显示 |
| `position: fixed; bottom: 0` | 底部固定 | 始终显示在页面底部 |

#### 8.6.4 显示时机流程图

```
页面加载
    │
    ├─────────────────────────────────────────────┐
    │  检查年龄验证弹窗状态                        │
    │  (ageVerificationModal 是否可见)             │
    └─────────────────────────────────────────────┘
           │
     ┌──────┴──────┐
     ↓             ↓
  弹窗显示中      弹窗已关闭
     │             │
     ↓             ↓
  监听弹窗      延迟1秒
  关闭事件      显示广告
     │             
     ↓             
  弹窗关闭      
     │             
     ↓             
  显示底部广告
```

#### 8.6.5 依赖关系图

```
BottomAd.astro
    │
    ├── 依赖外部资源:
    │   └── https://a.magsrv.com/ad-provider.js
    │
    ├── 依赖DOM元素:
    │   └── #bottomAdContainer (自身容器)
    │   └── #ageVerificationModal (年龄验证弹窗)
    │
    ├── 被引用位置:
    │   └── src/layouts/BaseLayout.astro
    │
    └── 调用链路:
        BaseLayout.astro
            │
            ├── isBot 检测
            │
            ├── import BottomAd from "@components/BottomAd.astro"
            │
            └── {!isBot && <BottomAd />}
                    │
                    └── 页面底部显示广告
```

---

### 8.7 BaseHead 组件详解（Google Analytics 集成）

#### 8.7.1 文件信息

| 项目 | 内容 |
|------|------|
| 文件路径 | `src/components/BaseHead.astro` |
| 总行数 | 75 行 |
| Google Analytics ID | G-ZR2CF91PST |
| 广告相关功能 | 网站分析、用户行为追踪 |

#### 8.7.2 核心代码结构

```astro
---
// BaseHead.astro - 页面头部组件
import { META_TITLE } from "@consts";

interface Props {
  title?: string;
  description: string;
  image?: string;
}

const canonicalURL = new URL(Astro.url.pathname, Astro.site);
const { title = META_TITLE, description, image = "/blog-placeholder-1.avif" } = Astro.props;
---

<!-- 基础元数据 -->
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link rel="icon" type="image/x-icon" href="/favicon.ico" />

<!-- SEO: 规范链接 -->
<link rel="canonical" href={canonicalURL} />

<!-- SEO: 网站地图 -->
<link rel="sitemap" href="/sitemap-index.xml" />

<!-- SEO: 站点验证 -->
<meta name="yandex-verification" content="bcbbd1b4bad4398f" />
<meta name="6a97888e-site-verification" content="364a3efe6cb9c67e7515a8c3cd9cb721" />

<!-- 广告相关: Client Hints -->
<meta http-equiv="Delegate-CH" content="Sec-CH-UA https://s.magsrv.com; ..." />

<!-- ============== 广告/分析相关代码 ============== -->
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ZR2CF91PST"></script>
<script is:inline>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-ZR2CF91PST');
</script>

<!-- SEO: 页面标题和描述 -->
<title>{title}</title>
<meta name="title" content={title} />
<meta name="description" content={description} />

<!-- SEO: Open Graph (Facebook) -->
<meta property="og:type" content="website" />
<meta property="og:url" content={Astro.url} />
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={new URL(image, Astro.url)} />

<!-- SEO: Twitter Card -->
<meta property="twitter:card" content="summary_large_image" />
...

<!-- SEO: Schema.org JSON-LD -->
<script type="application/ld+json" set:html={JSON.stringify({
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": title,
  ...
})}></script>
```

#### 8.7.3 代码作用解析

| 代码部分 | 作用 | 详细说明 |
|----------|------|----------|
| `<script async src="gtag/js?id=G-ZR2CF91PST">` | 加载GA4脚本 | 异步加载不阻塞页面 |
| `window.dataLayer = window.dataLayer \|\| []` | 数据层 | 存储分析数据 |
| `gtag('config', 'G-ZR2CF91PST')` | 初始化配置 | 绑定跟踪ID |
| `<meta http-equiv="Delegate-CH">` | Client Hints | 向广告服务器传递客户端信息 |
| `<link rel="canonical">` | 规范URL | 防止重复内容问题 |
| `<meta name="yandex-verification">` | Yandex验证 | 搜索站长工具验证 |
| `<meta name="6a97888e-site-verification">` | 广告平台验证 | ExoClick/magsrv验证 |

#### 8.7.4 Google Analytics 工作原理

```
用户访问页面
      │
      ↓
加载 gtag.js
      │
      ↓
初始化 dataLayer
      │
      ↓
发送以下数据到 Google Analytics:
  - 页面浏览量
  - 用户设备信息
  - 用户地理位置
  - 页面停留时间
  - 点击事件 (如广告点击)
      │
      ↓
在 GA 后台查看:
  - 实时用户
  - 用户来源
  - 页面浏览量
  - 转化追踪
  - 广告收益报告
```

#### 8.7.5 依赖关系图

```
BaseHead.astro
    │
    ├── 依赖:
    │   ├── @consts (META_TITLE 常量)
    │   └── https://www.googletagmanager.com/gtag/js
    │
    ├── 被引用:
    │   └── src/layouts/BaseLayout.astro (所有页面基础布局)
    │
    └── 调用链路:
        任何页面
            ↓
        BaseLayout.astro
            ↓
        <BaseHead title={title} description={description} />
            ↓
        <head> 中插入:
            - GA分析代码
            - SEO元数据
            - 社交分享卡片
```

---

### 8.8 BaseLayout 组件详解（广告控制中心）

#### 8.8.1 文件信息

| 项目 | 内容 |
|------|------|
| 文件路径 | `src/layouts/BaseLayout.astro` |
| 总行数 | 180 行 |
| 核心功能 | 页面布局、广告控制、年龄验证 |

#### 8.8.2 核心代码结构

```astro
---
// BaseLayout.astro - 基础布局组件
import BaseHead from "@components/BaseHead.astro";
import Header from "@components/Header.astro";
import Footer from "@components/Footer.astro";
import BottomAd from "@components/BottomAd.astro";
import ExoClickPopunder from "@components/ExoClickPopunder.astro";

const { title, description } = Astro.props;
import "../assets/app.css";

// ========== 爬虫检测 (用于广告控制) ==========
const userAgent = Astro.request.headers.get('user-agent') || '';
const botUserAgents = [
  'googlebot', 'bingbot', 'slurp', 'duckduckbot',
  'baiduspider', 'yandexbot', 'facebookexternalhit',
  'twitterbot', 'linkedinbot', 'whatsapp', 'telegrambot',
  'applebot', 'petalbot', 'ahrefsbot', 'semrushbot',
  'mj12bot', 'dotbot', 'rogerbot', 'screaming frog'
];
const isBot = botUserAgents.some(bot => userAgent.toLowerCase().includes(bot));
---

<!doctype html>
<html>
  <head>
    <BaseHead title={title} description={description} />
  </head>
  
  <body>
    <!-- 1. 弹窗广告: 爬虫不显示 -->
    {!isBot && <ExoClickPopunder />}
    
    <Header />
    
    <main>
      <slot />  <!-- 页面内容插槽 -->
    </main>
    
    <Footer />
    
    <!-- 2. 底部广告: 爬虫不显示 -->
    {!isBot && <BottomAd />}
    
    <!-- 3. 年龄验证弹窗: 爬虫不显示 -->
    {!isBot && (
    <div id="ageVerificationModal" class="fixed inset-0 z-50 hidden">
      <!-- 弹窗内容 (标题、描述、按钮) -->
      <h3>年龄验证 / Age Verification Required</h3>
      <p>本成人内容...</p>
      
      <!-- 确认按钮 -->
      <button id="confirmAge">是的，我已满18岁</button>
      <!-- 拒绝按钮 -->
      <button id="denyAge">不，我未满18岁</button>
    </div>
    )}
    
    <!-- 4. 年龄验证脚本 -->
    <script type="module">
      // 检查是否已验证
      const isVerified = localStorage.getItem('ageVerified') === 'true';
      
      // 弹窗控制
      function showModal() { ... }
      function hideModal() { ... }
      
      // 确认按钮: 记录验证状态，隐藏弹窗
      document.getElementById('confirmAge').addEventListener('click', () => {
        localStorage.setItem('ageVerified', 'true');
        hideModal();
      });
      
      // 拒绝按钮: 跳转到Google
      document.getElementById('denyAge').addEventListener('click', () => {
        window.location.href = 'https://www.google.com';
      });
      
      // 页面加载后检查
      if (!isVerified) {
        setTimeout(showModal, 500);
      }
    </script>
  </body>
</html>
```

#### 8.8.3 代码作用解析

| 代码部分 | 作用 | 详细说明 |
|----------|------|----------|
| `botUserAgents` 数组 | 爬虫User-Agent列表 | 用于识别搜索引擎爬虫 |
| `isBot` 变量 | 爬虫判断结果 | true=爬虫, false=真实用户 |
| `{!isBot && <ExoClickPopunder />}` | 条件渲染弹窗广告 | 爬虫不加载 |
| `{!isBot && <BottomAd />}` | 条件渲染底部广告 | 爬虫不加载 |
| `{!isBot && <年龄验证弹窗 />}` | 条件渲染年龄验证 | 爬虫不加载 |
| `localStorage.getItem('ageVerified')` | 检查验证状态 | 用户确认过不再提示 |
| `confirmAge` 按钮 | 确认年龄 | 记录状态，隐藏弹窗 |
| `denyAge` 按钮 | 拒绝年龄 | 跳转Google |
| `astro:page-load` 事件 | Astro SPA导航 | 页面切换后重新检查 |

#### 8.8.4 广告控制流程图

```
用户请求页面
      │
      ↓
服务器端检测 User-Agent
      │
      ↓
      ┌──────────────────────┐
      │  是爬虫 (isBot=true) │ ──→ 不加载任何广告
      └──────────────────────┘
      │
      ↓ 是真实用户 (isBot=false)
      │
      ├────────────────────────────────────────┐
      │  检查年龄验证状态                        │
      │  (localStorage.ageVerified)            │
      └────────────────────────────────────────┘
              │
        ┌─────┴─────┐
        ↓           ↓
    已验证       未验证
        │           │
        ↓           ↓
    加载所有广告    显示年龄验证弹窗
                      │
                      ├──────────────┐
                      ↓              ↓
                点击"确认"      点击"拒绝"
                      │              │
                      ↓              ↓
                记录验证状态      跳转Google
                加载所有广告
```

#### 8.8.5 依赖关系图

```
BaseLayout.astro (广告控制中心)
    │
    ├── imports 依赖:
    │   ├── @components/BaseHead.astro
    │   │       └── 功能: 页面头部、GA分析
    │   ├── @components/Header.astro
    │   ├── @components/Footer.astro
    │   ├── @components/BottomAd.astro
    │   │       └── 功能: 底部悬浮广告
    │   ├── @components/ExoClickPopunder.astro
    │   │       └── 功能: 弹窗广告
    │   └── ../assets/app.css
    │
    ├── 控制逻辑:
    │   ├── 爬虫检测 (isBot)
    │   ├── 年龄验证状态 (localStorage)
    │   └── 广告显示条件 (!isBot)
    │
    ├── 被以下文件引用:
    │   ├── src/pages/index.astro
    │   ├── src/pages/posts/[...slug].astro
    │   ├── src/pages/category/[category]/[page].astro
    │   ├── src/pages/tags/[tag]/[page].astro
    │   ├── src/pages/videos.astro
    │   ├── src/pages/videos/[series]/index.astro
    │   ├── src/pages/videos/[series]/[slug].astro
    │   ├── src/pages/search.astro
    │   ├── src/pages/guestbook.astro
    │   └── src/pages/404.astro
    │
    └── 页面结构:
        <BaseLayout>
            │
            ├── <BaseHead /> (GA + SEO)
            │
            ├── {!isBot && <ExoClickPopunder />} (弹窗)
            │
            ├── <Header />
            │
            ├── <main> <slot /> </main> (页面内容)
            │
            ├── <Footer />
            │
            ├── {!isBot && <BottomAd />} (底部广告)
            │
            └── {!isBot && <年龄验证弹窗 />}
```

---

### 8.9 广告组件调用关系总览

#### 8.9.1 完整调用链路图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户访问 URL                                  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    src/pages/*.astro                                │
│  (index.astro, page/[page].astro, category/*/page.astro 等)        │
│                                                                      │
│  1. 引入布局: import BaseLayout from "../layouts/BaseLayout.astro" │
│  2. 引入广告: import AdWidget from "@components/AdWidget.astro"      │
│              import AdWidgetTriple from "@components/AdWidgetTriple"│
│  3. 获取数据: const allPosts = await getCollection("posts")        │
│  4. 渲染组件: <AdWidget /> 或 <AdWidgetTriple posts={allPosts} />   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    src/layouts/BaseLayout.astro                    │
│                                                                      │
│  1. 检测爬虫: const isBot = botUserAgents.some(...)                 │
│  2. 引入组件: import ExoClickPopunder from "..."                    │
│              import BottomAd from "..."                             │
│  3. 条件渲染: {!isBot && <ExoClickPopunder />}                      │
│              {!isBot && <BottomAd />}                                │
│  4. 年龄验证: {!isBot && <年龄验证弹窗 />}                           │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    src/components/*.astro                            │
│                                                                      │
│  AdWidget.astro ──────────→ 加载 https://a.magsrv.com/ad-provider  │
│                                  ↓                                  │
│                              <ins data-zoneid="5863494">           │
│                                                                      │
│  AdWidgetTriple.astro ──→ 加载 https://a.magsrv.com/ad-provider   │
│                                  ↓                                  │
│                              <ins data-zoneid="5863494">           │
│                                  + 伪装内容层                       │
│                                                                      │
│  ExoClickPopunder.astro ─→ 初始化 ExoClick SDK                     │
│                                  ↓                                  │
│                              监听点击 → 弹窗广告                     │
│                                                                      │
│  BottomAd.astro ──────────→ 加载 https://a.magsrv.com/ad-provider │
│                                  ↓                                  │
│                              <ins data-zoneid="5863710">           │
│                                  + 底部固定定位                     │
│                                                                      │
│  BaseHead.astro ──────────→ 加载 https://googletagmanager.com/gtag│
│                                  ↓                                  │
│                              初始化 GA4                              │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         广告服务器                                    │
│                                                                      │
│  a.magsrv.com  ────────────── 侧边栏/底部广告                        │
│  a.pemsrv.com  ────────────── 弹窗广告                              │
│  googletagmanager.com ─────── 网站分析                               │
└─────────────────────────────────────────────────────────────────────┘
```

#### 8.9.2 页面文件广告引用对照表

| 页面文件 | AdWidget | AdWidgetTriple | BaseLayout(含弹窗+底部) |
|----------|----------|----------------|-------------------------|
| `index.astro` | ❌ | ✅ (1处) | ✅ |
| `page/[page].astro` | ❌ | ✅ (2处) | ✅ |
| `category/[category]/[page].astro` | ❌ | ✅ (1处) | ✅ |
| `tags/[tag]/[page].astro` | ❌ | ✅ (1处) | ✅ |
| `videos.astro` | ❌ | ✅ (1处) | ✅ |
| `videos/[series]/index.astro` | ❌ | ✅ (1处) | ✅ |
| `videos/[series]/[slug].astro` | ❌ | ❌ | ✅ |
| `posts/[...slug].astro` | ❌ | ❌ | ✅ |
| `search.astro` | ❌ | ❌ | ✅ |
| `guestbook.astro` | ❌ | ❌ | ✅ |
| `404.astro` | ❌ | ❌ | ✅ |

---

### 8.10 常见广告问题排查

#### 8.10.1 广告不显示

**可能原因**:
1. 广告联盟账户被封禁
2. 浏览器安装了广告屏蔽插件 (AdBlock, uBlock Origin等)
3. 网络问题导致广告脚本加载失败
4. 广告位ID配置错误
5. 爬虫访问 (isBot=true)

**排查方法**:

```javascript
// 1. 检查浏览器控制台 (F12 → Console)
console.log('AdProvider:', window.AdProvider);

// 2. 检查网络请求 (F12 → Network)
// 搜索: a.magsrv.com 或 a.pemsrv.com

// 3. 检查DOM元素
document.querySelector('ins[data-zoneid="5863494"]')

// 4. 检查isBot状态 (需在页面中添加调试)
const isBot = /* 复制BaseLayout中的检测代码 */;
console.log('isBot:', isBot);
```

#### 8.10.2 广告加载缓慢

**可能原因**:
1. 广告联盟服务器响应慢
2. 广告脚本阻塞页面加载

**解决方法**:

```astro
<!-- 使用 async 异步加载，不阻塞页面 -->
<script is:inline async src="https://a.magsrv.com/ad-provider.js"></script>
```

#### 8.10.3 弹窗广告触发失败

**可能原因**:
1. 浏览器阻止了弹窗 (popup blocker)
2. TCF 同意未获取
3. 频率限制生效 (60分钟内不重复显示)
4. Cookie 被禁用

**解决方法**:

```javascript
// 1. 检查浏览器弹窗设置
// 浏览器设置 → 隐私与安全 → 弹窗窗口 → 添加白名单

// 2. 清除 Cookie 后重试
// 浏览器设置 → Cookie → 删除 site: 91tutu.cc

// 3. 检查TCF状态
console.log('TCF:', window.__tcfapi);

// 4. 等待60分钟后测试
```

#### 8.10.4 年龄验证弹窗问题

**问题**: 弹窗一直显示，无法关闭

**可能原因**:
1. localStorage 被禁用
2. JavaScript 错误

**排查**:

```javascript
// 检查 localStorage 是否可用
try {
  localStorage.setItem('test', 'test');
  localStorage.removeItem('test');
  console.log('localStorage 可用');
} catch (e) {
  console.log('localStorage 不可用:', e);
}

// 手动设置验证状态
localStorage.setItem('ageVerified', 'true');
location.reload();
```

---

## 九、安全与防护

### 9.1 R2 流量防护

详见 [R2_PROTECTION.md](astro-melody-starter/R2_PROTECTION.md):

1. **Cloudflare WAF 规则**: 速率限制、防DDoS
2. **防盗链**: 检查 Referer 头
3. **缓存策略**: 静态资源长期缓存
4. **成本控制**: 设置预算告警

### 9.2 中间件安全

- Content-Type 检查
- Frame 选项保护
- 引用策略控制

### 9.3 隐私保护

- 不收集敏感用户信息
- Cookie 使用合规
- GDPR 合规

---

## 十、常见问题

### 10.1 图片上传问题

**Q: 图片上传失败怎么办?**

A: 检查以下内容:
1. 确认 rclone 已正确配置 R2
2. 检查网络连接
3. 确认 R2 存储桶有足够空间
4. 查看错误日志

**Q: 如何重新处理已上传的图片?**

A: 删除 `conversion_record.json` 文件后重新运行转换脚本

### 10.2 视频处理问题

**Q: 视频切片失败怎么办?**

A: 检查以下内容:
1. 确认 FFmpeg 已正确安装并添加到 PATH
2. 检查视频格式是否支持
3. 确认输入输出目录权限
4. 查看 FFmpeg 错误输出

**Q: 视频无法播放怎么办?**

A: 检查以下内容:
1. 确认 HLS URL 正确
2. 确认 R2 存储桶已启用公共访问
3. 检查浏览器控制台错误
4. 验证 CORS 配置

### 10.3 部署问题

**Q: 部署到 Cloudflare Pages 失败怎么办?**

A: 检查以下内容:
1. 确认 `npm run build` 本地构建成功
2. 检查 wrangler.toml 配置
3. 查看 Cloudflare 构建日志
4. 确认环境变量正确设置

---

## 十一、快捷命令参考

### 图片博文

```powershell
# 步骤1: 转换图片为WebP
cd c:\huang\Image
python convert_to_webp_size_optimized.py

# 步骤2: 添加元数据
cd c:\huang\Image
python add_metadata_tags.py

# 步骤3: 上传到R2
cd c:\huang\Image-1
python upload_to_r2.py

# 步骤4: 生成博文
cd c:\huang\Image-1
python generate_markdown.py
```

### 视频博文

```powershell
# 步骤1: 转换为HLS
cd c:\huang
python video_processor.py

# 步骤2: 上传到R2
cd c:\huang
python upload_video_to_r2.py

# 步骤3: 生成博文
cd c:\huang
python generate_video_posts.py

# 步骤4: 构建并部署
cd c:\huang\astro-melody-starter
npm run build
npx wrangler pages deploy dist --branch=main
```

### 开发命令

```powershell
cd c:\huang\astro-melody-starter

# 开发模式
pnpm run dev

# 构建
pnpm run build

# 预览
pnpm run preview

# 检查
pnpm run astro check
```

---

## 十二、相关文档

- [Astro 官方文档](https://docs.astro.build)
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Cloudflare R2 文档](https://developers.cloudflare.com/r2/)
- [rclone 文档](https://rclone.org/docs/)
- [FFmpeg 文档](https://ffmpeg.org/documentation.html)
- [HLS.js 文档](https://hls-js.netlify.app/docs/)

---

*本文档最后更新于 2026-03-15*
