# Hướng dẫn cài đặt FFmpeg và thêm vào PATH

## 1. Tải FFmpeg

1. Truy cập trang web chính thức của FFmpeg tại [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Tìm và nhấp vào liên kết tải xuống cho Windows
3. Tải phiên bản "Windows builds from gyan.dev" hoặc "Windows builds by BtbN"
4. Chọn phiên bản phù hợp với hệ thống của bạn (thường là phiên bản "full" hoặc "essentials" và phiên bản 64-bit)

## 2. Giải nén file tải về

1. Sau khi tải xuống, bạn sẽ có một file nén (thường là .zip hoặc .7z)
2. Giải nén file này vào một thư mục trên máy tính của bạn
   - Ví dụ: `C:\Program Files\ffmpeg`
   - Hoặc: `C:\ffmpeg`
3. Sau khi giải nén, bạn sẽ thấy một thư mục có tên là `bin` chứa các file thực thi của FFmpeg (ffmpeg.exe, ffprobe.exe, ffplay.exe)

## 3. Thêm FFmpeg vào biến môi trường PATH

### Cách 1: Sử dụng giao diện Windows

1. Nhấn chuột phải vào biểu tượng **This PC** hoặc **My Computer** trên Desktop hoặc trong File Explorer
2. Chọn **Properties**
3. Chọn **Advanced system settings** ở bên trái
4. Trong cửa sổ System Properties, chọn tab **Advanced**
5. Nhấn vào nút **Environment Variables**
6. Trong phần **System variables**, tìm biến **Path** và chọn **Edit**
7. Trong Windows 10/11:
   - Nhấn nút **New**
   - Thêm đường dẫn đến thư mục `bin` của FFmpeg (ví dụ: `C:\Program Files\ffmpeg\bin` hoặc `C:\ffmpeg\bin`)
   - Nhấn **OK**
8. Trong Windows 7/8:
   - Thêm dấu chấm phẩy (;) vào cuối giá trị hiện tại, sau đó thêm đường dẫn đến thư mục `bin` của FFmpeg
   - Ví dụ: `...;C:\Program Files\ffmpeg\bin`
   - Nhấn **OK**

### Cách 2: Sử dụng Command Prompt (với quyền Administrator)

1. Nhấn chuột phải vào nút Start và chọn **Windows PowerShell (Admin)** hoặc **Command Prompt (Admin)**
2. Nhập lệnh sau (thay thế đường dẫn bằng đường dẫn thực tế đến thư mục `bin` của FFmpeg):

   ```
   setx /M PATH "%PATH%;C:\Program Files\ffmpeg\bin"
   ```

   hoặc

   ```
   setx /M PATH "%PATH%;C:\ffmpeg\bin"
   ```

3. Nhấn Enter để thực hiện lệnh

## 4. Kiểm tra cài đặt

1. Đóng tất cả các cửa sổ Command Prompt hoặc PowerShell đang mở
2. Mở một cửa sổ Command Prompt hoặc PowerShell mới
3. Nhập lệnh:

   ```
   ffmpeg -version
   ```

4. Nếu FFmpeg đã được cài đặt và thêm vào PATH đúng cách, bạn sẽ thấy thông tin về phiên bản FFmpeg

## Lưu ý

- Sau khi thêm FFmpeg vào PATH, bạn có thể cần khởi động lại máy tính để các thay đổi có hiệu lực
- Nếu bạn gặp lỗi "'ffmpeg' is not recognized as an internal or external command", hãy kiểm tra lại đường dẫn đã thêm vào PATH
- Đảm bảo rằng đường dẫn bạn thêm vào PATH trỏ đến thư mục chứa các file thực thi (.exe) của FFmpeg

## Sử dụng với ứng dụng Ghép Video và Audio

Sau khi cài đặt FFmpeg và thêm vào PATH thành công, bạn có thể chạy ứng dụng Ghép Video và Audio mà không gặp lỗi liên quan đến FFmpeg. Ứng dụng sẽ tự động sử dụng FFmpeg để xử lý các file video và audio.