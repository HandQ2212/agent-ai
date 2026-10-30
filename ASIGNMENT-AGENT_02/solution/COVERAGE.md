# Đối chiếu yêu cầu với sản phẩm

| Yêu cầu | Vị trí trong báo cáo | Mã / bằng chứng |
|---|---|---|
| Tutorial 20 chủ đề | Tutorial Unit 1–20 | tutorial.md, notebook |
| PEAS, tối thiểu 3 agent | Unit 3, 5; Exercise 1 | 4 worker + coordinator trong mas_system.py |
| Chạy/mở rộng shopping | Unit 8–9; Exercise 2 | InventoryAgent, PolicyAgent, Coordinator |
| Intent PyTorch đã train | Unit 10; Exercise 3 | train_intent.py, checkpoint, dataset/predictions CSV |
| Test held-out, precision/recall từng lớp | Kết quả classifier | intent_metrics.json, confusion matrix |
| Confidence threshold/clarification | Unit 10 | Router, validation threshold; OOD probes |
| Timeout thật | Unit 11; Exercise 4 | asyncio.wait_for, test_timeout |
| Empty/malformed/stale | Unit 11, 17 | test_unknown, test_empty, test_malformed, test_stale |
| Tối thiểu 8 tests/3 failure tests | Unit 18 | 17 tests, tutorial_tests.log |
| So sánh single/MAS/learned/ablation | Unit 16; Exercise 5 | evaluate_mas.py, 880 benchmark records |
| Source, README, diagram | Unit 3, 5 và README | nguồn Python, TikZ trong báo cáo |
| Demo/presentation | Unit 20 | demo_slides.html, notebook |
| Paper MAS đủ nội dung chính | Paper phần 2 | paper_mas.md; source map Sections 1–7 |
| Paper RL đủ nội dung chính | Paper phần 3 | paper_rl.md; source map I–VII |
| Paper dài, chi tiết, có phản biện | 18 chuyên đề, synthesis, bản đồ đọc | paper_technical.md, paper_synthesis.md |
| Bìa/mẫu báo cáo cũ | Cả ba PDF | PTIT logo gốc; assignment_format.sty, cover |
| Assignment baseline A | Thí nghiệm A | baseline_42_*; reference_original_42_* |
| Learning curve B | Thí nghiệm B | episode CSV, learning_curve.png |
| Ba learning rates C | Thí nghiệm C | alpha_001, baseline, alpha_050 |
| Ba exploration settings D | Thí nghiệm D | schedule, fixed 0.05, fixed 0.30 |
| Frozen fair evaluation E | Thí nghiệm E | fair_comparison.csv, Q freeze assertion |
| Multi-seed mean/SD | Thiết lập và phụ lục | 5 seeds mỗi configuration, aggregate.csv |
| Câu 1 mô hình | Trả lời Câu 1 | Environment, quan sát/full state |
| Câu 2 học so với luật | Câu 2 | QLearningAgent, RuleBasedAgent |
| Câu 3 Q=4.65 | Câu 3 | test_update_example |
| Câu 4 epsilon | Câu 4 | exploration.csv/configurations.csv |
| Câu 5 margin 5 và 3 | Câu 5 | expected_profit, bảng lý thuyết |
| Câu 6 trung bình reward | Câu 6 | 255591/10000, bảng multi-seed |
| Câu 7 alpha | Câu 7 | aggregate + learning_rates.png |
| Câu 8 non-stationarity | Câu 8 | self-play 5 seeds, selfplay_summary.csv |
| Câu 9 thay môi trường đã chạy | Câu 9 | discount 40%, frozen/retrained comparisons |
| Câu 10 agent tốt hơn | Câu 10 | exact_best_response; DP và fair evaluation |
| Kiểm policy không lấy mẫu | Chuyên đề và phần bổ sung assignment | analyze_exact.py, exact_policy_values.csv |
| Đủ source và code trích trong PDF | Phụ lục | lstinputlisting lấy trực tiếp code đã chạy |
| Kết luận, giới hạn và tham khảo | Cuối mỗi báo cáo | references.tex, JSON/CSV thực thi |
