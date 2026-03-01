# Astro 内容缓存问题排查记录

## 问题描述

在 Astro 项目中，`src/content/videos/` 目录下已经没有任何 `.md` 文件，但构建后仍然生成了已删除内容对应的静态页面（如 `/videos/videotest/`）。

## 问题现象

1. 视频分区显示已删除的 `videotest` 分组
2. 构建输出中显示：
   ```
   ▶ src/pages/videos/[series]/[slug].astro
     └─ /videos/videotest/videotest1/index.html
   ▶ src/pages/videos/[series]/index.astro
     └─ /videos/videotest/index.html
   ```
3. 开发服务器已提示内容为空：
   ```
   [WARN] [glob-loader] No files found matching "**/*.md" in directory "src\content\videos"
   ```

## 排查过程

### 1. 检查数据源

首先检查了视频数据的来源：

- `src/data/videos/videos_metadata.json` - 只包含"紧急企划"系列，无 videotest
- `src/content/videos/` 目录 - 没有任何 `.md` 文件
- `src/content/config.ts` - 确认 videos collection 使用 glob loader 从 `./src/content/videos/` 加载

### 2. 检查构建产物

发现 `dist/videos/videotest/` 目录存在旧文件，删除后重新构建，问题依旧。

### 3. 检查项目缓存目录

发现 `.astro/` 目录下有缓存文件，删除 `.astro` 和 `dist` 目录后重新构建，问题依旧。

### 4. 定位根本原因

最终在 `node_modules/.astro/data-store.json` 中找到了缓存的 videotest 数据：

```powershell
# 搜索缓存中的 videotest
grep -r "videotest" node_modules/.astro/
# Found 1 line
```

这个文件是 Astro 的内容缓存，存储了之前构建时的内容集合数据。

## 解决方案

删除 `node_modules/.astro/data-store.json` 缓存文件后重新构建：

```powershell
# 清理缓存
Remove-Item -Force "node_modules/.astro/data-store.json"
Remove-Item -Recurse -Force ".astro", "dist"

# 重新构建
npm run build
```

构建输出确认问题已解决：

```
▶ src/pages/videos/[series]/[slug].astro
The collection "videos" does not exist or is empty. Please check your content config file for errors.
▶ src/pages/videos/[series]/index.astro
The collection "videos" does not exist or is empty. Please check your content config file for errors.
▶ src/pages/videos.astro
  └─ /videos/index.html
```

不再生成 videotest 相关页面。

## 根本原因

Astro 使用 `node_modules/.astro/data-store.json` 作为内容集合的持久化缓存。当内容文件被删除后，如果缓存没有正确失效，构建时仍会使用旧的缓存数据生成页面。

这个问题可能由以下原因触发：
1. 文件系统的时间戳问题导致缓存失效检测失败
2. Astro 版本的缓存失效逻辑存在缺陷
3. 非正常退出开发服务器导致缓存状态不一致

## 预防措施

### 方案一：添加清理脚本

在 `package.json` 中添加清理命令：

```json
{
  "scripts": {
    "clean": "Remove-Item -Recurse -Force .astro, dist, node_modules/.astro -ErrorAction SilentlyContinue",
    "build:clean": "npm run clean && npm run build"
  }
}
```

### 方案二：构建前自动清理

修改 `package.json` 的 build 脚本：

```json
{
  "scripts": {
    "prebuild": "node -e \"const fs=require('fs'); ['.astro','dist','node_modules/.astro'].forEach(p=>{try{fs.rmSync(p,{recursive:true})}catch(e){}})\"",
    "build": "astro check && astro build"
  }
}
```

### 方案三：使用 npm 脚本（跨平台）

安装 rimraf 并添加清理脚本：

```json
{
  "scripts": {
    "clean": "rimraf .astro dist node_modules/.astro",
    "build": "npm run clean && astro check && astro build"
  },
  "devDependencies": {
    "rimraf": "^5.0.0"
  }
}
```

## 相关文件

- 内容配置：`src/content/config.ts`
- 视频列表页：`src/pages/videos.astro`
- 视频系列页：`src/pages/videos/[series]/index.astro`
- 视频详情页：`src/pages/videos/[series]/[slug].astro`
- 缓存文件：`node_modules/.astro/data-store.json`

## 日期

2026-03-01
