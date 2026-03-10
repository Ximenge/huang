# Popunder 广告系统使用说明

## 1. 基础用法

在你的 Astro 项目中，在 `<body>` 标签开始处添加以下代码：

```html
<script type="application/javascript" async 
  src="/popunder.js" 
  id="popunderldr" 
  data-idzone="YOUR_ADZONE_ID" 
  data-frequency_period="720" 
  data-frequency_count="1" 
  data-trigger_method="3" 
  data-chrome_enabled="true" 
  data-capping_enabled="true" 
  data-cookieconsent="true">
</script>
```

## 2. 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `data-idzone` | String | 必填 | 广告位ID |
| `data-frequency_period` | Number | 720 | 频率限制周期（分钟） |
| `data-frequency_count` | Number | 1 | 周期内最多显示次数 |
| `data-trigger_method` | Number | 3 | 触发方式（见下方） |
| `data-trigger_class` | String | '' | 触发class（trigger_method=2时使用） |
| `data-trigger_delay` | Number | 0 | 触发延迟（秒） |
| `data-chrome_enabled` | Boolean | true | Chrome浏览器启用 |
| `data-new_tab` | Boolean | false | 是否在新标签页打开广告 |
| `data-capping_enabled` | Boolean | true | 启用频率限制 |
| `data-cookieconsent` | Boolean | true | 需要Cookie同意 |

## 3. 触发方式 (trigger_method)

| 值 | 触发方式 | 说明 |
|----|----------|------|
| 1 | 任意点击 | 点击页面任意位置触发 |
| 2 | 特定class | 点击带有指定class的元素触发 |
| 3 | 点击链接 | 点击链接时触发（推荐） |
| 4 | 非特定class | 点击非指定class的元素触发 |
| 5 | 非链接 | 点击非链接元素时触发 |

## 4. 使用示例

### 示例1：点击链接时触发（最常用）

```html
<body>
  <script type="application/javascript" async 
    src="/popunder.js" 
    id="popunderldr" 
    data-idzone="123456" 
    data-trigger_method="3" 
    data-frequency_period="720" 
    data-frequency_count="1">
  </script>
  <!-- 页面内容 -->
</body>
```

### 示例2：点击特定按钮时触发

```html
<body>
  <script type="application/javascript" async 
    src="/popunder.js" 
    id="popunderldr" 
    data-idzone="123456" 
    data-trigger_method="2" 
    data-trigger_class="ad-trigger"
    data-frequency_period="720" 
    data-frequency_count="1">
  </script>
  
  <button class="ad-trigger">点击下载</button>
  <button class="ad-trigger">点击查看更多</button>
</body>
```

### 示例3：点击任意位置触发（高频）

```html
<body>
  <script type="application/javascript" async 
    src="/popunder.js" 
    id="popunderldr" 
    data-idzone="123456" 
    data-trigger_method="1" 
    data-frequency_period="60" 
    data-frequency_count="3">
  </script>
</body>
```

## 5. 工作原理

1. **脚本加载**：页面加载时异步加载 `popunder.js`
2. **配置读取**：从 `data-*` 属性读取配置参数
3. **事件监听**：根据 `trigger_method` 设置点击事件监听
4. **频率控制**：使用 Cookie 记录用户已看到的广告次数
5. **弹窗触发**：
   - 用户点击时，在新标签页打开原链接
   - 在当前页面打开广告链接
6. **浏览器适配**：针对 Chrome 使用特殊处理方式

## 6. 注意事项

1. **广告位ID**：需要将 `YOUR_ADZONE_ID` 替换为实际的广告位ID
2. **频率限制**：建议设置合理的频率限制，避免过度打扰用户
3. **浏览器兼容性**：代码已适配 Chrome、Firefox、Safari 等主流浏览器
4. **移动端**：在移动端会自动使用兼容的弹窗方式

## 7. 在 Astro 项目中集成

### 方法1：直接修改 BaseLayout.astro

```astro
---
// src/layouts/BaseLayout.astro
---
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- 头部内容 -->
</head>
<body>
  <!-- Popunder 广告脚本 -->
  <script type="application/javascript" async 
    src="/popunder.js" 
    id="popunderldr" 
    data-idzone="YOUR_ADZONE_ID" 
    data-trigger_method="3" 
    data-frequency_period="720" 
    data-frequency_count="1">
  </script>
  
  <slot />
</body>
</html>
```

### 方法2：使用组件方式

创建 `src/components/PopunderAd.astro`：

```astro
---
interface Props {
  idzone: string;
  triggerMethod?: number;
  frequencyPeriod?: number;
  frequencyCount?: number;
}

const { 
  idzone, 
  triggerMethod = 3, 
  frequencyPeriod = 720, 
  frequencyCount = 1 
} = Astro.props;
---

<script 
  type="application/javascript" 
  async 
  src="/popunder.js" 
  id="popunderldr" 
  data-idzone={idzone}
  data-trigger_method={triggerMethod}
  data-frequency_period={frequencyPeriod}
  data-frequency_count={frequencyCount}
  data-chrome_enabled="true"
  data-capping_enabled="true">
</script>
```

然后在布局中使用：

```astro
---
import PopunderAd from '../components/PopunderAd.astro';
---

<body>
  <PopunderAd idzone="123456" triggerMethod={3} />
  <slot />
</body>
```

## 8. 测试

部署后，可以通过以下方式测试：

1. 清除浏览器 Cookie
2. 访问网站
3. 点击链接（如果 trigger_method=3）
4. 观察是否弹出广告页面

## 9. 与 ExoClick 的区别

| 特性 | 本实现 | ExoClick |
|------|--------|----------|
| 代码量 | 轻量 (~8KB) | 较重 (~100KB+) |
| 混淆程度 | 无 | 重度混淆 |
| 反调试 | 无 | 有 |
| 广告评分 | 无 | 有 |
| 自定义程度 | 高 | 低 |
| 广告源 | 需要自行接入 | 内置 |

**注意**：这个实现只是一个框架，你需要：
1. 接入实际的广告源（修改 `buildAdUrl` 函数）
2. 或者使用自己的广告跳转逻辑
