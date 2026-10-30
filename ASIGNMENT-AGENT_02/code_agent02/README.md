# Code thực hành Agent 02

Thư mục này chứa code chạy độc lập cho tutorial và assignment trong báo cáo tổng hợp.

- `tutorial/`: hệ đa tác tử mua hàng, mô hình PyTorch, mã chạy ví dụ, benchmark và kiểm thử.
- `assignment/`: Q-learning, agent theo luật, thí nghiệm, phân tích quy hoạch động và kiểm thử.
- `results/`: dữ liệu tổng hợp, checkpoint mô hình, kết quả thí nghiệm và biểu đồ đã chạy.
- Hai file `.ipynb`: notebook có sẵn output, có thể mở bằng Jupyter hoặc VS Code.

## Chuẩn bị

Chạy các lệnh tại thư mục `code_agent02`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Dữ liệu đi kèm là dữ liệu mô phỏng; không cần API key hoặc GPU.

## Tutorial

```sh
python3 tutorial/slide_baseline.py
python3 tutorial/mas_system.py
python3 tutorial/train_intent.py
python3 tutorial/thuc_hanh_tong_hop.py
python3 tutorial/evaluate_mas.py
python3 -m unittest discover -s tutorial -p 'test_*.py' -v
```

`train_intent.py` sẽ huấn luyện lại mô hình và ghi kết quả vào `results/tutorial/`. Đã có checkpoint đi kèm nên có thể chạy ngay `thuc_hanh_tong_hop.py`. Benchmark ghi lại kết quả vào cùng thư mục.

## Assignment

```sh
python3 assignment/agent02_experiment.py
python3 assignment/analyze_exact.py
python3 -m unittest discover -s assignment -p 'test_*.py' -v
```

`agent02_experiment.py` thực hiện toàn bộ 36 lượt huấn luyện, mỗi lượt 5.000 episode × 20 bước; lệnh này cần thời gian và sẽ ghi lại `results/assignment/`. File `reference_agent02.py` là bản code gốc được cung cấp trong đề.

Notebook mặc định đọc kết quả đã lưu và chạy ví dụ kiểm chứng; muốn chạy lại toàn bộ thí nghiệm, bật `RUN_FULL_EXPERIMENT` hoặc dùng lệnh bên trên.
