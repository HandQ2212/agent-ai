# Dự án Agent 02

Dự án được phân tách theo dữ liệu, mã agent và mã web:

```text
du_an_agent02/
├── dataset/                 # Dữ liệu đầu vào để train/test
├── code_agent/
│   ├── tutorial/            # Multi-agent shopping, PyTorch, benchmark, test
│   └── assignment/          # Q-learning, rule-based, thí nghiệm, test
├── code_web/                # Giao diện web và máy chủ kết nối agent
├── ket_qua/
│   ├── tutorial/            # Checkpoint, metrics, dự đoán và biểu đồ
│   └── assignment/          # CSV, Q-table và biểu đồ thực nghiệm
├── notebooks/               # Notebook train chung và notebook thực hành
└── requirements.txt
```

**Phạm vi web:** `code_web/` có giao diện tương tác và máy chủ Python kết nối trực tiếp với agent, classifier đã train và kết quả thí nghiệm. Mọi sản phẩm và dữ liệu đều là mô phỏng. Trang trình chiếu `demo_slides.html` vẫn có thể mở riêng.

## Cài đặt

Tại thư mục `du_an_agent02`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Dataset

`dataset/intent_dataset.csv` chứa 432 câu tiếng Việt tổng hợp có nhãn và split: 270 train, 54 validation, 108 test. `code_agent/tutorial/train_intent.py` đọc trực tiếp tệp này khi huấn luyện. Các cột `text`, `label`, `class`, `group`, `split` thể hiện nội dung, nhãn và cách chia dữ liệu.

Dữ liệu sản phẩm và tồn kho của ví dụ shopping được khai báo trong `code_agent/tutorial/mas_system.py`. Assignment tạo dữ liệu bán hàng ngẫu nhiên từ mô hình mô phỏng, không đọc một dataset bán hàng thực tế. Dữ liệu sinh ra từ thí nghiệm và số liệu đánh giá nằm trong `ket_qua/`.

## Chạy agent tutorial

```sh
python3 code_agent/tutorial/slide_baseline.py
python3 code_agent/tutorial/mas_system.py
python3 code_agent/tutorial/train_intent.py
python3 code_agent/tutorial/thuc_hanh_tong_hop.py
python3 code_agent/tutorial/evaluate_mas.py
python3 -m unittest discover -s code_agent/tutorial -p 'test_*.py' -v
```

Checkpoint đã có trong `ket_qua/tutorial/intent_model.pt`; có thể chạy `thuc_hanh_tong_hop.py` ngay sau khi cài thư viện. Chạy lại `train_intent.py` sẽ ghi lại checkpoint và kết quả đánh giá, nhưng sử dụng dataset đầu vào trong `dataset/`.

## Chạy agent assignment

```sh
python3 code_agent/assignment/agent02_experiment.py
python3 code_agent/assignment/analyze_exact.py
python3 -m unittest discover -s code_agent/assignment -p 'test_*.py' -v
```

Thí nghiệm mặc định chạy 36 lượt training, mỗi lượt 5.000 episode × 20 bước, và ghi lại kết quả trong `ket_qua/assignment/`. File `reference_agent02.py` là code gốc của đề và khi chạy sẽ tạo thư mục kết quả riêng theo cấu hình của nó.

## Chạy web tương tác

Cài dependencies ở bước trên, sau đó chạy từ thư mục dự án:

```sh
python3 code_web/server.py
```

Mở `http://127.0.0.1:8000`. Giao diện có trợ lý mua sắm gọi agent Python thật, kiểm tra kịch bản lỗi, phân loại ý định bằng PyTorch và xem số liệu Q-learning đã lưu. Bắt đầu tại trang **Tổng quan** và chuyển trang bằng menu. Bấm Ctrl+C để dừng máy chủ.

```sh
python3 -m unittest discover -s code_web -p 'test_*.py' -v
```

Có thể đổi cổng bằng `python3 code_web/server.py --port 8080`. Để phục vụ từ địa chỉ mạng được chỉ định, dùng `--host` và `--port`. GitHub lưu mã nguồn; **GitHub Pages chỉ phục vụ trang tĩnh và không chạy máy chủ Python**, vì vậy các API của web này cần chạy máy chủ Python riêng. Trang trình chiếu tĩnh cũ nằm ở `code_web/demo_slides.html`.

## Notebook

**Notebook huấn luyện tổng hợp:** `notebooks/train_agent02.ipynb` gom các bước train classifier PyTorch và Q-learning, kèm giải thích, biểu đồ, đánh giá và output đã chạy. Mặc định train 120 epoch và 5.000 episode với seed 42; kết quả lưu riêng trong `ket_qua/notebook_train/`. Bật `RUN_FULL_EXPERIMENT = True` nếu muốn chạy lại toàn bộ 36 lượt thí nghiệm.

Mở notebook trong `notebooks/` bằng Jupyter hoặc VS Code. Các notebook đã lưu output từ lần chạy trước và có thể chạy lại từ thư mục dự án hoặc thư mục `notebooks/`. Hai notebook thực hành cũ mặc định đọc kết quả đã có. Notebook `train_agent02.ipynb` mặc định chạy train minh họa và lưu kết quả riêng; chỉ bật tùy chọn toàn bộ thí nghiệm khi muốn tạo lại đầy đủ dữ liệu.

## Đưa lên GitHub và Render

Xem hướng dẫn từng bước trong `HUONG_DAN_DEPLOY.md`. Dự án có `render.yaml` và `requirements-render.txt` để deploy web có backend Python lên Render Web Service.
