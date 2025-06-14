
## Tính năng chính

- ****: Kết hợp nhiều file video/ảnh với nhiều file audio thành một video hoàn chỉnh
- **Hỗ trợ nhiều định dạng**:
  - Video: MP4, MOV, MKV, AVI, FLV, WMV
  - Ảnh: JPG, JPEG, PNG, BMP, GIF
  - Audio: MP3, WAV, AAC, M4A, OGG, FLAC
- **Tùy chỉnh chất lượng đầu ra**:
  - Chất lượng video: Thấp, Trung bình, Cao
  - Bitrate audio: 128k, 192k, 256k
  - Độ phân giải: Giữ nguyên, 720p, 1080p
- **Tự động xử lý trùng tên file**: Tự động thêm hiệu số vào tên file khi phát hiện trùng lặp
- **Giao diện thân thiện**: Giao diện đồ họa trực quan, dễ sử dụng

## Cách sử dụng

1. **Thêm video/ảnh**:
   - Nhấn nút "Thêm video/ảnh" để chọn các file video hoặc ảnh từ máy tính
   - Có thể chọn nhiều file cùng lúc
   - Danh sách các file đã chọn sẽ hiển thị trong khung bên dưới

2. **Thêm audio**:
   - Nhấn nút "Thêm audio" để chọn các file âm thanh từ máy tính
   - Có thể chọn nhiều file cùng lúc
   - Danh sách các file đã chọn sẽ hiển thị trong khung bên dưới

3. **Tùy chỉnh chất lượng**:
   - Chọn chất lượng video mong muốn (Thấp, Trung bình, Cao)
   - Chọn bitrate audio (128k, 192k, 256k)
   - Chọn độ phân giải (Giữ nguyên, 720p, 1080p)

4. **Chọn đường dẫn lưu file**:
   - Nhấn nút "Chọn nơi lưu" để xác định vị trí và tên file đầu ra
   - Nếu file đã tồn tại, ứng dụng sẽ hỏi bạn có muốn tạo tên file mới với hiệu số hay không

5. **Bắt đầu xử lý**:
   - Nhấn nút "Bắt đầu" để tiến hành quá trình ghép video và audio
   - Trạng thái xử lý sẽ được hiển thị ở phía dưới
   - Khi hoàn thành, một thông báo sẽ hiện lên

## Quy trình xử lý

Khi bạn nhấn nút "Bắt đầu", ứng dụng sẽ thực hiện các bước sau:

1. Kiểm tra tính hợp lệ của đầu vào (có video/ảnh, có audio, có đường dẫn lưu)
2. Kiểm tra và xử lý trùng lặp tên file đầu ra
3. Tạo video từ các file ảnh (nếu có) với thời lượng phù hợp
4. Ghép các file audio thành một file audio duy nhất
5. Cắt và ghép các video/ảnh thành một chuỗi video liên tục
6. Kết hợp video và audio với các thiết lập chất lượng đã chọn
7. Lưu file đầu ra và thông báo hoàn thành

## Yêu cầu hệ thống

- Python 3.6 trở lên
- FFmpeg (cần được cài đặt và thêm vào biến môi trường PATH)
- Các thư viện Python: tkinter, PIL (Pillow), numpy, moviepy

## Cài đặt

1. Cài đặt Python từ [python.org](https://www.python.org/downloads/)
2. Cài đặt FFmpeg từ [ffmpeg.org](https://ffmpeg.org/download.html)
3. Cài đặt các thư viện Python cần thiết:
   ```
   pip install pillow numpy moviepy
   ```
4. Tải và chạy file `tool_render_video_audio.py`

## Lưu ý

- Quá trình xử lý có thể mất nhiều thời gian tùy thuộc vào số lượng và kích thước của các file đầu vào
- Đảm bảo có đủ dung lượng ổ đĩa cho các file tạm thời và file đầu ra
- Ứng dụng sử dụng FFmpeg để xử lý video và audio, vì vậy cần đảm bảo FFmpeg đã được cài đặt đúng cách
