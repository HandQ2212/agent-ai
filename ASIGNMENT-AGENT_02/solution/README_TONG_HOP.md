# Báo cáo tổng hợp Agent 02

Bản PDF `../agent02_CT_04_hainn.pdf` gộp tutorial, phân tích cả hai paper và toàn bộ assignment vào một báo cáo có chung bìa, mục lục và tài liệu tham khảo. Bản PDF chứa hướng dẫn từng bước, kết quả thực thi và **mã nguồn đầy đủ của sáu tệp tutorial**, bao gồm baseline theo slide, hệ đa tác tử, mô hình PyTorch, demo, benchmark và kiểm thử.

Thư mục `tutorial/` chứa mã Python gốc có thể chạy. Để in code tiếng Việt trong PDF bằng pdfLaTeX, `report/code_ascii/` là bản dùng escape Unicode; cấu trúc cú pháp được đối chiếu với mã gốc bằng AST. Nên dùng các file gốc trong `tutorial/` khi thực hành.

## Chạy tutorial

Tại thư mục `solution/`:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 tutorial/slide_baseline.py
python3 tutorial/mas_system.py
python3 tutorial/train_intent.py
python3 tutorial/thuc_hanh_tong_hop.py
python3 tutorial/evaluate_mas.py
python3 -m unittest discover -s tutorial -p 'test_*.py' -v
```

Checkpoint, dữ liệu tổng hợp, kết quả và biểu đồ đã được kèm theo trong `results/tutorial/`. Đầu ra thực tế của demo và 17 kiểm thử được in trong PDF và lưu tại `build/tutorial_thuc_hanh_output.txt`, `build/tutorial_thuc_hanh_tests.txt`. Dữ liệu học chỉ phục vụ mô phỏng, bao gồm cả các ví dụ ngoài miền bị mô hình định tuyến sai được báo trung thực.

Notebook `tutorial_CT_04_hainn.ipynb` có 14 ô code đã thực thi và lưu output; bản HTML có thể xem offline. Notebook assignment đi kèm 15 ô code đã thực thi. File `tutorial/demo_slides.html` là bản thuyết trình ngắn.

## Chạy assignment

```sh
python3 assignment/agent02_experiment.py
python3 assignment/analyze_exact.py
python3 -m unittest discover -s assignment -p 'test_*.py'
```

Chương trình đầy đủ thực hiện 36 lần huấn luyện, mỗi lần 5.000 episode × 20 bước; dữ liệu thực nghiệm cũ đã được lưu trong `results/assignment/`. Tệp `assignment/reference_agent02.py` là code gốc giảng viên cung cấp; bản mở rộng được ghi rõ những thay đổi về RNG và đánh giá trong báo cáo.

## Dựng lại báo cáo

Cần pdfLaTeX và TeX Live có font T5/VNR, babel tiếng Việt, TikZ, tcolorbox, listings và longtable. Mã nguồn LaTeX của các phần đã được chuẩn bị, do đó không cần Pandoc khi chỉ biên dịch lại.

```sh
python3 build_combined_report.py
```

Script kiểm cấu trúc cú pháp của bản code dùng để in, chạy pdfLaTeX ba lượt, kiểm nội dung chính rồi tạo `../agent02_CT_04_hainn.pdf`. Nếu thay đổi các ví dụ tutorial, chạy lại demo và test, lưu output vào hai file trong `build/` trước khi biên dịch:

```sh
python3 tutorial/thuc_hanh_tong_hop.py > build/tutorial_thuc_hanh_output.txt
python3 -m unittest discover -s tutorial -p 'test_*.py' -v > build/tutorial_thuc_hanh_tests.txt 2>&1
python3 build_combined_report.py
```
