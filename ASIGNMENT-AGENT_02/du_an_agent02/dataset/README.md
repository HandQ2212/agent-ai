# Dataset

`intent_dataset.csv` là dataset tổng hợp phục vụ classifier ý định của tutorial, gồm 432 câu, ba lớp `ecommerce`, `tourism`, `healthcare_admin` và các split được chia theo họ động từ. Tệp được `code_agent/tutorial/train_intent.py` đọc trực tiếp; train chỉ dùng vocabulary từ phần train, validation dùng chọn mô hình/ngưỡng và test để đánh giá.

Tập này được tạo từ template, một số đối tượng dùng chung giữa các split; kết quả trên tập test không đại diện chất lượng sử dụng thực tế. Dữ liệu kho/sản phẩm là ví dụ khai báo trong code; dữ liệu assignment được sinh bằng mô phỏng. Kết quả training và evaluation được lưu riêng trong `ket_qua/`.
