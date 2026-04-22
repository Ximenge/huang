#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

class R2Uploader:
    def __init__(self, local_dir, r2_bucket, r2_remote="r2"):
        self.local_dir = Path(local_dir)
        self.r2_bucket = r2_bucket
        self.r2_remote = r2_remote
        self.r2_path = f"{r2_remote}:{r2_bucket}"
    
    def upload_video(self, video_folder):
        video_path = self.local_dir / video_folder
        if not video_path.exists():
            print(f"Video folder not found: {video_folder}")
            return None
        
        print(f"Uploading video: {video_folder}")
        
        # 读取元数据
        metadata_file = video_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {'name': video_folder}
        
        # 上传到R2
        remote_path = f"{self.r2_path}/videos/{video_folder}"
        
        try:
            # 使用rclone上传整个文件夹
            cmd = [
                'rclone',
                'sync',
                str(video_path),
                remote_path,
                '--progress',
                '--transfers', '4',
                '--checkers', '8'
            ]
            
            subprocess.run(cmd, check=True)
            print(f"Successfully uploaded {video_folder} to R2")
            
            # 更新元数据中的R2路径
            metadata['r2_path'] = f"videos/{video_folder}"
            metadata['r2_bucket'] = self.r2_bucket
            metadata['hls_url'] = f"https://pub-{self.r2_bucket.replace('bucket-', '')}.r2.dev/videos/{video_folder}/playlist.m3u8"
            
            return metadata
            
        except subprocess.CalledProcessError as e:
            print(f"Error uploading {video_folder}: {e}")
            return None
    
    def upload_all_videos(self):
        if not self.local_dir.exists():
            print(f"Local directory not found: {self.local_dir}")
            return []
        
        video_folders = [f for f in self.local_dir.iterdir() if f.is_dir() and not f.name.startswith('.')]
        
        if not video_folders:
            print("No video folders found in local directory")
            return []
        
        print(f"Found {len(video_folders)} video folders to upload")
        
        all_metadata = []
        for video_folder in video_folders:
            metadata = self.upload_video(video_folder.name)
            if metadata:
                all_metadata.append(metadata)
        
        # 保存所有视频的元数据
        metadata_file = self.local_dir / "r2_uploaded_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"All videos uploaded. Metadata saved to {metadata_file}")
        return all_metadata
    
    def upload_metadata_to_project(self, metadata_file, project_dir):
        metadata_path = Path(metadata_file)
        if not metadata_path.exists():
            print(f"Metadata file not found: {metadata_file}")
            return False
        
        project_path = Path(project_dir)
        videos_metadata_dir = project_path / "src" / "data" / "videos"
        videos_metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制元数据文件到项目
        target_file = videos_metadata_dir / "videos_metadata.json"
        shutil.copy(metadata_path, target_file)
        
        print(f"Metadata copied to {target_file}")
        return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload HLS videos to Cloudflare R2')
    parser.add_argument('--local', '-l', required=True, help='Local directory containing HLS files')
    parser.add_argument('--bucket', '-b', required=True, help='Cloudflare R2 bucket name')
    parser.add_argument('--remote', '-r', default='r2', help='Rclone remote name (default: r2)')
    parser.add_argument('--project', '-p', help='Project directory to copy metadata to')
    
    args = parser.parse_args()
    
    uploader = R2Uploader(args.local, args.bucket, args.remote)
    all_metadata = uploader.upload_all_videos()
    
    if args.project and all_metadata:
        metadata_file = Path(args.local) / "r2_uploaded_metadata.json"
        uploader.upload_metadata_to_project(metadata_file, args.project)
