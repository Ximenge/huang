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

def convert_to_webp(input_path, dpi=72, quality=75):
    """将单个图片文件转换为 webp 格式
    
    Args:
        input_path: 输入图片路径
        dpi: 目标DPI值，默认72
        quality: WebP质量，0-100，默认75（更小的值意味着更小的文件大小）
    """
    try:
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        output_path = os.path.splitext(input_path)[0] + '.webp'
        
        # 判断图片是否需要压缩
        # 如果宽度低于720或者高度低于1440，则不压缩，直接转换为webp
        if original_width < 720 or original_height < 1440:
            print(f"  图片尺寸过小 ({original_width}x{original_height})，不压缩直接转换")
            # 直接保存为WebP格式，不调整大小
            img.save(output_path, 'webp', quality=quality, dpi=(dpi, dpi))
            
            original_size = os.path.getsize(input_path) / 1024
            webp_size = os.path.getsize(output_path) / 1024
            compression_ratio = (1 - webp_size / original_size) * 100 if original_size > 0 else 0
            
            print(f"已转换: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            print(f"  原始大小: {original_size:.1f}KB, WebP大小: {webp_size:.1f}KB, 压缩率: {compression_ratio:.1f}%")
            return True
        
        # 判断图片方向并调整分辨率
        original_ratio = original_width / original_height if original_height > 0 else 1
        
        if original_height > original_width:
            # 竖屏图片：高度 > 宽度（竖着拿手机）
            # 目标比例选项：宽度x高度
            ratio_1080_1440 = 1080 / 1440  # 0.75
            ratio_960_1440 = 960 / 1440      # 0.667
            
            # 选择更接近原图比例的目标分辨率
            if abs(original_ratio - ratio_1080_1440) <= abs(original_ratio - ratio_960_1440):
                target_size = (1080, 1440)
                print(f"  检测到竖屏图片 ({original_width}x{original_height}, 比例{original_ratio:.3f}) -> 调整为 {target_size[0]}x{target_size[1]}")
            else:
                target_size = (960, 1440)
                print(f"  检测到竖屏图片 ({original_width}x{original_height}, 比例{original_ratio:.3f}) -> 调整为 {target_size[0]}x{target_size[1]}")
        elif original_width > original_height:
            # 横屏图片：宽度 > 高度（横着拿手机）
            # 目标比例选项：宽度x高度
            ratio_1440_720 = 1440 / 720    # 2.0
            ratio_1440_1080 = 1440 / 1080  # 1.333
            
            # 选择更接近原图比例的目标分辨率
            if abs(original_ratio - ratio_1440_720) <= abs(original_ratio - ratio_1440_1080):
                target_size = (1440, 720)
                print(f"  检测到横屏图片 ({original_width}x{original_height}, 比例{original_ratio:.3f}) -> 调整为 {target_size[0]}x{target_size[1]}")
            else:
                target_size = (1440, 1080)
                print(f"  检测到横屏图片 ({original_width}x{original_height}, 比例{original_ratio:.3f}) -> 调整为 {target_size[0]}x{target_size[1]}")
        else:
            # 正方形图片
            target_size = (1080, 1080)
            print(f"  检测到正方形图片 ({original_width}x{original_height}) -> 调整为 {target_size[0]}x{target_size[1]}")
        
        # 调整图片大小
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # 保存为WebP格式，设置DPI
        img_resized.save(output_path, 'webp', quality=quality, dpi=(dpi, dpi))
        
        original_size = os.path.getsize(input_path) / 1024
        webp_size = os.path.getsize(output_path) / 1024
        compression_ratio = (1 - webp_size / original_size) * 100 if original_size > 0 else 0
        
        print(f"已转换: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        print(f"  原始大小: {original_size:.1f}KB, WebP大小: {webp_size:.1f}KB, 压缩率: {compression_ratio:.1f}%")
        return True
    except Exception as e:
        print(f"转换失败 {os.path.basename(input_path)}: {str(e)}")
        return False

def copy_webp_files(source_dir, target_dir):
    """复制目录中的所有 webp 文件到目标目录"""
    copied_files = 0
    
    # 遍历目录及其子目录
    for root, _, files in os.walk(source_dir):
        for file in files:
            # 检查是否为 webp 文件
            if file.lower().endswith('.webp'):
                # 构建源文件路径
                source_path = os.path.join(root, file)
                
                # 构建目标文件路径（保持相对路径结构）
                relative_path = os.path.relpath(root, source_dir)
                if relative_path != '.':
                    target_subdir = os.path.join(target_dir, relative_path)
                    # 创建目标子目录
                    os.makedirs(target_subdir, exist_ok=True)
                    target_path = os.path.join(target_subdir, file)
                else:
                    target_path = os.path.join(target_dir, file)
                
                # 检查目标文件是否存在
                if os.path.exists(target_path):
                    print(f"跳过: {os.path.basename(file)} (目标文件已存在)")
                else:
                    # 复制文件
                    try:
                        shutil.copy2(source_path, target_path)
                        print(f"已复制: {os.path.basename(file)} -> {target_path}")
                        copied_files += 1
                    except Exception as e:
                        print(f"复制失败 {os.path.basename(file)}: {str(e)}")
    
    return copied_files

def batch_convert(directory, record=None, dpi=72, quality=75):
    """批量转换目录中的所有图片文件
    
    Args:
        directory: 要处理的目录
        record: 转换记录字典
        dpi: 目标DPI值，默认72
        quality: WebP质量，0-100，默认75
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
        
        dir_converted_count = 0
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            
            if ext == '.webp':
                continue
                
            if ext in supported_formats:
                total_files += 1
                input_path = os.path.join(root, file)
                
                original_size = os.path.getsize(input_path) / 1024
                total_original_size += original_size
                
                if convert_to_webp(input_path, dpi=dpi, quality=quality):
                    converted_files += 1
                    dir_converted_count += 1
                    
                    webp_path = os.path.splitext(input_path)[0] + '.webp'
                    if os.path.exists(webp_path):
                        total_webp_size += os.path.getsize(webp_path) / 1024
        
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
    
    TARGET_DPI = 72
    WEBP_QUALITY = 75
    
    print(f"开始转换目录: {current_directory}")
    print(f"目标DPI: {TARGET_DPI}")
    print(f"WebP质量: {WEBP_QUALITY}")
    
    json_record_path = os.path.join(current_directory, "conversion_record.json")
    
    print(f"\n加载转换记录: {json_record_path}")
    conversion_record = load_conversion_record(json_record_path)
    print(f"已记录的转换目录数: {len(conversion_record)}")
    
    converted_count = batch_convert(current_directory, conversion_record, dpi=TARGET_DPI, quality=WEBP_QUALITY)
    
    if converted_count > 0:
        save_conversion_record(json_record_path, conversion_record)
    
    # 创建目标文件夹（当前文件夹名后接 -1）
    current_dir_name = os.path.basename(current_directory)
    target_directory = os.path.join(os.path.dirname(current_directory), f"{current_dir_name}-1")
    
    # 检查目标文件夹是否存在
    if os.path.exists(target_directory):
        print(f"\n目标文件夹已存在，直接使用: {target_directory}")
    else:
        print(f"\n创建目标文件夹: {target_directory}")
        os.makedirs(target_directory, exist_ok=True)
    
    # 复制 webp 文件到目标文件夹
    print("\n开始复制 webp 文件到目标文件夹...")
    copied_count = copy_webp_files(current_directory, target_directory)
    
    print(f"\n复制完成！")
    print(f"成功复制: {copied_count} 个 webp 文件")
