import whisper
import subprocess
import os
from pathlib import Path
import torch

class VideoSubtitleGenerator:
    """视频自动字幕生成器"""
    
    def __init__(self, model_size="base", use_directml=False):
        """
        初始化字幕生成器
        
        Args:
            model_size: Whisper模型大小 (tiny, base, small, medium, large)
            use_directml: 是否使用 DirectML 加速 (仅 Windows)
        """
        self.device = self._setup_device(use_directml)
        print(f"正在加载 Whisper {model_size} 模型...")
        print(f"使用设备: {self.device}")
        
        self.model = whisper.load_model(model_size, device=self.device)
        print("模型加载完成！")
    
    def _setup_device(self, use_directml):
        """
        设置计算设备
        
        Args:
            use_directml: 是否使用 DirectML
        
        Returns:
            设备字符串
        """
        if use_directml:
            try:
                import torch_directml
                dml_device = torch_directml.device()
                print("DirectML 可用！将使用 GPU 加速")
                return dml_device
            except ImportError:
                print("警告: torch-directml 未安装，将使用 CPU")
                print("安装命令: pip install torch-directml")
                return "cpu"
        elif torch.cuda.is_available():
            print("CUDA 可用！将使用 NVIDIA GPU 加速")
            return "cuda"
        else:
            print("将使用 CPU 进行计算")
            return "cpu"
    
    def extract_audio(self, video_path, audio_path="temp_audio.wav"):
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            audio_path: 输出音频文件路径
        """
        print(f"正在从视频中提取音频: {video_path}")
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            audio_path
        ]
        subprocess.run(command, check=True, capture_output=True,
                      encoding='utf-8', errors='replace')
        print(f"音频提取完成: {audio_path}")
        return audio_path
    
    def transcribe_audio(self, audio_path, language=None):
        """
        识别音频内容
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码（如 'zh' 中文, 'en' 英文），None为自动检测
        """
        print("正在识别音频内容...")
        result = self.model.transcribe(
            audio_path,
            language=language,
            verbose=False
        )
        print("音频识别完成！")
        return result
    
    def generate_srt(self, transcription, output_path):
        """
        生成SRT字幕文件
        
        Args:
            transcription: Whisper转录结果
            output_path: 输出SRT文件路径
        """
        print(f"正在生成字幕文件: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(transcription['segments'], 1):
                start_time = self._format_timestamp(segment['start'])
                end_time = self._format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        print("字幕文件生成完成！")
    
    def _format_timestamp(self, seconds):
        """格式化时间戳为SRT格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def add_subtitles_to_video(self, video_path, srt_path, output_path,
                              font_size=24, font_name="Arial",
                              margin_v=25, margin_h=0,
                              primary_color="&HFFFFFF", outline_color="&H000000",
                              bold=False, italic=False):
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
            primary_color: 主颜色
            outline_color: 描边颜色
            bold: 是否粗体
            italic: 是否斜体
        """
        print(f"正在将字幕嵌入视频...")
        
        # 使用临时文件名避免特殊字符问题
        import shutil
        import uuid
        
        temp_dir = Path(srt_path).parent
        temp_id = uuid.uuid4().hex[:8]
        
        temp_srt = temp_dir / f"temp_sub_{temp_id}.srt"
        temp_output = temp_dir / f"temp_output_{temp_id}.mp4"
        
        try:
            shutil.copy(str(srt_path), str(temp_srt))
            
            # 构建样式参数
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
            
            command = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-vf", f"subtitles={temp_srt.name}:force_style='{force_style}'",
                "-c:a", "copy",
                str(temp_output)
            ]
            
            print(f"字幕样式: 字体={font_name} 大小={font_size} 底边距={margin_v}")
            subprocess.run(command, cwd=str(temp_dir), check=True,
                          capture_output=True, encoding='utf-8', errors='replace')
            
            shutil.move(str(temp_output), str(output_path))
            print(f"字幕视频生成完成: {output_path}")
            
        finally:
            if temp_srt.exists():
                temp_srt.unlink()
            if temp_output.exists():
                temp_output.unlink()
    
    def process_video(self, video_path, language=None, output_dir=None, embed_subtitles=False):
        """
        处理视频：提取音频、识别、生成字幕
        
        Args:
            video_path: 视频文件路径
            language: 语言代码（None为自动检测）
            output_dir: 输出目录（None则使用视频所在目录）
            embed_subtitles: 是否将字幕嵌入视频
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
        
        try:
            # 1. 提取音频
            self.extract_audio(str(video_path), str(audio_path))
            
            # 2. 识别音频
            transcription = self.transcribe_audio(str(audio_path), language)
            
            # 3. 生成字幕文件
            srt_path = output_dir / f"{video_path.stem}.srt"
            self.generate_srt(transcription, str(srt_path))
            
            # 4. 可选：将字幕嵌入视频
            if embed_subtitles:
                output_video = output_dir / f"{video_path.stem}_with_subtitles{video_path.suffix}"
                self.add_subtitles_to_video(
                    str(video_path),
                    str(srt_path),
                    str(output_video)
                )
            
            elapsed_time = time.time() - start_time
            print("\n" + "="*50)
            print("处理完成！")
            print(f"字幕文件: {srt_path}")
            if embed_subtitles:
                print(f"带字幕视频: {output_video}")
            print(f"总耗时: {elapsed_time:.2f} 秒")
            print(f"使用设备: {self.device}")
            print("="*50)
            
            return str(srt_path)
            
        finally:
            # 清理临时文件
            if audio_path.exists():
                audio_path.unlink()
                print("临时音频文件已清理")


def main():
    """主函数 - 命令行使用示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频自动字幕生成器")
    parser.add_argument("video", help="视频文件路径")
    parser.add_argument("-l", "--language", help="语言代码 (如: zh, en)", default=None)
    parser.add_argument("-m", "--model", help="模型大小 (tiny/base/small/medium/large)", default="base")
    parser.add_argument("-o", "--output", help="输出目录", default=None)
    parser.add_argument("-e", "--embed", action="store_true", help="将字幕嵌入视频")
    parser.add_argument("-d", "--directml", action="store_true", help="使用 DirectML GPU 加速 (Windows)")
    
    args = parser.parse_args()
    
    # 创建生成器实例
    generator = VideoSubtitleGenerator(
        model_size=args.model,
        use_directml=args.directml
    )
    
    # 处理视频
    generator.process_video(
        video_path=args.video,
        language=args.language,
        output_dir=args.output,
        embed_subtitles=args.embed
    )


if __name__ == "__main__":
    main()
