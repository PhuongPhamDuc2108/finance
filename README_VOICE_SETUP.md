# Hướng Dẫn Thiết Lập Nhận Dạng Giọng Nói

## Yêu Cầu Tiên Quyết

1. **Các Thư Viện Python**:
   - Đảm bảo tất cả các thư viện phụ thuộc được cài đặt bằng cách chạy:
   ```
   pip install -r requirements.txt
   ```

2. **FFmpeg (Tùy Chọn nhưng Khuyến Nghị)**:
   - Để có chất lượng chuyển đổi âm thanh tốt hơn, hãy cài đặt FFmpeg:
   - Windows: Tải xuống từ [FFmpeg.org](https://ffmpeg.org/download.html) và thêm vào PATH
   - Linux: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`

## Thiết Lập Google Cloud Speech-to-Text API

Ứng dụng này sử dụng Google Cloud Speech-to-Text API để nhận dạng giọng nói chính xác, đặc biệt là cho tiếng Việt. Làm theo các bước sau để thiết lập thông tin đăng nhập Google Cloud của bạn:

1. **Tạo Dự Án Google Cloud**:
   - Truy cập [Google Cloud Console](https://console.cloud.google.com/)
   - Tạo một dự án mới hoặc chọn một dự án hiện có

2. **Kích Hoạt Speech-to-Text API**:
   - Trong dự án của bạn, điều hướng đến "APIs & Services" > "Library"
   - Tìm kiếm "Speech-to-Text API" và kích hoạt nó

3. **Tạo Thông Tin Đăng Nhập Tài Khoản Dịch Vụ**:
   - Đi đến "APIs & Services" > "Credentials"
   - Nhấp vào "Create Credentials" > "Service Account"
   - Điền thông tin chi tiết tài khoản dịch vụ và cấp cho nó vai trò "Speech-to-Text Admin"
   - Tạo khóa JSON cho tài khoản dịch vụ này

4. **Cập Nhật Tệp Thông Tin Đăng Nhập**:
   - Thay thế nội dung của `google_credentials.json` bằng khóa JSON bạn đã tải xuống
   - Đảm bảo tệp nằm trong thư mục gốc của dự án

## Lệnh Giọng Nói

Ứng dụng hỗ trợ các lệnh giọng nói sau đây bằng cả tiếng Việt và tiếng Anh:

### Lệnh Điều Hướng
- "thêm thu nhập" / "add income" - Điều hướng đến trang thêm thu nhập
  - Cũng có thể: "đi đến thêm thu nhập", "mở thêm thu nhập", "chuyển đến thêm thu nhập"
  - Cũng có thể: "go to add income", "open add income", "navigate to add income"
- "thêm chi tiêu" / "add expense" - Điều hướng đến trang thêm chi tiêu
  - Cũng có thể: "đi đến thêm chi tiêu", "mở thêm chi tiêu", "chuyển đến thêm chi tiêu"
  - Cũng có thể: "go to add expense", "open add expense", "navigate to add expense"
- "báo cáo" / "financial report" - Điều hướng đến trang báo cáo tài chính
  - Cũng có thể: "xem báo cáo", "đi đến báo cáo", "mở báo cáo", "chuyển đến báo cáo", "xem tài chính"
  - Cũng có thể: "view report", "show report", "go to report", "open report", "navigate to report", "view finance"
- "trang chủ" / "home" - Điều hướng đến trang chủ
  - Cũng có thể: "về trang chủ", "đi đến trang chủ", "mở trang chủ", "chuyển đến trang chủ", "quay về trang chủ"
  - Cũng có thể: "go home", "main page", "go to home", "open home", "navigate to home", "return home"
- "dự báo" / "forecast" - Điều hướng đến trang dự báo
  - Cũng có thể: "đi đến dự báo", "mở dự báo", "chuyển đến dự báo", "xem dự báo", "dự đoán"
  - Cũng có thể: "prediction", "financial forecast", "go to forecast", "open forecast", "navigate to forecast", "view forecast"
- "tài khoản" / "account" - Điều hướng đến trang tài khoản
  - Cũng có thể: "đi đến tài khoản", "mở tài khoản", "chuyển đến tài khoản", "thông tin cá nhân", "hồ sơ"
  - Cũng có thể: "profile", "my account", "settings", "go to account", "open account", "navigate to account", "user profile"

### Lệnh Thu Nhập
- "thêm thu nhập [nguồn] [số tiền]" / "add income [source] [amount]" - Thêm thu nhập với nguồn và số tiền được chỉ định
- "thêm [số tiền] [nguồn]" / "add [amount] income" - Định dạng thay thế để thêm thu nhập
- "thêm [nguồn] [số tiền]" / "add [source] [amount]" - Định dạng trực tiếp để thêm thu nhập
- "[nguồn] [số tiền]" - Định dạng đơn giản (ví dụ: "lương 100" / "salary 100") - Chỉ cần nói nguồn và số tiền
- "[nguồn][số tiền]" - Định dạng không khoảng cách (ví dụ: "lương100" / "salary100") - Không có khoảng cách giữa nguồn và số tiền
- "[nguồn] là [số tiền]" / "[source] is [amount]" - Sử dụng "là" hoặc "is" (ví dụ: "lương là 100" / "salary is 100")
- "có [nguồn] [số tiền]" / "have [source] [amount]" - Sử dụng "có" hoặc "have" (ví dụ: "có lương 100" / "have salary 100")

### Lệnh Chi Tiêu
- "thêm chi tiêu [danh mục] [số tiền]" / "add expense [category] [amount]" - Thêm chi tiêu với danh mục và số tiền được chỉ định
- "thêm [số tiền] chi tiêu" / "add [amount] expense" - Định dạng thay thế để thêm chi tiêu
- "thêm [danh mục] [số tiền]" / "add [category] [amount]" - Định dạng trực tiếp để thêm chi tiêu
- "[danh mục] [số tiền]" - Định dạng đơn giản (ví dụ: "thực phẩm 100" / "food 100") - Chỉ cần nói danh mục và số tiền
- "[danh mục][số tiền]" - Định dạng không khoảng cách (ví dụ: "thựcphẩm100" / "food100") - Không có khoảng cách giữa danh mục và số tiền
- "[danh mục] là [số tiền]" / "[category] is [amount]" - Sử dụng "là" hoặc "is" (ví dụ: "thực phẩm là 100" / "food is 100")
- "chi [danh mục] [số tiền]" / "spend [category] [amount]" - Sử dụng "chi" hoặc "spend" (ví dụ: "chi thực phẩm 100" / "spend food 100")

### Lệnh Xóa
- "xóa thu nhập [id]" / "delete income [id]" - Xóa thu nhập với ID được chỉ định
- "xóa chi tiêu [id]" / "delete expense [id]" - Xóa chi tiêu với ID được chỉ định
- "xóa khoản thu nhập cuối cùng" / "delete last income" - Xóa khoản thu nhập gần đây nhất
- "xóa khoản chi tiêu cuối cùng" / "delete last expense" - Xóa khoản chi tiêu gần đây nhất

### Lệnh Báo Cáo
- "đọc báo cáo" / "read report" - Đọc báo cáo tài chính
  - Cũng có thể: "đọc kết quả", "đọc chi tiêu", "đọc thu nhập", "đọc tài chính", "đọc tình hình", "đọc tóm tắt"
  - Cũng có thể: "đọc to báo cáo", "đọc cho tôi báo cáo", "đọc thông tin tài chính", "đọc tổng quan", "đọc tổng kết"
  - Cũng có thể: "read financial report", "read summary", "read finances", "read income", "read expense"
  - Cũng có thể: "read financial summary", "read overview", "read financial status", "read financial situation", "read aloud report"

## Ngôn Ngữ Được Hỗ Trợ

Hệ thống nhận dạng giọng nói chủ yếu hỗ trợ:

1. **Tiếng Việt (vi-VN)**: Ngôn ngữ chính với khả năng nhận dạng tối ưu cho các thuật ngữ tài chính
2. **Tiếng Anh (en-US)**: Ngôn ngữ dự phòng

Hệ thống được tối ưu hóa cho thuật ngữ tài chính tiếng Việt nhưng cũng có thể hiểu các lệnh tiếng Anh. Để có kết quả tốt nhất, hãy nói rõ ràng và sử dụng các mẫu lệnh được mô tả ở trên.

## Xử Lý Lỗi

Khi một lệnh không được nhận dạng, hệ thống sẽ hiển thị thông báo lỗi hữu ích với các ví dụ về lệnh hợp lệ. Hãy thử diễn đạt lại lệnh của bạn bằng cách sử dụng một trong các định dạng được đề xuất.

## Xử Lý Sự Cố

Nếu bạn gặp vấn đề với nhận dạng giọng nói:

1. **Kiểm Tra Thông Tin Đăng Nhập**: Đảm bảo thông tin đăng nhập Google Cloud của bạn được thiết lập chính xác
2. **Kiểm Tra Kết Nối Internet**: API yêu cầu kết nối internet hoạt động
3. **Kiểm Tra Đầu Vào Âm Thanh**: Đảm bảo micrô của bạn hoạt động bình thường
4. **Tương Thích Trình Duyệt**: Sử dụng Chrome hoặc Edge để có khả năng tương thích tốt nhất
5. **Chế Độ Dự Phòng**: Ứng dụng sẽ chuyển sang nhận dạng giọng nói dựa trên trình duyệt nếu Google Cloud API không hoạt động
6. **Nói Rõ Ràng**: Phát âm từ rõ ràng và tránh tiếng ồn nền
7. **Sử Dụng Lệnh Đơn Giản**: Bắt đầu với các lệnh đơn giản như "lương 100" trước khi thử các lệnh phức tạp hơn
8. **Kiểm Tra Định Dạng Lệnh**: Đảm bảo bạn đang sử dụng một trong các định dạng lệnh được hỗ trợ
