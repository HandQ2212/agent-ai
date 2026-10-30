# Agent Lab — Web tương tác

Tại thư mục gốc dự án, cài `requirements.txt` rồi chạy:

```sh
python3 code_web/server.py
```

Mở `http://127.0.0.1:8000`. `index.html`, `styles.css`, `app.js` là giao diện; `server.py` cung cấp API kết nối agent Python, classifier và kết quả đã lưu. `test_web.py` kiểm tra chức năng của lớp kết nối.

- **Tổng quan:** đọc số liệu mô phỏng đã lưu.
- **Trợ lý mua sắm:** chạy các agent thật, hiển thị sản phẩm và trace; có kịch bản lỗi.
- **Thí nghiệm RL:** biểu đồ và bảng từ kết quả đã lưu, không huấn luyện lại trong web.
- **Phân loại ý định:** gọi checkpoint PyTorch đã train; dữ liệu là tổng hợp.

GitHub Pages chỉ chạy nội dung tĩnh, không chạy `server.py`. Nếu muốn công khai web tương tác, cần đưa cả ứng dụng Python lên một dịch vụ hỗ trợ máy chủ và cấu hình phù hợp. `demo_slides.html` là trang slide tĩnh cũ.
