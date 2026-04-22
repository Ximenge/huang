#!/usr/bin/env python3
import os
import subprocess
import json
import shutil
from pathlib import Path

class VideoProcessor:
    def __init__(self, input_dir, output_dir, segment_duration=10):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.segment_duration = segment_duration
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_video(self, video_file):
        video_path = self.input_dir / video_file
        video_name = video_path.stem
        output_folder = self.output_dir / video_name
        output_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing video: {video_file}")
        
        # 生成HLS切片
        self._generate_hls(video_path, output_folder)
        
        # 生成视频元数据
        metadata = self._generate_metadata(video_path, video_name)
        
        # 保存元数据
        metadata_file = output_folder / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"Video processed successfully: {video_name}")
        return metadata
    
    def _generate_hls(self, video_path, output_folder):
        m3u8_file = output_folder / "playlist.m3u8"
        
        # ffmpeg命令生成HLS切片
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-f', 'hls',
            '-hls_time', str(self.segment_duration),
            '-hls_list_size', '0',
            '-hls_segment_filename', f'{output_folder}/segment_%03d.ts',
            str(m3u8_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"HLS segments generated for {video_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing video: {e}")
            print(f"stderr: {e.stderr}")
            raise
    
    def _generate_metadata(self, video_path, video_name):
        # 获取视频信息
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            
            # 提取关键信息
            duration = float(video_info['format']['duration'])
            size = int(video_info['format']['size'])
            
            # 查找视频流
            video_stream = None
            audio_stream = None
            for stream in video_info['streams']:
                if stream['codec_type'] == 'video' and video_stream is None:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            metadata = {
                'name': video_name,
                'original_file': video_path.name,
                'duration': duration,
                'size': size,
                'hls_playlist': 'playlist.m3u8',
                'segment_duration': self.segment_duration,
                'total_segments': int(duration // self.segment_duration) + 1
            }
            
            if video_stream:
                metadata['video'] = {
                    'codec': video_stream.get('codec_name'),
                    'width': video_stream.get('width'),
                    'height': video_stream.get('height'),
                    'bitrate': video_stream.get('bit_rate')
                }
            
            if audio_stream:
                metadata['audio'] = {
                    'codec': audio_stream.get('codec_name'),
                    'sample_rate': audio_stream.get('sample_rate'),
                    'channels': audio_stream.get('channels')
                }
            
            return metadata
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting video metadata: {e}")
            return {
                'name': video_name,
                'original_file': video_path.name,
                'error': str(e)
            }
    
    def process_all_videos(self):
        video_files = list(self.input_dir.glob('*.mp4')) + list(self.input_dir.glob('*.mkv')) + list(self.input_dir.glob('*.avi'))
        
        if not video_files:
            print("No video files found in input directory")
            return []
        
        print(f"Found {len(video_files)} video files to process")
        
        all_metadata = []
        for video_file in video_files:
            try:
                metadata = self.process_video(video_file.name)
                all_metadata.append(metadata)
            except Exception as e:
                print(f"Failed to process {video_file.name}: {e}")
        
        # 保存所有视频的元数据
        all_metadata_file = self.output_dir / "all_videos_metadata.json"
        with open(all_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"All videos processed. Metadata saved to {all_metadata_file}")
        return all_metadata

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process videos to HLS format')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing video files')
    parser.add_argument('--output', '-o', required=True, help='Output directory for HLS files')
    parser.add_argument('--segment-duration', '-s', type=int, default=10, help='Segment duration in seconds')
    
    args = parser.parse_args()
    
    processor = VideoProcessor(args.input, args.output, args.segment_duration)
    processor.process_all_videos()
