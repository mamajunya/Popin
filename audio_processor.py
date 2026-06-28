"""
音频预处理模块：人声分离 + 静音检测切片
用于解决长音频导致的模型幻觉问题
"""

import subprocess
import numpy as np
from pathlib import Path
import json
import wave


class AudioProcessor:
    """音频预处理器"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def separate_vocals(self, audio_path, output_vocal_path):
        """
        使用 Demucs 进行人声分离（GPU 加速）
        这对于准确检测静音点很重要，避免在句子中间切断
        
        Args:
            audio_path: 输入音频路径
            output_vocal_path: 输出人声路径
            
        Returns:
            bool: 是否成功分离
        """
        try:
            print("=" * 60)
            print("正在进行人声分离（GPU 加速）...")
            print(f"输入音频: {audio_path}")
            print(f"输出路径: {output_vocal_path}")
            
            # 创建临时输出目录
            temp_output_dir = self.output_dir / "demucs_output"
            temp_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用 Python demucs 命令行工具
            command = [
                "demucs",
                "--two-stems", "vocals",  # 只分离人声
                "-n", "htdemucs",          # 使用 htdemucs 模型
                "-o", str(temp_output_dir),
                str(audio_path)
            ]
            
            print("执行命令:", " ".join(command))
            print("正在分离人声...")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                print(f"✗ Demucs 执行失败")
                print(f"错误输出: {result.stderr}")
                return False
            
            # 查找输出的人声文件
            audio_name = Path(audio_path).stem
            possible_vocal_paths = [
                temp_output_dir / "htdemucs" / audio_name / "vocals.wav",
                temp_output_dir / "htdemucs" / audio_name / "vocals.mp3",
            ]
            
            vocal_file = None
            for path in possible_vocal_paths:
                if path.exists():
                    vocal_file = path
                    print(f"✓ 找到人声文件: {vocal_file}")
                    break
            
            if vocal_file is None:
                print("✗ 未找到输出的人声文件")
                return False
            
            # 转换为16kHz单声道
            print("正在转换为 16kHz 单声道...")
            self._convert_audio(str(vocal_file), output_vocal_path, sample_rate=16000)
            
            # 清理临时文件
            import shutil
            if temp_output_dir.exists():
                shutil.rmtree(temp_output_dir)
            
            print(f"✓ 人声分离完成: {output_vocal_path}")
            print("=" * 60)
            return True
            
        except FileNotFoundError:
            print("✗ Demucs 未安装")
            print("  请运行: pip install demucs")
            print("=" * 60)
            return False
            
        except Exception as e:
            print(f"✗ 人声分离失败: {e}")
            import traceback
            traceback.print_exc()
            print("=" * 60)
            return False
    
    def _convert_audio(self, input_path, output_path, sample_rate=16000):
        """转换音频格式为 16kHz 单声道 WAV"""
        command = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-ar", str(sample_rate),
            "-ac", "1",
            "-acodec", "pcm_s16le",
            output_path
        ]
        subprocess.run(command, capture_output=True, check=True,
                      encoding='utf-8', errors='replace')
    
    def detect_silence_segments(self, audio_path, min_silence_duration=0.5, 
                               silence_threshold=-40, min_segment_duration=1.0,
                               max_segment_duration=30.0):
        """
        检测音频中的静音片段，用于切分音频
        同时检测并跳过长时间的纯静音段（避免幻觉）
        
        Args:
            audio_path: 音频文件路径
            min_silence_duration: 最小静音持续时间（秒）
            silence_threshold: 静音阈值（dB）
            min_segment_duration: 最小片段时长（秒）
            max_segment_duration: 最大片段时长（秒）
            
        Returns:
            List[Tuple[float, float]]: 音频片段列表 [(start_time, end_time), ...]
                                       只包含有人声的片段
        """
        print("正在检测音频静音片段...")
        
        # 使用 ffmpeg silencedetect 过滤器检测静音
        command = [
            "ffmpeg",
            "-i", audio_path,
            "-af", f"silencedetect=n={silence_threshold}dB:d={min_silence_duration}",
            "-f", "null",
            "-"
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 解析静音检测结果
        silence_starts = []
        silence_ends = []
        
        for line in result.stderr.split('\n'):
            if 'silence_start' in line:
                try:
                    time = float(line.split('silence_start: ')[1].split()[0])
                    silence_starts.append(time)
                except:
                    pass
            elif 'silence_end' in line:
                try:
                    time = float(line.split('silence_end: ')[1].split('|')[0].strip())
                    silence_ends.append(time)
                except:
                    pass
        
        # 获取音频总时长
        duration = self._get_audio_duration(audio_path)
        
        # 构建有声片段列表（反转静音片段）
        voice_segments = []
        
        if not silence_ends:
            # 没有检测到静音，整个音频都是有声的
            current = 0
            while current < duration:
                end = min(current + max_segment_duration, duration)
                if end - current >= min_segment_duration:
                    voice_segments.append((current, end))
                current = end
        else:
            # 配对静音开始和结束，构建有声片段
            # 静音段之间就是有声段
            
            # 添加开头的有声段（如果有）
            if silence_ends and silence_ends[0] > min_segment_duration:
                voice_segments.append((0, silence_ends[0]))
            
            # 处理中间的有声段
            for i in range(len(silence_ends) - 1):
                voice_start = silence_ends[i]
                voice_end = silence_starts[i + 1] if i + 1 < len(silence_starts) else duration
                
                # 检查这段有声音频是否足够长
                if voice_end - voice_start >= min_segment_duration:
                    # 如果有声段太长，进一步切分
                    if voice_end - voice_start > max_segment_duration:
                        temp_start = voice_start
                        while voice_end - temp_start > max_segment_duration:
                            voice_segments.append((temp_start, temp_start + max_segment_duration))
                            temp_start += max_segment_duration
                        if voice_end - temp_start >= min_segment_duration:
                            voice_segments.append((temp_start, voice_end))
                    else:
                        voice_segments.append((voice_start, voice_end))
                else:
                    print(f"  跳过短静音段: {voice_start:.1f}s - {voice_end:.1f}s (时长 {voice_end - voice_start:.1f}s)")
            
            # 添加结尾的有声段（如果有）
            if silence_ends:
                last_silence_end = silence_ends[-1]
                if duration - last_silence_end >= min_segment_duration:
                    voice_segments.append((last_silence_end, duration))
        
        # 统计跳过的时长
        total_duration = duration
        voice_duration = sum(end - start for start, end in voice_segments)
        skipped_duration = total_duration - voice_duration
        
        print(f"检测到 {len(voice_segments)} 个有声片段")
        print(f"总时长: {total_duration:.1f}s")
        print(f"有声时长: {voice_duration:.1f}s ({voice_duration/total_duration*100:.1f}%)")
        print(f"跳过静音: {skipped_duration:.1f}s ({skipped_duration/total_duration*100:.1f}%)")
        
        return voice_segments
    
    def _get_audio_duration(self, audio_path):
        """获取音频时长"""
        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        try:
            return float(result.stdout.strip())
        except:
            return 0.0
    
    def split_audio(self, audio_path, segments):
        """
        根据时间片段切分音频
        
        Args:
            audio_path: 音频文件路径
            segments: 片段列表 [(start, end), ...]
            
        Returns:
            List[Tuple[str, float, float]]: [(片段文件路径, 开始时间, 结束时间), ...]
        """
        print("正在切分音频...")
        segment_files = []
        
        for i, (start, end) in enumerate(segments):
            segment_path = self.output_dir / f"segment_{i:04d}.wav"
            
            command = [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-ss", str(start),
                "-to", str(end),
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                str(segment_path)
            ]
            
            subprocess.run(
                command,
                capture_output=True,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            
            segment_files.append((str(segment_path), start, end))
        
        print(f"音频切分完成，共 {len(segment_files)} 个片段")
        return segment_files
    
    def load_filter_patterns(self):
        """从配置文件加载过滤规则"""
        config_file = Path("hallucination_filters.json")
        
        # 默认规则（如果配置文件不存在）
        default_patterns = [
            # 日语常见幻觉
            r'ご視聴ありがとうございました',
            r'ご視聴ありがとうございます',
            r'ありがとうございました',
            r'チャンネル登録',
            r'高評価',
            r'コメント',
            r'よろしくお願いします',
            r'またね',
            r'バイバイ',
            # 英语常见幻觉
            r'see you',
            r'bye bye',
            r'thank you for watching',
            r'thanks for watching',
            r'subscribe',
            # 制作信息
            r'字幕by',
            r'翻訳:',
            r'製作:',
            r'制作:',
            r'監督:',
            r'声優:',
            r'cast:',
            r'staff:',
            # 背景音乐
            r'音楽',
            r'BGM',
            r'ミュージック',
            r'music',
            # 噪音
            r'\.\.\.+$',
            r'^[\s\.,，。、]*$',
            r'^(あ|ああ|ああ+|ん|んん+|えー+|うー+)$',
        ]
        
        if not config_file.exists():
            return default_patterns
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if not config.get('enabled', True):
                return []
            
            patterns = []
            for category, settings in config.get('filters', {}).items():
                if settings.get('enabled', True):
                    patterns.extend(settings.get('patterns', []))
            
            # 过滤掉示例规则
            patterns = [p for p in patterns if not p.startswith('例:')]
            
            return patterns if patterns else default_patterns
            
        except Exception as e:
            print(f"⚠️  加载过滤规则失败，使用默认规则: {e}")
            return default_patterns
    
    def filter_hallucination_subtitles(self, subtitles):
        """
        过滤幻觉字幕
        
        Args:
            subtitles: 字幕列表 [{'start': ..., 'end': ..., 'text': ...}, ...]
            
        Returns:
            过滤后的字幕列表
        """
        # 从配置文件加载过滤规则
        hallucination_patterns = self.load_filter_patterns()
        
        import re
        filtered = []
        filtered_count = 0
        
        for sub in subtitles:
            text = sub['text'].strip()
            
            # 检查是否匹配幻觉模式
            is_hallucination = False
            for pattern in hallucination_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    is_hallucination = True
                    filtered_count += 1
                    print(f"  🗑️  过滤幻觉字幕: \"{text}\"")
                    break
            
            # 检查是否为过短的字幕（可能是噪音）
            if not is_hallucination and len(text) == 0:
                is_hallucination = True
                filtered_count += 1
            
            if not is_hallucination:
                filtered.append(sub)
        
        if filtered_count > 0:
            print(f"✓ 共过滤 {filtered_count} 条幻觉字幕")
        
        return filtered
    
    def merge_srt_segments(self, srt_segments_with_offset, output_srt_path):
        """
        合并多个 SRT 片段，调整时间偏移，并过滤幻觉字幕
        
        Args:
            srt_segments_with_offset: [(srt_path, time_offset), ...]
            output_srt_path: 输出 SRT 文件路径
        """
        print("正在合并字幕片段...")
        
        all_subtitles = []
        
        for srt_path, time_offset in srt_segments_with_offset:
            if not Path(srt_path).exists():
                continue
            
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 SRT
            import re
            pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n((?:.*\n?)+?)(?=\n\d+\n|\Z)'
            matches = re.findall(pattern, content, re.MULTILINE)
            
            for match in matches:
                index, start_time, end_time, text = match
                
                # 调整时间偏移
                new_start = self._add_time_offset(start_time, time_offset)
                new_end = self._add_time_offset(end_time, time_offset)
                
                all_subtitles.append({
                    'start': new_start,
                    'end': new_end,
                    'text': text.strip()
                })
        
        # 按时间排序
        all_subtitles.sort(key=lambda x: self._time_to_seconds(x['start']))
        
        # 过滤幻觉字幕
        print("\n检查并过滤幻觉字幕...")
        all_subtitles = self.filter_hallucination_subtitles(all_subtitles)
        
        # 写入合并后的 SRT
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            for i, subtitle in enumerate(all_subtitles, 1):
                f.write(f"{i}\n")
                f.write(f"{subtitle['start']} --> {subtitle['end']}\n")
                f.write(f"{subtitle['text']}\n\n")
        
        print(f"字幕合并完成: {output_srt_path}")
        return output_srt_path
    
    def _add_time_offset(self, time_str, offset_seconds):
        """
        给 SRT 时间戳添加偏移
        
        Args:
            time_str: "HH:MM:SS,mmm" 格式
            offset_seconds: 偏移秒数
            
        Returns:
            str: 新的时间戳
        """
        total_seconds = self._time_to_seconds(time_str)
        new_total = total_seconds + offset_seconds
        
        hours = int(new_total // 3600)
        minutes = int((new_total % 3600) // 60)
        seconds = int(new_total % 60)
        milliseconds = int((new_total % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _time_to_seconds(self, time_str):
        """将 SRT 时间戳转换为秒数"""
        # "HH:MM:SS,mmm" -> seconds
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        
        return h * 3600 + m * 60 + s + ms / 1000.0
    
    def cleanup_temp_files(self, keep_patterns=None):
        """清理临时文件"""
        if keep_patterns is None:
            keep_patterns = []
        
        for file in self.output_dir.glob("segment_*.wav"):
            file.unlink()
        
        for file in self.output_dir.glob("segment_*.srt"):
            file.unlink()
        
        # 清理 demucs 输出
        demucs_dir = self.output_dir / "htdemucs"
        if demucs_dir.exists():
            import shutil
            shutil.rmtree(demucs_dir)
        
        print("临时文件清理完成")
