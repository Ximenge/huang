# Cloudflare Pages 和 R2 流量防护指南

本文档提供防止恶意刷流量消耗R2配额的完整防护方案。

## 风险分析

### 潜在攻击方式
1. **DDoS攻击** - 大量请求消耗带宽和R2流量
2. **图片盗链** - 其他网站直接引用你的R2资源
3. **爬虫滥用** - 恶意爬虫高频抓取内容
4. **API滥用** - 如果有API端点被恶意调用

## 防护方案

### 1. Cloudflare WAF 规则配置

#### 1.1 基础速率限制
在Cloudflare Dashboard中配置WAF规则：

```javascript
// 防止单个IP高频请求
(http.request.uri.path matches ".*") and (cf.threat_score > 10)
```

**配置建议：**
- 每10分钟限制1000次请求
- 超过限制返回429状态码
- 持续时间：1小时

#### 1.2 针对静态资源的防护
```javascript
// 针对图片和媒体文件的特殊规则
(http.request.uri.path matches "\.(jpg|jpeg|png|gif|webp|svg|mp4|webm)$") and 
(cf.threat_score > 5)
```

### 2. Cloudflare Page Rules

#### 2.1 启用缓存
```
*91tutu.cc/*
- Cache Level: Cache Everything
- Edge Cache TTL: 2 hours
- Browser Cache TTL: 4 hours
```

#### 2.2 图片缓存优化
```
*91tutu.cc/*.{jpg,png,webp,gif}
- Cache Level: Aggressive
- Edge Cache TTL: 1 month
- Browser Cache TTL: 1 year
```

### 3. R2 存储防护

#### 3.1 预签名URL (推荐)
使用预签名URL限制访问时间：

```javascript
// 示例：生成预签名URL
import { R2 } from '@cloudflare/workers-types';

async function getPresignedUrl(bucket, key, expiresIn = 3600) {
  const url = new URL(`https://your-bucket.r2.dev/${key}`);
  url.searchParams.set('expires', Date.now() + expiresIn * 1000);
  return url.toString();
}
```

#### 3.2 访问控制列表 (ACL)
```javascript
// 在wrangler.toml中配置R2绑定
[[r2_buckets]]
binding = "IMAGES"
bucket_name = "your-bucket-name"

// 在Worker中实现访问控制
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // 检查Referer头防止盗链
    const referer = request.headers.get('Referer');
    if (!referer || !referer.includes('91tutu.cc')) {
      return new Response('Unauthorized', { status: 403 });
    }
    
    // 继续处理请求
  }
};
```

### 4. Astro 项目配置优化

#### 4.1 启用图片优化
```javascript
// astro.config.mjs
image: {
  remotePatterns: [
    {
      protocol: "https",
      hostname: "images.unsplash.com",
    },
    {
      protocol: "https",
      hostname: "your-bucket.r2.dev",
    },
  ],
  // 启用本地图片优化
  service: {
    entrypoint: "astro/assets/services/sharp",
  },
}
```

#### 4.2 添加防盗链中间件
创建 `src/middleware.ts`:

```typescript
export async function onRequest(context) {
  const response = await context.next();
  
  // 添加防盗链头
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  
  return response;
}
```

### 5. 监控和告警

#### 5.1 Cloudflare Analytics
- 设置流量异常告警
- 监控请求频率
- 跟踪热门资源

#### 5.2 R2 使用监控
```bash
# 查看R2使用情况
wrangler r2 bucket list
wrangler r2 object list your-bucket-name
```

### 6. 成本控制措施

#### 6.1 设置预算告警
在Cloudflare Dashboard中：
1. 进入 Billing & Subscriptions
2. 设置每月预算告警
3. 配置邮件和短信通知

#### 6.2 限制R2访问
```javascript
// 在Worker中实现请求频率限制
const rateLimiter = new Map();

async function checkRateLimit(ip) {
  const now = Date.now();
  const requests = rateLimiter.get(ip) || [];
  
  // 清理1小时前的请求
  const recentRequests = requests.filter(time => now - time < 3600000);
  
  if (recentRequests.length > 1000) {
    return false; // 超过限制
  }
  
  recentRequests.push(now);
  rateLimiter.set(ip, recentRequests);
  return true;
}
```

## 实施步骤

### 阶段1：基础防护 (立即实施)
1. 在Cloudflare Dashboard启用WAF
2. 配置基础速率限制规则
3. 启用Page Rules缓存

### 阶段2：高级防护 (1-2天)
1. 实现防盗链中间件
2. 配置R2访问控制
3. 设置监控告警

### 阶段3：持续优化 (持续进行)
1. 定期审查访问日志
2. 调整防护规则
3. 监控成本和性能

## 应急响应

### 发现异常流量时的处理步骤

1. **立即行动**
   ```bash
   # 暂时限制访问
   npx wrangler pages deployment list --project-name=astro-melody-starter
   ```

2. **启用严格模式**
   - 在WAF中启用"Under Attack Mode"
   - 临时提高速率限制阈值

3. **分析攻击源**
   - 查看Cloudflare Analytics
   - 识别恶意IP和User-Agent
   - 添加到黑名单

4. **恢复服务**
   - 确认攻击停止后逐步放宽限制
   - 监控24小时确保稳定

## 最佳实践

### 1. 定期审查
- 每周检查访问日志
- 每月审查WAF规则效果
- 季度评估成本和性能

### 2. 分层防护
```
用户请求 → Cloudflare WAF → 速率限制 → 缓存层 → R2存储
```

### 3. 渐进式部署
- 先在测试环境验证
- 逐步应用到生产环境
- 持续监控效果

## 相关资源

- [Cloudflare WAF文档](https://developers.cloudflare.com/waf/)
- [R2存储文档](https://developers.cloudflare.com/r2/)
- [Cloudflare Page Rules](https://developers.cloudflare.com/cache/about-page-rules/)
- [Astro安全最佳实践](https://docs.astro.build/en/guides/security/)

## 常见问题

### Q: 如何知道是否被攻击？
A: 监控以下指标：
- 请求量突然激增
- 带宽使用异常增长
- R2流量消耗加快
- 来自单一IP的大量请求

### Q: 防护会影响正常用户吗？
A: 合理配置不会影响正常用户：
- 设置合理的速率限制
- 使用白名单信任的爬虫
- 定期调整规则基于实际流量

### Q: R2流量用完了怎么办？
A: 
1. 立即启用严格防护模式
2. 联系Cloudflare支持
3. 考虑升级套餐或设置硬性限制
4. 审查并优化资源使用
