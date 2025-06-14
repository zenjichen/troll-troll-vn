import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import tempfile
import random
from threading import Thread

def get_duration(file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', file],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return float(result.stdout.strip())

def is_image_file(file_path):
    # Check if the file is an image based on extension
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

def create_video_from_image(image_path, output_path, duration=5, video_crf='23', resolution='original'):
    # Create a video from an image with specified duration (5-8 seconds)
    duration = random.uniform(5, 8)  # Random duration between 5-8 seconds
    
    # Set scaling based on resolution
    scale_filter = 'scale=trunc(iw/2)*2:trunc(ih/2)*2'  # Default: ensure dimensions are even
    if resolution == '720p':
        scale_filter = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2'
    elif resolution == '1080p':
        scale_filter = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2'
    
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1', '-i', image_path, 
        '-c:v', 'libx264', '-t', str(duration), '-pix_fmt', 'yuv420p',
        '-vf', scale_filter,
        '-crf', video_crf, output_path
    ])
    return duration

def process(videos, audios, save_path, quality_settings=None, info_callback=None):
    tmp = tempfile.mkdtemp()
    
    # Set default quality settings if not provided
    if quality_settings is None:
        quality_settings = {
            'video_quality': 'medium',  # low, medium, high
            'audio_bitrate': '192k',    # 128k, 192k, 256k
            'resolution': 'original'    # 720p, 1080p, original
        }
    
    # Get quality parameters
    video_crf = {
        'low': '28',      # Lower quality, smaller file
        'medium': '23',   # Default quality
        'high': '18'      # Higher quality, larger file
    }.get(quality_settings['video_quality'], '23')
    
    audio_bitrate = quality_settings['audio_bitrate']
    
    if info_callback:
        info_callback("Đang xử lý audio...")
    
    # Merge ALL audio files in order (concatenate sequentially)
    merged_audio = os.path.join(tmp, "audio_merged.wav")
    
    if info_callback:
        info_callback(f"Đang ghép {len(audios)} file audio theo thứ tự...")
    
    if len(audios) == 1:
        # Single audio file - just normalize
        subprocess.run(['ffmpeg', '-y', '-i', audios[0], '-ar', '44100', '-ac', '2', 
                       '-c:a', 'pcm_s16le', merged_audio])
    else:
        # Multiple audio files - use filter_complex for reliable concatenation
        inputs = []
        for i, audio in enumerate(audios):
            inputs.extend(['-i', audio])
        
        # Build filter_complex string: [0:a][1:a][2:a]...concat=n=X:v=0:a=1[outa]
        filter_parts = ''.join(f'[{i}:a]' for i in range(len(audios)))
        filter_complex = f'{filter_parts}concat=n={len(audios)}:v=0:a=1[outa]'
        
        cmd = ['ffmpeg', '-y'] + inputs + ['-filter_complex', filter_complex, 
               '-map', '[outa]', '-ar', '44100', '-ac', '2', '-c:a', 'pcm_s16le', merged_audio]
        
        subprocess.run(cmd)
    
    # Get duration of the final merged audio
    dur_audio = get_duration(merged_audio)
    
    if info_callback:
        info_callback(f"Đã ghép xong {len(audios)} audio, tổng thời lượng: {dur_audio:.1f}s")
    
    if info_callback:
        info_callback("Đang tạo chuỗi video...")
    
    # Create randomized video sequence
    video_sequence = []
    video_files_to_concat = []  # Store actual file paths for concatenation
    current_duration = 0
    video_counter = 0
    
    # Get resolution setting
    resolution = quality_settings['resolution']
    
    while current_duration < dur_audio:
        # Randomly pick a video
        selected_video = random.choice(videos)
        
        # Check if it's an image or video
        if is_image_file(selected_video):
            # Create a video from the image
            image_video = os.path.join(tmp, f"image_video_{video_counter}.mp4")
            video_duration = create_video_from_image(selected_video, image_video, video_crf=video_crf, resolution=resolution)
            
            if current_duration + video_duration > dur_audio:
                # Trim the last video to match audio duration
                remaining_time = dur_audio - current_duration
                trimmed_video = os.path.join(tmp, f"trimmed_{video_counter}.mp4")
                subprocess.run(['ffmpeg', '-y', '-i', image_video, '-t', str(remaining_time), 
                               '-c:v', 'libx264', '-crf', video_crf, trimmed_video])
                video_files_to_concat.append(trimmed_video)
                current_duration = dur_audio
            else:
                video_files_to_concat.append(image_video)
                current_duration += video_duration
        else:
            # Regular video processing
            video_duration = get_duration(selected_video)
            
            if current_duration + video_duration > dur_audio:
                # Trim the last video to match audio duration
                remaining_time = dur_audio - current_duration
                trimmed_video = os.path.join(tmp, f"trimmed_{video_counter}.mp4")
                subprocess.run(['ffmpeg', '-y', '-i', selected_video, '-t', str(remaining_time), 
                               '-c:v', 'libx264', '-crf', video_crf, trimmed_video])
                video_files_to_concat.append(trimmed_video)
                current_duration = dur_audio
            else:
                # Copy the full video to temp folder to ensure consistent format
                copied_video = os.path.join(tmp, f"video_{video_counter}.mp4")
                subprocess.run(['ffmpeg', '-y', '-i', selected_video, '-c:v', 'libx264', '-crf', video_crf, copied_video])
                video_files_to_concat.append(copied_video)
                current_duration += video_duration
        
        video_counter += 1
        print(f"Added {'image' if is_image_file(selected_video) else 'video'}: {os.path.basename(selected_video)} (Duration: {video_duration:.2f}s, Total: {current_duration:.2f}s)")
        
        if info_callback:
            info_callback(f"Đã thêm: {os.path.basename(selected_video)} ({current_duration:.1f}/{dur_audio:.1f}s)")
    
    if info_callback:
        info_callback("Đang ghép video...")
    
    # Concatenate video sequence
    final_video = os.path.join(tmp, "final_video.mp4")
    if len(video_files_to_concat) > 1:
        video_list_txt = os.path.join(tmp, "video_list.txt")
        with open(video_list_txt, "w", encoding="utf-8") as f:
            for vid in video_files_to_concat:
                f.write(f"file '{vid}'\n")
        # Concatenate all video segments
        subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', video_list_txt, 
                       '-c', 'copy', final_video])
    else:
        final_video = video_files_to_concat[0]
    
    if info_callback:
        info_callback("Đang kết hợp video và audio...")
    
    # Combine final video with merged audio - remove original audio completely
    subprocess.run([
        'ffmpeg', '-y', '-i', final_video, '-i', merged_audio,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', audio_bitrate, '-ar', '44100',
        '-map', '0:v:0', '-map', '1:a:0', 
        '-avoid_negative_ts', 'make_zero', '-fflags', '+genpts',
        '-shortest', save_path
    ])
    
    # Clean up temp files
    try:
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))
        os.rmdir(tmp)
    except:
        pass

def run_merge(videos, audios, save_path, quality_settings, btn, info_callback=None):
    try:
        btn['state'] = 'disabled'
        btn['text'] = 'Đang xử lý...'
        if info_callback:
            info_callback("Bắt đầu xử lý...")
        process(videos, audios, save_path, quality_settings, info_callback)
        messagebox.showinfo("Thành công", f"Đã xuất file:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra:\n{str(e)}")
    finally:
        btn['state'] = 'normal'
        btn['text'] = '👇 XUẤT VIDEO'
        if info_callback:
            info_callback("Hoàn thành!")

class App:
    def __init__(self, master):
        self.master = master
        self.video_paths = []
        self.audio_paths = []

        # Quality settings variables
        self.video_quality_var = tk.StringVar(value="medium")
        self.audio_bitrate_var = tk.StringVar(value="192k")
        self.resolution_var = tk.StringVar(value="original")

        master.title("Tool ghép _video tự bỏ âm với list audio_ max speed zenjichen")
        master.geometry("740x880")
        master.configure(bg='#f0f0f0')
        
        # Create style for ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_frame = tk.Frame(master, bg='#f0f0f0')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(main_frame, bg='#2196F3', relief='raised', bd=2)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🎬 Tool render video audio max speed zenjichen", 
                              font=('Arial', 16, 'bold'), 
                              bg='#2196F3', fg='white', pady=15)
        title_label.pack()
        
        # Video/Image selection section
        self.create_file_section(main_frame, "📹 DANH SÁCH VIDEO & ẢNH (sẽ random xen kẽ):", 
                                "video/ảnh", self.add_videos, self.remove_selected_videos, 
                                self.clear_all_videos)
        
        # Audio selection section  
        self.create_file_section(main_frame, "🎵 DANH SÁCH AUDIO (ghép nối tiếp theo thứ tự):", 
                                "audio", self.add_audios, self.remove_selected_audios, 
                                self.clear_all_audios)

        # Quality settings section
        self.create_quality_section(main_frame)

        # Save path section
        save_section = tk.LabelFrame(main_frame, text="💾 ĐƯỜNG DẪN LUU FILE", 
                                   font=('Arial', 11, 'bold'), 
                                   fg='#1976D2', bg='#f0f0f0', pady=10)
        save_section.pack(fill="x", pady=(0, 20))
        
        save_frame = tk.Frame(save_section, bg='#f0f0f0')
        save_frame.pack(fill="x", padx=10, pady=5)
        
        self.save_entry = tk.Entry(save_frame, font=('Arial', 10), relief='solid', bd=1)
        self.save_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.save_entry.insert(0, os.path.abspath("output.mp4"))
        
        browse_btn = tk.Button(save_frame, text="📁 Chọn", font=('Arial', 10), 
                              bg='#FF9800', fg='white', relief='flat',
                              command=self.browse_save_path)
        browse_btn.pack(side="right", padx=5, pady=2)

        # Status and run section
        status_frame = tk.Frame(main_frame, bg='#f0f0f0')
        status_frame.pack(fill="x")
        
        # Run button
        self.run_btn = tk.Button(status_frame, text="🚀 XUẤT VIDEO", 
                                font=('Arial', 14, 'bold'), 
                                bg="#4CAF50", fg="white", relief='flat',
                                pady=15, command=self.start)
        self.run_btn.pack(pady=(0, 15))
        
        # Status info
        self.status_lbl = tk.Label(status_frame, text="✅ Sẵn sàng xử lý", 
                                  fg="#4CAF50", font=('Arial', 10, 'bold'),
                                  bg='#f0f0f0')
        self.status_lbl.pack(pady=(0, 5))
        
        self.info_lbl = tk.Label(status_frame, 
                                text="💡 Lưu ý: Video và ảnh sẽ được random xen kẽ để khớp với độ dài audio (ảnh sẽ hiển thị 5-8 giây)", 
                                fg="#666", font=('Arial', 9), bg='#f0f0f0')
        self.info_lbl.pack(pady=(0, 10))
        
    def create_quality_section(self, parent):
        quality_section = tk.LabelFrame(parent, text="⚙️ CHẤT LƯỢNG OUTPUT", 
                                      font=('Arial', 11, 'bold'), 
                                      fg='#1976D2', bg='#f0f0f0', pady=10)
        quality_section.pack(fill="x", pady=(0, 20))
        
        # Create frame for quality options
        quality_frame = tk.Frame(quality_section, bg='#f0f0f0')
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        # Video quality
        video_frame = tk.Frame(quality_frame, bg='#f0f0f0')
        video_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Label(video_frame, text="Chất lượng video:", bg='#f0f0f0', font=('Arial', 10)).pack(anchor="w")
        
        tk.Radiobutton(video_frame, text="Thấp (file nhỏ)", variable=self.video_quality_var, 
                      value="low", bg='#f0f0f0').pack(anchor="w")
        tk.Radiobutton(video_frame, text="Trung bình", variable=self.video_quality_var, 
                      value="medium", bg='#f0f0f0').pack(anchor="w")
        tk.Radiobutton(video_frame, text="Cao (file lớn)", variable=self.video_quality_var, 
                      value="high", bg='#f0f0f0').pack(anchor="w")
        
        # Audio bitrate
        audio_frame = tk.Frame(quality_frame, bg='#f0f0f0')
        audio_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Label(audio_frame, text="Chất lượng audio:", bg='#f0f0f0', font=('Arial', 10)).pack(anchor="w")
        
        tk.Radiobutton(audio_frame, text="128k", variable=self.audio_bitrate_var, 
                      value="128k", bg='#f0f0f0').pack(anchor="w")
        tk.Radiobutton(audio_frame, text="192k", variable=self.audio_bitrate_var, 
                      value="192k", bg='#f0f0f0').pack(anchor="w")
        tk.Radiobutton(audio_frame, text="256k", variable=self.audio_bitrate_var, 
                      value="256k", bg='#f0f0f0').pack(anchor="w")
        
        # Resolution
        res_frame = tk.Frame(quality_frame, bg='#f0f0f0')
        res_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        tk.Label(res_frame, text="Độ phân giải:", bg='#f0f0f0', font=('Arial', 10)).pack(anchor="w")
        
        tk.Radiobutton(res_frame, text="Giữ nguyên", variable=self.resolution_var, 
                      value="original", bg='#f0f0f0').pack(anchor="w")
        tk.Radiobutton(res_frame, text="720p", variable=self.resolution_var, 
                      value="720p", bg='#f0f0f0').pack(anchor="w")
        tk.Radiobutton(res_frame, text="1080p", variable=self.resolution_var, 
                      value="1080p", bg='#f0f0f0').pack(anchor="w")

    def create_file_section(self, parent, title, file_type, add_func, remove_func, clear_func):
        # Create section frame
        section = tk.LabelFrame(parent, text=title, font=('Arial', 11, 'bold'), 
                               fg='#1976D2', bg='#f0f0f0', pady=10)
        section.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create scrollable text area with improved styling
        text_frame = tk.Frame(section, bg='#f0f0f0')
        text_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Text widget with scrollbar
        text_widget = tk.Text(text_frame, height=6, wrap=tk.WORD, 
                             font=('Consolas', 9), relief='solid', bd=1,
                             bg='#ffffff', selectbackground='#3f51b5',
                             selectforeground='white')
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview,
                                bg='#e0e0e0', troughcolor='#f5f5f5', 
                                activebackground='#bdbdbd')
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack text and scrollbar
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store text widget reference
        if file_type == "video":
            self.video_text = text_widget
        else:
            self.audio_text = text_widget
        
        # Button frame with improved styling
        btn_frame = tk.Frame(section, bg='#f0f0f0')
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        # Styled buttons
        add_btn = tk.Button(btn_frame, text=f"➕ Thêm {file_type}", 
                           font=('Arial', 9), bg='#2196F3', fg='white', 
                           relief='flat', command=add_func)
        add_btn.pack(side="left", padx=(0, 8), pady=2)
        
        remove_btn = tk.Button(btn_frame, text="❌ Xóa đã chọn", 
                              font=('Arial', 9), bg='#FF5722', fg='white', 
                              relief='flat', command=remove_func)
        remove_btn.pack(side="left", padx=(0, 8), pady=2)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Xóa tất cả", 
                             font=('Arial', 9), bg='#9E9E9E', fg='white', 
                             relief='flat', command=clear_func)
        clear_btn.pack(side="left", pady=2)
        
        # Initialize display
        if file_type == "video":
            self.update_video_display()
        else:
            self.update_audio_display()

    def add_videos(self):
        paths = filedialog.askopenfilenames(
            title="Thêm video/ảnh", 
            filetypes=[
                ("All supported files", "*.mp4 *.mov *.mkv *.avi *.flv *.wmv *.jpg *.jpeg *.png *.bmp *.gif"),
                ("Video files", "*.mp4 *.mov *.mkv *.avi *.flv *.wmv"),
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")
            ]
        )
        if paths:
            for path in paths:
                if path not in self.video_paths:
                    self.video_paths.append(path)
            self.update_video_display()

    def clear_all_videos(self):
        self.video_paths = []
        self.update_video_display()

    def remove_selected_videos(self):
        try:
            selected_text = self.video_text.selection_get()
            lines_to_remove = []
            for line in selected_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('📹') and not line.startswith('Chưa'):
                    for i, path in enumerate(self.video_paths):
                        if os.path.basename(path) in line:
                            lines_to_remove.append(i)
            
            for i in sorted(set(lines_to_remove), reverse=True):
                self.video_paths.pop(i)
            
            self.update_video_display()
        except tk.TclError:
            messagebox.showinfo("Thông báo", "Hãy chọn (highlight) các dòng video muốn xóa trong text box")

    def update_video_display(self):
        self.video_text.config(state=tk.NORMAL)
        self.video_text.delete(1.0, tk.END)
        
        if self.video_paths:
            video_count = sum(1 for path in self.video_paths if not is_image_file(path))
            image_count = len(self.video_paths) - video_count
            
            if image_count > 0 and video_count > 0:
                self.video_text.insert(tk.END, f"📹 Đã chọn {video_count} video và {image_count} ảnh:\n\n")
            elif image_count > 0:
                self.video_text.insert(tk.END, f"🖼️ Đã chọn {image_count} ảnh:\n\n")
            else:
                self.video_text.insert(tk.END, f"📹 Đã chọn {video_count} video:\n\n")
                
            for i, path in enumerate(self.video_paths, 1):
                filename = os.path.basename(path)
                file_type = "🖼️ Ảnh" if is_image_file(path) else "📹 Video"
                self.video_text.insert(tk.END, f"  {i:2d}. {file_type}: {filename}\n")
                # Add file path in smaller text
                self.video_text.insert(tk.END, f"      📂 {path}\n\n")
        else:
            self.video_text.insert(tk.END, "Chưa chọn video hoặc ảnh nào\n\n")
            self.video_text.insert(tk.END, "👆 Nhấn nút 'Thêm video/ảnh' để bắt đầu")
        
        self.video_text.config(state=tk.DISABLED)

    def add_audios(self):
        paths = filedialog.askopenfilenames(
            title="Thêm audio", 
            filetypes=[("Audio files", "*.mp3 *.wav *.aac *.m4a *.ogg *.flac")]
        )
        if paths:
            for path in paths:
                if path not in self.audio_paths:
                    self.audio_paths.append(path)
            self.update_audio_display()

    def clear_all_audios(self):
        self.audio_paths = []
        self.update_audio_display()

    def remove_selected_audios(self):
        try:
            selected_text = self.audio_text.selection_get()
            lines_to_remove = []
            for line in selected_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('🎵') and not line.startswith('Chưa'):
                    for i, path in enumerate(self.audio_paths):
                        if os.path.basename(path) in line:
                            lines_to_remove.append(i)
            
            for i in sorted(set(lines_to_remove), reverse=True):
                self.audio_paths.pop(i)
            
            self.update_audio_display()
        except tk.TclError:
            messagebox.showinfo("Thông báo", "Hãy chọn (highlight) các dòng audio muốn xóa trong text box")

    def update_audio_display(self):
        self.audio_text.config(state=tk.NORMAL)
        self.audio_text.delete(1.0, tk.END)
        
        if self.audio_paths:
            self.audio_text.insert(tk.END, f"🎵 Đã chọn {len(self.audio_paths)} audio:\n\n")
            for i, path in enumerate(self.audio_paths, 1):
                filename = os.path.basename(path)
                self.audio_text.insert(tk.END, f"  {i:2d}. {filename}\n")
                # Add file path in smaller text
                self.audio_text.insert(tk.END, f"      📂 {path}\n\n")
        else:
            self.audio_text.insert(tk.END, "Chưa chọn audio nào\n\n")
            self.audio_text.insert(tk.END, "👆 Nhấn nút 'Thêm audio' để bắt đầu")
        
        self.audio_text.config(state=tk.DISABLED)

    def browse_save_path(self):
        path = filedialog.asksaveasfilename(
            title="Chọn nơi lưu file",
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if path:
            # Kiểm tra xem file đã tồn tại chưa
            if os.path.exists(path):
                # Tách đường dẫn thành phần thư mục, tên file và phần mở rộng
                directory, filename = os.path.split(path)
                name, ext = os.path.splitext(filename)
                
                # Tìm tên file mới với hiệu số
                counter = 1
                new_path = path
                while os.path.exists(new_path):
                    new_path = os.path.join(directory, f"{name}_{counter}{ext}")
                    counter += 1
                
                # Thông báo cho người dùng
                if messagebox.askyesno("File đã tồn tại", 
                                      f"File {filename} đã tồn tại.\n\nBạn có muốn lưu thành {os.path.basename(new_path)} không?\n\nChọn 'No' để ghi đè file cũ."):
                    path = new_path
            
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(0, path)

    def update_status(self, message):
        self.status_lbl['text'] = f"⚙️ {message}"
        self.status_lbl['fg'] = "#FF9800"
        self.master.update()

    def start(self):
        if not self.video_paths:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn ít nhất một file video hoặc ảnh.")
            return
        if not self.audio_paths:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn ít nhất một file audio.")
            return
        if not self.save_entry.get().strip():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn đường dẫn lưu file.")
            return
        
        # Lấy đường dẫn lưu file
        save_path = self.save_entry.get().strip()
        
        # Kiểm tra xem thư mục lưu có tồn tại không
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            messagebox.showerror("Lỗi", f"Thư mục không tồn tại: {save_dir}")
            return
        
        # Kiểm tra xem file đã tồn tại chưa và xử lý trùng tên
        if os.path.exists(save_path):
            # Tách đường dẫn thành phần thư mục, tên file và phần mở rộng
            directory, filename = os.path.split(save_path)
            name, ext = os.path.splitext(filename)
            
            # Tìm tên file mới với hiệu số
            counter = 1
            new_path = save_path
            while os.path.exists(new_path):
                new_path = os.path.join(directory, f"{name}_{counter}{ext}")
                counter += 1
            
            # Thông báo cho người dùng
            if messagebox.askyesno("File đã tồn tại", 
                                  f"File {filename} đã tồn tại.\n\nBạn có muốn lưu thành {os.path.basename(new_path)} không?\n\nChọn 'No' để ghi đè file cũ."):
                save_path = new_path
                # Cập nhật ô nhập liệu
                self.save_entry.delete(0, tk.END)
                self.save_entry.insert(0, save_path)
        
        # Get quality settings
        quality_settings = {
            'video_quality': self.video_quality_var.get(),
            'audio_bitrate': self.audio_bitrate_var.get(),
            'resolution': self.resolution_var.get()
        }
            
        Thread(target=run_merge, args=(self.video_paths, self.audio_paths, save_path, 
                                      quality_settings, self.run_btn, self.update_status)).start()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()