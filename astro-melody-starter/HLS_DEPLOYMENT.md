# HLS视频部署指南

本指南介绍如何使用HLS技术将视频部署到Cloudflare R2，并在网站上播放。

## 前置要求

1. **安装ffmpeg**
   - Windows: 下载ffmpeg并添加到PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

2. **安装rclone**
   - 下载rclone: https://rclone.org/downloads/
   - 配置Cloudflare R2: `rclone config`

3. **安装Python依赖**
   ```bash
   pip install requests
   ```

## 部署流程

### 1. 准备视频文件

将视频文件放入`videos_input`目录：
```
videos_input/
├── video1.mp4
├── video2.mp4
└── video3.mp4
```

### 2. 使用ffmpeg切片视频

运行视频处理脚本：
```bash
python scripts/video_processor.py --input videos_input --output videos_output
```

参数说明：
- `--input`: 输入目录，包含原始视频文件
- `--output`: 输出目录，存放HLS切片文件
- `--segment-duration`: 切片时长（秒），默认10秒

输出结构：
```
videos_output/
├── video1/
│   ├── playlist.m3u8
│   ├── segment_000.ts
│   ├── segment_001.ts
│   ├── ...
│   └── metadata.json
├── video2/
│   ├── playlist.m3u8
│   ├── segment_000.ts
│   ├── ...
│   └── metadata.json
└── all_videos_metadata.json
```

### 3. 上传到Cloudflare R2

运行上传脚本：
```bash
python scripts/r2_uploader.py --local videos_output --bucket your-bucket-name --project .
```

参数说明：
- `--local`: 本地HLS文件目录
- `--bucket`: Cloudflare R2存储桶名称
- `--remote`: rclone远程名称（默认：r2）
- `--project`: 项目目录，用于复制元数据文件

### 4. 更新视频元数据

上传完成后，元数据会自动复制到`src/data/videos/videos_metadata.json`。

如果需要手动更新，编辑`src/data/videos/videos_metadata.json`文件，添加新的视频信息。

### 5. 重新构建项目

```bash
npm run build
```

### 6. 部署到Cloudflare Pages

```bash
wrangler pages deploy dist
```

## HLS配置说明

### 视频切片参数

在`video_processor.py`中可以调整切片参数：

```python
# 切片时长（秒）
segment_duration = 10

# 视频编码参数
'-c:v', 'libx264',  # 视频编码器
'-c:a', 'aac',       # 音频编码器
'-hls_time', str(segment_duration),  # 切片时长
'-hls_list_size', '0',  # 0表示不限制播放列表大小
```

### HLS.js播放器配置

在视频页面中可以调整播放器参数：

```javascript
const hls = new Hls({
  debug: false,           // 调试模式
  enableWorker: true,     // 启用Web Worker
  lowLatencyMode: true,   // 低延迟模式
  backBufferLength: 90    // 后缓冲区长度（秒）
});
```

## 性能优化建议

1. **切片时长**
   - 短视频（<5分钟）：5-10秒
   - 中等视频（5-30分钟）：10-15秒
   - 长视频（>30分钟）：15-30秒

2. **视频编码**
   - 使用H.264编码以确保最大兼容性
   - 比特率建议：720p: 2-5Mbps, 1080p: 5-10Mbps

3. **CDN配置**
   - Cloudflare R2自动提供CDN加速
   - 确保R2存储桶已启用公共访问

4. **缓存策略**
   - HLS切片文件可以长期缓存
   - m3u8播放列表文件缓存时间较短

## 故障排除

### 视频无法播放

1. 检查HLS URL是否正确
2. 确认R2存储桶已启用公共访问
3. 检查浏览器控制台错误信息
4. 验证CORS配置

### 切片失败

1. 确认ffmpeg已正确安装
2. 检查视频文件格式是否支持
3. 验证输入输出目录权限

### 上传失败

1. 确认rclone已正确配置
2. 检查R2存储桶权限
3. 验证网络连接

## 示例

完整的部署流程示例：

```bash
# 1. 准备视频文件
mkdir -p videos_input
cp /path/to/your/videos/*.mp4 videos_input/

# 2. 切片视频
python scripts/video_processor.py --input videos_input --output videos_output

# 3. 上传到R2
python scripts/r2_uploader.py --local videos_output --bucket your-bucket-name --project .

# 4. 重新构建
npm run build

# 5. 部署
wrangler pages deploy dist
```

## 技术架构

```
原始视频 → ffmpeg切片 → HLS文件 → rclone上传 → Cloudflare R2 → CDN分发 → HLS.js播放
```

### 优势

- **快速加载**: CDN加速，切片按需加载
- **带宽优化**: 只加载需要播放的片段
- **兼容性好**: 支持所有现代浏览器
- **成本低**: Cloudflare R2提供免费额度

### 注意事项

- 视频文件大小建议控制在500MB以内
- 切片数量不宜过多，影响加载性能
- 定期清理不需要的视频文件
