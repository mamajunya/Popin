import subprocess
import os
from pathlib import Path
import json
from audio_processor import AudioProcessor

class VideoSubtitleGeneratorCpp:
    """使用 whisper.cpp 的视频自动字幕生成器（更快）"""
    
    def __init__(self, whisper_cpp_path, model_path, gpu_backend=None):
        """
        初始化字幕生成器
        
        Args:
            whisper_cpp_path: whisper.cpp 主程序路径（whisper-cli.exe, main.exe 或 main）
            model_path: 模型文件路径（.bin 文件）
            gpu_backend: GPU 后端 (None, 'cuda', 'vulkan', 'opencl', 'metal')
        """
        self.whisper_cpp_path = Path(whisper_cpp_path)
        self.model_path = Path(model_path)
        self.gpu_backend = gpu_backend
        
        # 检查新旧版本的可执行文件
        if not self.whisper_cpp_path.exists():
            # 尝试查找新版本的 whisper-cli.exe
            if self.whisper_cpp_path.name == "main.exe":
                new_path = self.whisper_cpp_path.parent / "whisper-cli.exe"
                if new_path.exists():
                    print(f"检测到新版本，使用 whisper-cli.exe 代替 main.exe")
                    self.whisper_cpp_path = new_path
                else:
                    raise FileNotFoundError(f"whisper.cpp 主程序不存在: {whisper_cpp_path}\n提示: 新版本使用 whisper-cli.exe")
            else:
                raise FileNotFoundError(f"whisper.cpp 主程序不存在: {whisper_cpp_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        print(f"使用 whisper.cpp: {self.whisper_cpp_path}")
        print(f"使用模型: {self.model_path}")
        if gpu_backend:
            print(f"GPU 加速: {gpu_backend.upper()}")
    
    def extract_audio(self, video_path, audio_path="temp_audio.wav"):
        """
        从视频中提取音频
        注意：如果启用人声分离，需要提取立体声；否则提取单声道
        
        Args:
            video_path: 视频文件路径
            audio_path: 输出音频文件路径
        """
        print(f"正在从视频中提取音频: {video_path}")
        # 提取立体声44.1kHz（demucs需要）
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "44100", "-ac", "2",  # 立体声，44.1kHz
            audio_path
        ]
        subprocess.run(command, check=True, capture_output=True, 
                      encoding='utf-8', errors='replace')
        print(f"音频提取完成: {audio_path}")
        return audio_path
    
    def transcribe_audio(self, audio_path, language=None, threads=4, gpu_layers=0):
        """
        使用 whisper.cpp 识别音频内容
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（如 'zh', 'en'）
            threads: 使用的 CPU 线程数
            gpu_layers: GPU 处理的层数（0=仅CPU，-1=全部GPU）
        """
        print("正在使用 whisper.cpp 识别音频内容...")
        
        # 输出 JSON 格式的临时文件
        output_json = Path(audio_path).parent / "temp_output.json"
        
        # 构建命令
        command = [
            str(self.whisper_cpp_path),
            "-m", str(self.model_path),
            "-f", str(audio_path),
            "-t", str(threads),
            "-oj",  # 输出 JSON 格式
            "-of", str(output_json.with_suffix('')),  # 输出文件前缀（不含扩展名）
        ]
        
        # 添加 GPU 参数
        if self.gpu_backend and gpu_layers != 0:
            command.extend(["-ngl", str(gpu_layers)])  # GPU layers
        
        # 添加语言参数
        if language:
            command.extend(["-l", language])
        
        # 运行 whisper.cpp
        print(f"执行命令: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode != 0:
            print(f"错误输出: {result.stderr}")
            raise RuntimeError(f"whisper.cpp 执行失败: {result.stderr}")
        
        print("音频识别完成！")
        
        # 读取 JSON 结果
        try:
            with open(output_json, 'r', encoding='utf-8') as f:
                transcription = json.load(f)
            output_json.unlink()  # 删除临时文件
            return transcription
        except Exception as e:
            print(f"警告: 无法读取 JSON 输出，尝试使用 SRT 输出: {e}")
            return None
    
    def transcribe_audio_srt(self, audio_path, output_srt, language=None, threads=4, gpu_layers=0):
        """
        使用 whisper.cpp 直接生成 SRT 字幕文件
        
        Args:
            audio_path: 音频文件路径
            output_srt: 输出 SRT 文件路径
            language: 语言代码（重要：必须指定正确的语言）
            threads: CPU 线程数
            gpu_layers: GPU 处理的层数（0=禁用GPU，其他值=启用GPU）
        """
        print("正在使用 whisper.cpp 生成字幕...")
        
        # 使用临时文件名避免特殊字符问题
        temp_output_dir = Path(audio_path).parent
        temp_prefix = temp_output_dir / "temp_subtitle"
        
        # 构建命令（直接输出 SRT）
        command = [
            str(self.whisper_cpp_path),
            "-m", str(self.model_path),
            "-f", str(audio_path),
            "-t", str(threads),
            "-osrt",  # 输出 SRT 格式
            "-of", str(temp_prefix),  # 使用临时文件名前缀
        ]
        
        # GPU 参数处理（新版 whisper-cli 的方式）
        # 注意：新版本默认启用 GPU，使用 --no-gpu 来禁用
        if gpu_layers == 0:
            # 禁用 GPU
            command.append("--no-gpu")
            print("已禁用 GPU，使用 CPU 计算")
        else:
            # 启用 GPU（默认行为，无需额外参数）
            if self.gpu_backend:
                print(f"已启用 GPU 加速 ({self.gpu_backend.upper()})")
        
        # 语言参数（重要！）
        if language:
            command.extend(["-l", language])
            print(f"指定语言: {language}")
        else:
            # 如果未指定语言，使用自动检测
            print("使用自动语言检测（可能不准确，建议指定语言）")
        
        print(f"执行命令: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, encoding='utf-8', errors='replace')
        
        # 打印输出以便调试
        if result.stdout:
            print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
        
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else result.stdout
            raise RuntimeError(f"whisper.cpp 执行失败: {error_msg}")
        
        # 将临时文件移动到目标位置
        temp_srt = Path(str(temp_prefix) + ".srt")
        if temp_srt.exists():
            import shutil
            try:
                shutil.move(str(temp_srt), str(output_srt))
                print(f"字幕文件生成完成: {output_srt}")
            except Exception as e:
                raise RuntimeError(f"移动字幕文件失败: {e}")
        else:
            # 列出目录中的文件以便调试
            print(f"查找临时文件: {temp_srt}")
            print(f"目录内容: {list(temp_output_dir.glob('temp_subtitle*'))}")
            raise RuntimeError(f"未找到生成的字幕文件: {temp_srt}")
    
    def add_subtitles_to_video(self, video_path, srt_path, output_path, 
                              font_size=24, font_name="Arial", 
                              margin_v=25, margin_h=0, 
                              primary_color="&HFFFFFF", outline_color="&H000000",
                              outline_width=2, bold=False, italic=False):
        """
        将字幕嵌入到视频中
        
        Args:
            video_path: 原视频路径
            srt_path: 字幕文件路径
            output_path: 输出视频路径
            font_size: 字体大小
            font_name: 字体名称
            margin_v: 垂直边距（底部）
            margin_h: 水平边距
            primary_color: 主颜色（ASS格式，如 &HFFFFFF 白色）
            outline_color: 描边颜色（ASS格式）
            outline_width: 描边宽度（1-5）
            bold: 是否粗体
            italic: 是否斜体
        """
        print(f"正在将字幕嵌入视频...")
        
        # 处理自定义字体名称（移除"自定义: "前缀）
        if font_name.startswith("自定义: "):
            font_name = font_name.replace("自定义: ", "")
        
        # 使用临时文件名避免特殊字符问题
        import shutil
        import uuid
        
        temp_dir = Path(srt_path).parent
        temp_id = uuid.uuid4().hex[:8]
        
        # 临时字幕文件
        temp_srt = temp_dir / f"temp_sub_{temp_id}.srt"
        # 临时输出视频
        temp_output = temp_dir / f"temp_output_{temp_id}.mp4"
        
        try:
            # 复制字幕到临时文件
            shutil.copy(str(srt_path), str(temp_srt))
            
            # 构建字幕样式参数
            style_params = []
            style_params.append(f"FontSize={font_size}")
            style_params.append(f"FontName={font_name}")
            style_params.append(f"MarginV={margin_v}")
            style_params.append(f"MarginH={margin_h}")
            style_params.append(f"PrimaryColour={primary_color}")
            style_params.append(f"OutlineColour={outline_color}")
            style_params.append(f"Outline={outline_width}")
            style_params.append(f"Bold={'1' if bold else '0'}")
            style_params.append(f"Italic={'1' if italic else '0'}")
            
            # 组合样式
            force_style = ",".join(style_params)
            
            # 使用临时文件名执行 FFmpeg
            command = [
                "ffmpeg", "-y", 
                "-i", str(video_path),
                "-vf", f"subtitles={temp_srt.name}:force_style='{force_style}'",
                "-c:a", "copy",
                str(temp_output)
            ]
            
            print(f"执行 FFmpeg 命令...")
            print(f"字幕样式: 字体={font_name} 大小={font_size} 底边距={margin_v} 颜色={primary_color} 描边={outline_color} 宽度={outline_width}")
            # 在字幕文件所在目录执行命令
            result = subprocess.run(command, cwd=str(temp_dir), check=True, 
                                   capture_output=True, encoding='utf-8', errors='replace')
            
            # 移动到最终位置
            shutil.move(str(temp_output), str(output_path))
            print(f"字幕视频生成完成: {output_path}")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg 执行失败:\n"
            error_msg += f"返回码: {e.returncode}\n"
            if e.stderr:
                error_msg += f"错误输出:\n{e.stderr[-500:]}"  # 只显示最后500字符
            print(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            print(f"字幕嵌入失败: {str(e)}")
            raise
        finally:
            # 清理临时文件
            if temp_srt.exists():
                temp_srt.unlink()
            if temp_output.exists():
                temp_output.unlink()
    
    def preview_subtitle_frame(self, video_path, srt_path, output_image, 
                               timestamp=30, font_size=24, font_name="Arial",
                               margin_v=25, margin_h=0,
                               primary_color="&HFFFFFF", outline_color="&H000000",
                               bold=False, italic=False):
        """
        生成带字幕的预览帧
        
        Args:
            video_path: 视频文件路径
            srt_path: 字幕文件路径
            output_image: 输出图片路径
            timestamp: 提取帧的时间点（秒）
            其他参数同 add_subtitles_to_video
        """
        print(f"正在生成字幕预览...")
        
        import shutil
        import uuid
        
        temp_dir = Path(srt_path).parent
        temp_id = uuid.uuid4().hex[:8]
        temp_srt = temp_dir / f"temp_sub_{temp_id}.srt"
        
        try:
            # 复制字幕到临时文件
            shutil.copy(str(srt_path), str(temp_srt))
            
            # 构建字幕样式参数
            style_params = []
            style_params.append(f"FontSize={font_size}")
            style_params.append(f"FontName={font_name}")
            style_params.append(f"MarginV={margin_v}")
            style_params.append(f"MarginH={margin_h}")
            style_params.append(f"PrimaryColour={primary_color}")
            style_params.append(f"OutlineColour={outline_color}")
            style_params.append(f"Bold={'1' if bold else '0'}")
            style_params.append(f"Italic={'1' if italic else '0'}")
            
            force_style = ",".join(style_params)
            
            # 提取指定时间点的帧并添加字幕
            command = [
                "ffmpeg", "-y",
                "-ss", str(timestamp),
                "-i", str(video_path),
                "-vf", f"subtitles={temp_srt.name}:force_style='{force_style}'",
                "-vframes", "1",
                str(output_image)
            ]
            
            result = subprocess.run(command, cwd=str(temp_dir), check=True,
                                   capture_output=True, encoding='utf-8', errors='replace')
            print(f"预览图片生成完成: {output_image}")
            
        finally:
            if temp_srt.exists():
                temp_srt.unlink()
    
    def process_video(self, video_path, language=None, output_dir=None, 
                     embed_subtitles=False, threads=4, gpu_layers=0,
                     subtitle_style=None, use_audio_preprocessing=True, parallel_count=2):
        """
        处理视频：提取音频、识别、生成字幕
        
        Args:
            video_path: 视频文件路径
            language: 语言代码（如 'zh', 'en'）
            output_dir: 输出目录（None则使用视频所在目录）
            embed_subtitles: 是否将字幕嵌入视频
            threads: CPU 线程数
            gpu_layers: GPU 处理的层数（0=仅CPU，-1=全部GPU，推荐32-64）
            subtitle_style: 字幕样式字典（可选）
            use_audio_preprocessing: 是否使用音频预处理（人声分离+切片）
            parallel_count: 并行处理的音频片段数量（1-8）
        """
        import time
        start_time = time.time()
        
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = video_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 临时音频文件
        audio_path = output_dir / "temp_audio.wav"
        srt_path = output_dir / f"{video_path.stem}.srt"
        
        # 默认字幕样式
        default_style = {
            'font_size': 24,
            'font_name': 'Arial',
            'margin_v': 25,
            'margin_h': 0,
            'primary_color': '&HFFFFFF',
            'outline_color': '&H000000',
            'bold': False,
            'italic': False
        }
        
        if subtitle_style:
            default_style.update(subtitle_style)
        
        try:
            # 1. 提取音频
            self.extract_audio(str(video_path), str(audio_path))
            
            if use_audio_preprocessing:
                # 使用音频预处理流程
                print("\n=== 启用音频预处理模式 ===")
                processor = AudioProcessor(output_dir / "temp_segments")
                
                # 2a. 人声分离（可选）
                vocal_path = output_dir / "temp_vocal.wav"
                vocal_separated = processor.separate_vocals(str(audio_path), str(vocal_path))
                
                # 使用人声或原始音频
                process_audio = str(vocal_path) if vocal_separated else str(audio_path)
                
                # 2b. 检测静音并切分音频
                # 如果有人声分离，使用更激进的参数（因为背景音乐已去除）
                # 如果没有，使用保守参数避免错误切分
                if vocal_separated:
                    print("\n使用人声轨道检测静音（更精确的切分点）")
                    segments = processor.detect_silence_segments(
                        process_audio,
                        min_silence_duration=0.3,   # 更短的静音
                        silence_threshold=-40,       # 更严格的阈值
                        min_segment_duration=2.0,
                        max_segment_duration=30.0
                    )
                else:
                    print("\n⚠ 警告: 未进行人声分离，使用原始音频")
                    print("使用保守的切分参数（避免在句子中间切断）")
                    segments = processor.detect_silence_segments(
                        process_audio,
                        min_silence_duration=1.0,    # 更长的静音才切分
                        silence_threshold=-30,       # 更宽松的阈值
                        min_segment_duration=5.0,    # 更长的最小片段
                        max_segment_duration=40.0    # 更长的最大片段
                    )
                
                # 2c. 切分音频
                segment_files = processor.split_audio(process_audio, segments)
                
                # 2d. 并行识别片段
                print(f"\n开始并行识别 {len(segment_files)} 个音频片段（并行数：{parallel_count}）...")
                srt_segments = []
                
                # 使用线程池进行并行处理
                from concurrent.futures import ThreadPoolExecutor, as_completed
                
                def process_segment(segment_info):
                    """处理单个片段的函数"""
                    i, (segment_path, start_offset, end_offset) = segment_info
                    print(f"\n处理片段 {i+1}/{len(segment_files)} ({start_offset:.1f}s - {end_offset:.1f}s)")
                    
                    segment_srt = output_dir / "temp_segments" / f"segment_{i:04d}.srt"
                    
                    try:
                        self.transcribe_audio_srt(
                            segment_path,
                            str(segment_srt),
                            language=language,
                            threads=threads,
                            gpu_layers=gpu_layers
                        )
                        return (str(segment_srt), start_offset)
                    except Exception as e:
                        print(f"警告: 片段 {i+1} 识别失败: {e}")
                        return None
                
                # 使用线程池并行处理
                with ThreadPoolExecutor(max_workers=parallel_count) as executor:
                    # 提交所有任务
                    futures = {
                        executor.submit(process_segment, (i, segment_info)): i 
                        for i, segment_info in enumerate(segment_files)
                    }
                    
                    # 收集结果（按完成顺序）
                    completed = 0
                    for future in as_completed(futures):
                        completed += 1
                        result = future.result()
                        if result:
                            srt_segments.append(result)
                        print(f"进度: {completed}/{len(segment_files)} 完成")
                
                # 按时间排序（因为并行处理可能乱序）
                srt_segments.sort(key=lambda x: x[1])
                
                print(f"\n所有片段识别完成，共 {len(srt_segments)} 个成功")
                
                # 2e. 合并字幕片段
                processor.merge_srt_segments(srt_segments, str(srt_path))
                
                # 清理临时文件
                if vocal_separated and vocal_path.exists():
                    vocal_path.unlink()
                processor.cleanup_temp_files()
                
            else:
                # 2. 直接使用 whisper.cpp 生成 SRT（原有流程）
                self.transcribe_audio_srt(
                    str(audio_path), 
                    str(srt_path),
                    language=language,
                    threads=threads,
                    gpu_layers=gpu_layers
                )
            
            # 3. 可选：将字幕嵌入视频
            output_video = None
            if embed_subtitles:
                output_video = output_dir / f"{video_path.stem}_with_subtitles{video_path.suffix}"
                self.add_subtitles_to_video(
                    str(video_path),
                    str(srt_path),
                    str(output_video),
                    **default_style
                )
            
            elapsed_time = time.time() - start_time
            print("\n" + "="*50)
            print("处理完成！")
            print(f"字幕文件: {srt_path}")
            if embed_subtitles and output_video:
                print(f"带字幕视频: {output_video}")
            print(f"总耗时: {elapsed_time:.2f} 秒")
            backend_info = f"whisper.cpp ({self.gpu_backend.upper()})" if self.gpu_backend else "whisper.cpp (CPU)"
            print(f"使用引擎: {backend_info}")
            if gpu_layers != 0:
                print(f"GPU 层数: {gpu_layers if gpu_layers > 0 else '全部'}")
            if use_audio_preprocessing:
                print("音频预处理: 已启用")
            print("="*50)
            
            return str(srt_path)
            
        except Exception as e:
            # 确保错误时也清理临时文件
            if audio_path.exists():
                try:
                    audio_path.unlink()
                    print("临时音频文件已清理")
                except:
                    pass
            raise e
        
        finally:
            # 清理临时文件（正常完成时）
            if audio_path.exists():
                try:
                    audio_path.unlink()
                    print("临时音频文件已清理")
                except Exception as cleanup_error:
                    print(f"清理临时文件时出错: {cleanup_error}")


def main():
    """主函数 - 命令行使用示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频自动字幕生成器 (whisper.cpp 版本)")
    parser.add_argument("video", help="视频文件路径")
    parser.add_argument("-w", "--whisper", required=True, help="whisper.cpp 主程序路径 (whisper-cli.exe)")
    parser.add_argument("-m", "--model", required=True, help="模型文件路径 (.bin)")
    parser.add_argument("-l", "--language", help="语言代码 (如: zh, en)", default=None)
    parser.add_argument("-o", "--output", help="输出目录", default=None)
    parser.add_argument("-e", "--embed", action="store_true", help="将字幕嵌入视频")
    parser.add_argument("-t", "--threads", type=int, help="CPU 线程数", default=4)
    parser.add_argument("-g", "--gpu", help="GPU 后端 (cuda/vulkan/opencl/metal)", 
                       choices=['cuda', 'vulkan', 'opencl', 'metal'], default=None)
    parser.add_argument("-ngl", "--gpu-layers", type=int, 
                       help="GPU 开关 (0=禁用, 1=启用，新版自动管理)", default=1)
    
    args = parser.parse_args()
    
    # 创建生成器实例
    generator = VideoSubtitleGeneratorCpp(
        whisper_cpp_path=args.whisper,
        model_path=args.model,
        gpu_backend=args.gpu
    )
    
    # 处理视频
    generator.process_video(
        video_path=args.video,
        language=args.language,
        output_dir=args.output,
        embed_subtitles=args.embed,
        threads=args.threads,
        gpu_layers=args.gpu_layers
    )


if __name__ == "__main__":
    main()
