#!/usr/bin/env python3
"""
视频处理脚本 - 支持二级目录结构
将video文件夹中的视频批量处理为HLS格式，输出到video-1文件夹

目录结构：
video/
├── 视频分组名称/        # 一级子目录 → 视频分组
│   └── 博文标题/        # 二级子目录 → 博文标题
│       └── video.mp4    # 视频文件

输出：
video-1/
├── 视频分组名称/
│   └── 博文标题/
│       └── video/
│           ├── playlist.m3u8
│           └── segment_xxx.ts
│       └── metadata.json
"""
import os
import subprocess
import json
from pathlib import Path

# 配置
VIDEO_SOURCE_DIR = r"C:\huang\video"           # 源视频文件夹
VIDEO_OUTPUT_DIR = r"C:\huang\video-1"         # 输出文件夹
CONVERSION_RECORD_FILE = r"C:\huang\video_conversion_record.json"  # 转换记录文件
SEGMENT_DURATION = 10                           # HLS切片时长（秒）

# 支持的视频格式
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv'}


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


def add_conversion_record(record, dir_path, converted_count, target_dir, group_name, post_title):
    """添加转换记录"""
    record[dir_path] = {
        "converted_count": converted_count,
        "target_directory": target_dir,
        "group_name": group_name,
        "post_title": post_title,
        "timestamp": os.path.getmtime(dir_path) if os.path.exists(dir_path) else None
    }


def convert_folder_name(folder_name):
    """转换文件夹名称（空格替换为连字符）"""
    return folder_name.replace(' ', '-')


def get_video_files(folder_path):
    """获取文件夹中的所有视频文件"""
    video_files = []
    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_VIDEO_FORMATS:
                    video_files.append(file)
    except Exception as e:
        print(f"      读取文件夹失败: {str(e)}")
    return sorted(video_files)


def get_video_info(video_path):
    """获取视频信息"""
    video_info = {
        "name": Path(video_path).stem,
        "original_file": os.path.basename(video_path),
    }
    
    try:
        file_size = os.path.getsize(video_path)
        video_info["size"] = file_size
        
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            info = json.loads(result.stdout)
            if 'format' in info:
                if 'duration' in info['format']:
                    video_info["duration"] = float(info['format']['duration'])
            
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_info["width"] = stream.get('width')
                    video_info["height"] = stream.get('height')
                    video_info["codec"] = stream.get('codec_name')
                    break
    except Exception:
        pass
    
    return video_info


def process_video_to_hls(input_path, output_folder, segment_duration=10):
    """
    将单个视频文件转换为HLS格式
    
    Args:
        input_path: 输入视频路径
        output_folder: 输出文件夹路径
        segment_duration: 切片时长（秒）
    
    Returns:
        bool: 是否成功
    """
    try:
        video_name = Path(input_path).stem
        
        video_output_folder = os.path.join(output_folder, video_name)
        os.makedirs(video_output_folder, exist_ok=True)
        
        m3u8_file = os.path.join(video_output_folder, "playlist.m3u8")
        
        if os.path.exists(m3u8_file):
            print(f"        跳过: {os.path.basename(input_path)} (HLS文件已存在)")
            return True, video_name
        
        print(f"        正在处理: {os.path.basename(input_path)}")
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', '1000k',
            '-c:a', 'aac',
            '-vf', 'scale=-2:1080',
            '-f', 'hls',
            '-hls_time', str(segment_duration),
            '-hls_list_size', '0',
            '-hls_segment_filename', f'{video_output_folder}/segment_%03d.ts',
            str(m3u8_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print(f"        [OK] 转换成功: {os.path.basename(input_path)} -> {video_name}/")
            return True, video_name
        else:
            print(f"        [FAIL] 转换失败: {os.path.basename(input_path)}")
            print(f"        错误: {result.stderr[:200]}")
            return False, video_name
            
    except Exception as e:
        print(f"        [ERROR] 处理异常 {os.path.basename(input_path)}: {str(e)}")
        return False, None


def extract_video_cover(input_path, output_folder):
    """
    从视频中提取封面图片（第1秒的画面）
    
    Args:
        input_path: 输入视频路径
        output_folder: 输出文件夹路径
    
    Returns:
        str: 封面文件名，失败返回 None
    """
    try:
        video_name = Path(input_path).stem
        cover_filename = f"{video_name}_cover.jpg"
        cover_path = os.path.join(output_folder, cover_filename)
        
        # 如果封面已存在，跳过
        if os.path.exists(cover_path):
            print(f"        跳过封面提取: {cover_filename} (已存在)")
            return cover_filename
        
        print(f"        正在提取封面: {cover_filename}")
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ss', '00:00:01',  # 第1秒
            '-vframes', '1',     # 提取1帧
            '-q:v', '2',         # 图片质量
            str(cover_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0 and os.path.exists(cover_path):
            print(f"        [OK] 封面提取成功: {cover_filename}")
            return cover_filename
        else:
            print(f"        [FAIL] 封面提取失败: {os.path.basename(input_path)}")
            return None
            
    except Exception as e:
        print(f"        [ERROR] 封面提取异常: {str(e)}")
        return None


def generate_post_metadata(output_folder, video_files_info, group_name, post_title, cover_file=None):
    """生成博文的元数据"""
    metadata = {
        "group_name": group_name,
        "post_title": post_title,
        "video_count": len(video_files_info),
        "videos": video_files_info
    }
    
    # 添加封面信息
    if cover_file:
        metadata["cover"] = cover_file
    
    metadata_file = os.path.join(output_folder, "metadata.json")
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"      元数据已保存: {metadata_file}")
    except Exception as e:
        print(f"      警告: 无法保存元数据: {str(e)}")
    
    return metadata


def process_second_level_folder(source_folder, output_folder, group_name, post_title, record):
    """
    处理二级子目录（博文目录）
    
    Args:
        source_folder: 源视频文件夹路径（二级子目录）
        output_folder: 输出文件夹路径
        group_name: 视频分组名称
        post_title: 博文标题
        record: 转换记录字典
    
    Returns:
        int: 成功处理的视频数量
    """
    print(f"    处理博文: {post_title}")
    
    if is_directory_converted(record, source_folder):
        print(f"      [SKIP] 跳过已转换的目录: {post_title}")
        return 0
    
    video_files = get_video_files(source_folder)
    
    if not video_files:
        print(f"      [SKIP] 未找到视频文件: {post_title}")
        return 0
    
    print(f"      找到 {len(video_files)} 个视频文件")
    
    os.makedirs(output_folder, exist_ok=True)
    
    converted_count = 0
    video_files_info = []
    cover_file = None
    
    for video_file in video_files:
        input_path = os.path.join(source_folder, video_file)
        success, video_name = process_video_to_hls(input_path, output_folder, SEGMENT_DURATION)
        
        if success and video_name:
            converted_count += 1
            video_info = get_video_info(input_path)
            video_info["hls_playlist"] = f"{video_name}/playlist.m3u8"
            video_files_info.append(video_info)
            
            # 提取第一个视频的封面作为博文封面
            if cover_file is None:
                cover_file = extract_video_cover(input_path, output_folder)
    
    if converted_count > 0:
        generate_post_metadata(output_folder, video_files_info, group_name, post_title, cover_file)
        add_conversion_record(record, source_folder, converted_count, output_folder, group_name, post_title)
    
    print(f"      完成: {converted_count}/{len(video_files)} 个视频处理成功")
    
    return converted_count


def process_first_level_folder(source_folder, output_base_dir, group_name, record):
    """
    处理一级子目录（视频分组）
    
    Args:
        source_folder: 源视频文件夹路径（一级子目录）
        output_base_dir: 输出基础目录
        group_name: 视频分组名称
        record: 转换记录字典
    
    Returns:
        tuple: (成功处理的视频数量, 处理的博文数量)
    """
    converted_group_name = convert_folder_name(group_name)
    output_group_folder = os.path.join(output_base_dir, converted_group_name)
    
    print(f"\n  处理视频分组: {group_name}")
    print(f"  输出目录: {converted_group_name}")
    
    second_level_folders = []
    try:
        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)
            if os.path.isdir(item_path):
                second_level_folders.append(item)
    except Exception as e:
        print(f"    错误: 无法读取目录: {str(e)}")
        return 0, 0
    
    if not second_level_folders:
        print(f"    [SKIP] 未找到二级子目录: {group_name}")
        return 0, 0
    
    print(f"    发现 {len(second_level_folders)} 个博文目录")
    
    os.makedirs(output_group_folder, exist_ok=True)
    
    total_converted = 0
    processed_posts = 0
    
    for post_title in sorted(second_level_folders):
        post_source_folder = os.path.join(source_folder, post_title)
        converted_post_title = convert_folder_name(post_title)
        post_output_folder = os.path.join(output_group_folder, converted_post_title)
        
        converted = process_second_level_folder(
            post_source_folder, 
            post_output_folder, 
            group_name, 
            post_title, 
            record
        )
        
        if converted > 0:
            total_converted += converted
            processed_posts += 1
    
    return total_converted, processed_posts


def batch_process_videos(source_dir, output_dir, record):
    """
    批量处理视频
    
    Args:
        source_dir: 源视频文件夹根目录
        output_dir: 输出文件夹根目录
        record: 转换记录字典
    
    Returns:
        tuple: (处理的总视频数, 处理的博文数, 处理的分组数)
    """
    total_videos = 0
    total_posts = 0
    total_groups = 0
    
    if not os.path.exists(source_dir):
        print(f"错误: 源目录不存在: {source_dir}")
        return 0, 0, 0
    
    os.makedirs(output_dir, exist_ok=True)
    
    first_level_folders = []
    try:
        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)
            if os.path.isdir(item_path):
                first_level_folders.append(item)
    except Exception as e:
        print(f"错误: 无法读取源目录: {str(e)}")
        return 0, 0, 0
    
    print(f"\n发现 {len(first_level_folders)} 个视频分组")
    print("=" * 60)
    
    for group_name in sorted(first_level_folders):
        group_source_folder = os.path.join(source_dir, group_name)
        
        converted, posts = process_first_level_folder(
            group_source_folder, 
            output_dir, 
            group_name, 
            record
        )
        
        if converted > 0:
            total_videos += converted
            total_posts += posts
            total_groups += 1
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print(f"处理视频分组: {total_groups}")
    print(f"处理博文: {total_posts}")
    print(f"成功处理视频: {total_videos}")
    
    return total_videos, total_posts, total_groups


def main():
    """主函数"""
    print("=" * 60)
    print("视频批量处理脚本 (HLS格式) - 二级目录结构")
    print("=" * 60)
    print(f"源文件夹: {VIDEO_SOURCE_DIR}")
    print(f"输出文件夹: {VIDEO_OUTPUT_DIR}")
    print(f"切片时长: {SEGMENT_DURATION}秒")
    print("=" * 60)
    
    print(f"\n加载转换记录: {CONVERSION_RECORD_FILE}")
    conversion_record = load_conversion_record(CONVERSION_RECORD_FILE)
    print(f"已记录的转换目录数: {len(conversion_record)}")
    
    converted_count, post_count, group_count = batch_process_videos(
        VIDEO_SOURCE_DIR, 
        VIDEO_OUTPUT_DIR, 
        conversion_record
    )
    
    if converted_count > 0:
        save_conversion_record(CONVERSION_RECORD_FILE, conversion_record)
    
    print("\n" + "=" * 60)
    print("全部完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
