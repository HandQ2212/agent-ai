# Bàn giao cho Antigravity

Đưa toàn bộ thư mục này lên repository và branch người dùng đã chỉ định. Nếu chưa có thông tin đích, hỏi địa chỉ repository và branch trước khi push. Không tự chọn tài khoản hoặc force-push.

Cấu trúc đã được phân thành `dataset/`, `code_agent/`, `code_web/`, `ket_qua/` và `notebooks/`. Giữ `ket_qua/` vì checkpoint, biểu đồ và các notebook đang sử dụng những tệp này. Dataset và kết quả là dữ liệu tổng hợp/mô phỏng.

Trước khi commit, xem trạng thái Git và chạy:

```sh
python3 code_agent/tutorial/thuc_hanh_tong_hop.py
python3 -m unittest discover -s code_agent/tutorial -p 'test_*.py'
python3 -m unittest discover -s code_agent/assignment -p 'test_*.py'
python3 -m unittest discover -s code_web -p 'test_*.py'
```

Sau đó commit, push lên đúng remote/branch, và báo lại URL, commit cùng kết quả kiểm thử. `.gitignore` loại môi trường ảo, cache và file bí mật. Phần `code_web/` gồm giao diện và `server.py` kết nối agent Python. GitHub Pages không chạy backend Python; để có API cần dịch vụ chạy server riêng.

Notebook huấn luyện chung: `notebooks/train_agent02.ipynb` (PyTorch và Q-learning); kết quả demo train riêng trong `ket_qua/notebook_train/`.
