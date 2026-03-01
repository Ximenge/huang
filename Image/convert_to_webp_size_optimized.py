import os
import shutil
import json
from PIL import Image

def load_conversion_record(json_path):
    """加载转换记录JSON文件"""
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 无法读取转换记录文件: {str(e)}")
            return {}
    return {}

def save_conversion_record(json_path, record):
    """保存转换记录到JSON文件"""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        print(f"转换记录已保存到: {json_path}")
    except Exception as e:
        print(f"警告: 无法保存转换记录文件: {str(e)}")

def is_directory_converted(record, dir_path):
    """检查目录是否已转换过"""
    return dir_path in record

def add_conversion_record(record, dir_path, converted_count, target_dir):
    """添加转换记录"""
    record[dir_path] = {
        "converted_count": converted_count,
        "target_directory": target_dir,
        "timestamp": os.path.getmtime(dir_path) if os.path.exists(dir_path) else None
    }



def copy_webp_files(source_dir, target_dir):
    """复制目录中的所有 webp 文件到目标目录，并按顺序重命名"""
    copied_files = 0
    
    # 遍历所有子目录
    for root, _, files in os.walk(source_dir):
        if root == source_dir:
            continue
        
        # 收集当前目录中的所有 webp 文件
        webp_files = []
        for file in files:
            if file.lower().endswith('.webp'):
                source_path = os.path.join(root, file)
                webp_files.append((source_path, file))
        
        # 按文件名排序，确保顺序一致
        webp_files.sort(key=lambda x: x[1])
        
        # 计算相对路径，创建目标子目录
        relative_path = os.path.relpath(root, source_dir)
        target_subdir = os.path.join(target_dir, relative_path)
        os.makedirs(target_subdir, exist_ok=True)
        
        # 按顺序复制并重命名文件
        for idx, (source_path, original_name) in enumerate(webp_files, 1):
            # 生成新的文件名：001.webp, 002.webp, 003.webp, ...
            new_filename = f"{idx:03d}.webp"
            target_path = os.path.join(target_subdir, new_filename)
            
            if os.path.exists(target_path):
                print(f"跳过: {new_filename} (目标文件已存在)")
            else:
                try:
                    shutil.copy2(source_path, target_path)
                    print(f"已复制: {original_name} -> {new_filename}")
                    copied_files += 1
                except Exception as e:
                    print(f"复制失败 {original_name}: {str(e)}")
    
    return copied_files

def batch_convert(directory, record=None, max_size_kb=200, dpi=72, max_resolution=1440):
    """批量转换目录中的所有图片文件
    
    Args:
        directory: 要处理的目录
        record: 转换记录字典
        max_size_kb: 目标文件大小上限（KB）
        dpi: 目标DPI值
        max_resolution: 最大分辨率（长或宽）
    """
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    
    total_files = 0
    converted_files = 0
    converted_dirs = 0
    total_original_size = 0
    total_webp_size = 0
    
    for root, _, files in os.walk(directory):
        if root == directory:
            continue
            
        if record is not None and is_directory_converted(record, root):
            print(f"跳过已转换的目录: {root}")
            continue
        
        # 收集当前目录中的所有图片文件
        image_files = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_formats:
                image_files.append(file)
        
        # 按文件名排序，确保顺序一致
        image_files.sort()
        
        dir_converted_count = 0
        for idx, file in enumerate(image_files, 1):
            ext = os.path.splitext(file)[1].lower()
            
            if ext in supported_formats:
                total_files += 1
                input_path = os.path.join(root, file)
                
                original_size = os.path.getsize(input_path) / 1024
                total_original_size += original_size
                
                # 生成新的webp文件名：001.webp, 002.webp, 003.webp, ...
                webp_filename = f"{idx:03d}.webp"
                output_path = os.path.join(root, webp_filename)
                
                # 检查目标文件是否存在
                if os.path.exists(output_path):
                    print(f"跳过: {webp_filename} (目标文件已存在)")
                    continue
                
                # 转换图片
                try:
                    img = Image.open(input_path)
                    original_width, original_height = img.size
                    original_ratio = original_width / original_height if original_height > 0 else 1
                    
                    original_file_size = os.path.getsize(input_path) / 1024
                    
                    # 计算基于分辨率上限的最大缩放比例
                    scale_by_width = max_resolution / original_width if original_width > max_resolution else 1.0
                    scale_by_height = max_resolution / original_height if original_height > max_resolution else 1.0
                    max_scale_by_resolution = min(scale_by_width, scale_by_height)
                    
                    # 计算目标尺寸（优先使用最大分辨率，保持比例）
                    target_width = int(original_width * max_scale_by_resolution)
                    target_height = int(original_height * max_scale_by_resolution)
                    
                    # 确保不超过分辨率上限（含1440）
                    target_width = min(target_width, max_resolution)
                    target_height = min(target_height, max_resolution)
                    
                    # 检查是否需要靠拢标准分辨率
                    standard_resolutions = [1080, 960, 1440, 1280, 720]
                    tolerance = 6
                    
                    # 检查宽度
                    for std_res in standard_resolutions:
                        if abs(target_width - std_res) <= tolerance:
                            target_width = std_res
                            print(f"  宽度靠拢标准分辨率: {std_res}px")
                            break
                    
                    # 检查高度
                    for std_res in standard_resolutions:
                        if abs(target_height - std_res) <= tolerance:
                            target_height = std_res
                            print(f"  高度靠拢标准分辨率: {std_res}px")
                            break
                    
                    print(f"  开始优化，优先保持比例和分辨率...")
                    print(f"  原始尺寸: {original_width}x{original_height}, 原始大小: {original_file_size:.1f}KB")
                    print(f"  目标分辨率: {target_width}x{target_height}")
                    
                    # 调整图片大小到目标分辨率
                    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # 第一步：尝试不同的质量设置，从高到低
                    best_quality = 95
                    best_size = float('inf')
                    
                    for quality in [95, 90, 85, 80, 75, 70, 65, 60, 55, 50]:
                        # 保存临时文件测试大小
                        temp_path = output_path + '.temp'
                        img_resized.save(temp_path, 'webp', quality=quality, dpi=(dpi, dpi))
                        temp_size = os.path.getsize(temp_path) / 1024
                        
                        # 如果找到合适的大小
                        if temp_size <= max_size_kb:
                            # 重命名临时文件为最终文件
                            if os.path.exists(output_path):
                                os.remove(output_path)
                            os.rename(temp_path, output_path)
                            
                            compression_ratio = (1 - temp_size / original_file_size) * 100 if original_file_size > 0 else 0
                            
                            print(f"  优化完成: 质量{quality}")
                            print(f"  最终尺寸: {target_width}x{target_height}")
                            print(f"已转换: {file} -> {webp_filename}")
                            print(f"  原始大小: {original_file_size:.1f}KB, WebP大小: {temp_size:.1f}KB, 压缩率: {compression_ratio:.1f}%")
                            
                            converted_files += 1
                            dir_converted_count += 1
                            
                            if os.path.exists(output_path):
                                total_webp_size += os.path.getsize(output_path) / 1024
                            
                            break
                        
                        # 记录最佳结果
                        if temp_size < best_size:
                            best_size = temp_size
                            best_quality = quality
                        
                        # 删除临时文件
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    else:
                        # 第二步：如果最低质量仍超过200KB，逐步降低分辨率
                        print(f"  最低质量50仍超过{max_size_kb}KB，开始降低分辨率...")
                        
                        # 使用二分法找到合适的缩放比例
                        scale_min = 0.1
                        scale_max = max_scale_by_resolution
                        final_scale = scale_max
                        final_quality = 50
                        
                        for iteration in range(10):
                            test_scale = (scale_min + scale_max) / 2
                            test_width = int(original_width * test_scale)
                            test_height = int(original_height * test_scale)
                            
                            # 确保不超过分辨率上限
                            test_width = min(test_width, max_resolution)
                            test_height = min(test_height, max_resolution)
                            
                            # 调整图片大小
                            img_test = img.resize((test_width, test_height), Image.Resampling.LANCZOS)
                            
                            # 尝试最低质量
                            temp_path = output_path + '.temp'
                            img_test.save(temp_path, 'webp', quality=final_quality, dpi=(dpi, dpi))
                            temp_size = os.path.getsize(temp_path) / 1024
                            
                            if temp_size <= max_size_kb:
                                # 找到合适的大小，尝试更高的缩放比例
                                scale_min = test_scale
                                final_scale = test_scale
                                final_width = test_width
                                final_height = test_height
                                final_size = temp_size
                            else:
                                # 仍然太大，降低缩放比例
                                scale_max = test_scale
                            
                            # 删除临时文件
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        
                        # 使用最终找到的参数保存图片
                        final_width = int(original_width * final_scale)
                        final_height = int(original_height * final_scale)
                        final_width = min(final_width, max_resolution)
                        final_height = min(final_height, max_resolution)
                        
                        img_final = img.resize((final_width, final_height), Image.Resampling.LANCZOS)
                        img_final.save(output_path, 'webp', quality=final_quality, dpi=(dpi, dpi))
                        
                        webp_size = os.path.getsize(output_path) / 1024
                        compression_ratio = (1 - webp_size / original_file_size) * 100 if original_file_size > 0 else 0
                        
                        print(f"  优化完成: 质量{final_quality}, 缩放比例{final_scale:.2f}")
                        print(f"  最终尺寸: {final_width}x{final_height}")
                        print(f"已转换: {file} -> {webp_filename}")
                        print(f"  原始大小: {original_file_size:.1f}KB, WebP大小: {webp_size:.1f}KB, 压缩率: {compression_ratio:.1f}%")
                        
                        converted_files += 1
                        dir_converted_count += 1
                        
                        if os.path.exists(output_path):
                            total_webp_size += os.path.getsize(output_path) / 1024
                except Exception as e:
                    print(f"转换失败 {file}: {str(e)}")
        
        if dir_converted_count > 0 and record is not None:
            relative_path = os.path.relpath(root, directory)
            current_dir_name = os.path.basename(directory)
            target_base = os.path.join(os.path.dirname(directory), f"{current_dir_name}-1")
            target_dir = os.path.join(target_base, relative_path)
            
            add_conversion_record(record, root, dir_converted_count, target_dir)
            converted_dirs += 1
    
    print(f"\n转换完成！")
    print(f"总图片数: {total_files}")
    print(f"成功转换: {converted_files}")
    print(f"失败: {total_files - converted_files}")
    print(f"转换的目录数: {converted_dirs}")
    
    if total_original_size > 0:
        total_compression_ratio = (1 - total_webp_size / total_original_size) * 100
        print(f"\n总体压缩统计:")
        print(f"原始总大小: {total_original_size:.1f}KB ({total_original_size/1024:.1f}MB)")
        print(f"WebP总大小: {total_webp_size:.1f}KB ({total_webp_size/1024:.1f}MB)")
        print(f"总体压缩率: {total_compression_ratio:.1f}%")
        print(f"节省空间: {(total_original_size - total_webp_size):.1f}KB ({(total_original_size - total_webp_size)/1024:.1f}MB)")
    
    return converted_files

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    MAX_SIZE_KB = 200
    TARGET_DPI = 72
    MAX_RESOLUTION = 1440
    
    print(f"开始转换目录: {current_directory}")
    print(f"目标文件大小: {MAX_SIZE_KB}KB以下")
    print(f"目标DPI: {TARGET_DPI}")
    print(f"最大分辨率: {MAX_RESOLUTION}px（含）")
    
    json_record_path = os.path.join(current_directory, "conversion_record.json")
    
    print(f"\n加载转换记录: {json_record_path}")
    conversion_record = load_conversion_record(json_record_path)
    print(f"已记录的转换目录数: {len(conversion_record)}")
    
    # 显示已记录的文件夹
    if conversion_record:
        print("\n已记录的文件夹（将跳过）:")
        for dir_path in conversion_record.keys():
            print(f"  - {os.path.basename(dir_path)}")
    
    converted_count = batch_convert(current_directory, conversion_record, max_size_kb=MAX_SIZE_KB, dpi=TARGET_DPI, max_resolution=MAX_RESOLUTION)
    
    if converted_count > 0:
        save_conversion_record(json_record_path, conversion_record)
        print(f"\n[OK] 已更新转换记录，共 {len(conversion_record)} 个文件夹")
    else:
        print("\n[INFO] 没有新的文件夹需要转换")
    
    current_dir_name = os.path.basename(current_directory)
    target_directory = os.path.join(os.path.dirname(current_directory), f"{current_dir_name}-1")
    
    if os.path.exists(target_directory):
        print(f"\n目标文件夹已存在，直接使用: {target_directory}")
    else:
        print(f"\n创建目标文件夹: {target_directory}")
        os.makedirs(target_directory, exist_ok=True)
    
    print("\n开始复制 webp 文件到目标文件夹...")
    copied_count = copy_webp_files(current_directory, target_directory)
    
    print(f"\n{'='*60}")
    print("转换流程完成")
    print(f"{'='*60}")
    print(f"新转换文件数: {converted_count}")
    print(f"复制文件数: {copied_count}")
    print(f"总记录文件夹数: {len(conversion_record)}")
    
    print(f"\n复制完成！")
    print(f"成功复制: {copied_count} 个 webp 文件")
