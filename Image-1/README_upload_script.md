# R2 自动上传脚本使用说明

## 功能特点

1. **自动检查远程目录**：上传前会检查 R2 中已存在的文件夹
2. **智能跳过**：如果远程目录已存在，自动跳过上传，避免重复
3. **文件夹名称转换**：自动将本地文件夹名称中的空格替换为 `-`，下划线保持不变
4. **详细日志**：显示上传进度、跳过原因和最终统计
5. **错误处理**：完善的异常处理和错误提示

## 配置说明

脚本中的配置项（第 4-12 行）：

```powershell
$remoteName = "small"              # rclone 配置名称
$baseRemotePath = "small"          # R2 中的基础路径
$localPath = "C:\huang\Image-1"   # 本地工作目录

$foldersToUpload = @{
    "UID 408339" = "UID-408339"   # 本地名称 -> 远程名称
    "test_images" = "test-images"
}
```

### 如何添加新的上传文件夹

在 `$foldersToUpload` 哈希表中添加新的映射：

```powershell
$foldersToUpload = @{
    "UID 408339" = "UID-408339"
    "test_images" = "test-images"
    "new_folder" = "new-folder"      # 新增的文件夹
}
```

**注意**：
- 左边是本地文件夹名称（可以包含空格）
- 右边是远程文件夹名称（空格会被替换为 `-`）

## 使用方法

### 方法 1：直接运行
```powershell
powershell -ExecutionPolicy Bypass -File upload_to_r2.ps1
```

### 方法 2：在 PowerShell 中运行
```powershell
cd C:\huang\Image-1
.\upload_to_r2.ps1
```

## 运行示例

### 场景 1：首次上传（远程无文件）
```
========================================
R2 Auto Upload Script
========================================

Step 1: Checking R2 remote directories...
Getting remote directory list: small...
Remote existing directories: 

Checking folder: UID 408339 (remote name: UID-408339)

----------------------------------------
Uploading: UID 408339 -> UID-408339
----------------------------------------
Transferred:        9.635 MiB / 9.635 MiB, 100%, 704.700 KiB/s, ETA 0s
[OK] Upload success: UID 408339

Checking folder: test_images (remote name: test-images)

----------------------------------------
Uploading: test_images -> test-images
----------------------------------------
Transferred:            418 B / 418 B, 100%, 104 B/s, ETA 0s
[OK] Upload success: test_images

========================================
Upload Complete!
========================================
Successfully uploaded: 2 folders
Skipped (already exists): 0 folders
Failed: 0 folders
```

### 场景 2：重复运行（远程已存在）
```
========================================
R2 Auto Upload Script
========================================

Step 1: Checking R2 remote directories...
Getting remote directory list: small...
Remote existing directories: UID-408339, test-images

Checking folder: UID 408339 (remote name: UID-408339)
  [SKIP] Remote directory already exists: UID-408339

Checking folder: test_images (remote name: test-images)
  [SKIP] Remote directory already exists: test-images

========================================
Upload Complete!
========================================
Successfully uploaded: 0 folders
Skipped (already exists): 2 folders
Failed: 0 folders
```

## 文件夹命名规则

| 本地文件夹名称 | 远程文件夹名称 | 说明 |
|--------------|--------------|------|
| `UID 408339` | `UID-408339` | 空格替换为 `-` |
| `test_images` | `test-images` | 下划线保持不变 |
| `my folder` | `my-folder` | 空格替换为 `-` |
| `my_folder` | `my-folder` | 下划线替换为 `-` |

## 输出说明

- **绿色** `[OK]`：上传成功
- **黄色** `[SKIP]`：跳过上传（远程已存在或本地不存在）
- **红色** `[FAIL]` / `[ERROR]`：上传失败或出错

## 注意事项

1. **rclone 配置**：确保 rclone 已正确配置，并且配置文件位于 `C:\Users\11786\AppData\Roaming\rclone\rclone.conf`
2. **网络连接**：确保网络连接正常，能够访问 Cloudflare R2
3. **权限**：确保有权限读写本地目录和 R2 存储
4. **文件夹映射**：修改 `$foldersToUpload` 时，确保远程名称符合 R2 的命名规则（不能包含特殊字符）

## 故障排除

### 问题：脚本无法运行
**解决方案**：使用 `-ExecutionPolicy Bypass` 参数
```powershell
powershell -ExecutionPolicy Bypass -File upload_to_r2.ps1
```

### 问题：无法连接到 R2
**解决方案**：
1. 检查 rclone 配置是否正确
2. 验证网络连接
3. 检查访问密钥是否有效

### 问题：文件夹名称转换错误
**解决方案**：
在 `$foldersToUpload` 中手动指定正确的远程名称映射

## 高级用法

### 强制重新上传
如果需要强制重新上传某个文件夹，可以：
1. 先在 R2 中删除该文件夹
2. 重新运行脚本

### 添加更多文件夹
编辑脚本中的 `$foldersToUpload` 部分，添加新的文件夹映射。