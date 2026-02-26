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

def convert_to_webp(input_path):
    """将单个图片文件转换为 webp 格式"""
    try:
        # 打开图片
        img = Image.open(input_path)
        
        # 创建输出路径（保持文件名不变，只改扩展名）
        output_path = os.path.splitext(input_path)[0] + '.webp'
        
        # 转换并保存
        img.save(output_path, 'webp', quality=85)
        
        print(f"已转换: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
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

def batch_convert(directory, record=None):
    """批量转换目录中的所有图片文件"""
    # 支持的图片格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    
    total_files = 0
    converted_files = 0
    converted_dirs = 0
    
    # 遍历目录及其子目录
    for root, _, files in os.walk(directory):
        # 检查是否是根目录（跳过根目录本身）
        if root == directory:
            continue
            
        # 检查该目录是否已转换过
        if record is not None and is_directory_converted(record, root):
            print(f"跳过已转换的目录: {root}")
            continue
        
        # 处理当前目录中的图片文件
        dir_converted_count = 0
        for file in files:
            # 获取文件扩展名
            ext = os.path.splitext(file)[1].lower()
            
            # 跳过 webp 文件
            if ext == '.webp':
                continue
                
            # 检查是否为支持的图片格式
            if ext in supported_formats:
                total_files += 1
                input_path = os.path.join(root, file)
                if convert_to_webp(input_path):
                    converted_files += 1
                    dir_converted_count += 1
        
        # 如果该目录有转换的文件，记录转换信息
        if dir_converted_count > 0 and record is not None:
            # 计算目标目录路径
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
    
    return converted_files

if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"开始转换目录: {current_directory}")
    
    # 定义JSON记录文件路径
    json_record_path = os.path.join(current_directory, "conversion_record.json")
    
    # 加载转换记录
    print(f"\n加载转换记录: {json_record_path}")
    conversion_record = load_conversion_record(json_record_path)
    print(f"已记录的转换目录数: {len(conversion_record)}")
    
    # 执行批量转换
    converted_count = batch_convert(current_directory, conversion_record)
    
    # 保存转换记录
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
