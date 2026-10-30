# Phụ lục kết quả đo và bằng chứng thực thi

Các bảng dưới được dựng trực tiếp từ CSV/JSON của lần chạy đầy đủ. Mọi mean cấu hình là trung bình qua năm seed 11, 22, 33, 44, 55; SD dùng ddof=1. Các ảnh là biểu đồ vẽ từ dữ liệu episode thực thi, không phải ảnh minh họa sinh bằng mô hình.

## Bảng tổng hợp thí nghiệm alpha và epsilon

| Cấu hình | Train mean | Eval mean | SD | CI95 ± | Discount (%) |
| --- | --- | --- | --- | --- | --- |
| baseline | 33.6513 | 34.0997 | 1.3678 | 1.6981 | 16.16 |
| alpha_001 | 32.0944 | 33.6484 | 2.1286 | 2.6425 | 19.91 |
| alpha_050 | 31.8520 | 31.9533 | 4.1613 | 5.1661 | 38.08 |
| epsilon_005 | 32.9458 | 33.3973 | 1.6126 | 2.0020 | 27.90 |
| epsilon_030 | 30.8822 | 31.4300 | 3.9272 | 4.8755 | 33.88 |


## So sánh công bằng với cùng đối thủ

| Focal policy | Mean reward/step | SD giữa seed |
| --- | --- | --- |
| RL | 34.0997 | 1.3678 |
| Rule | 35.1295 | 0.1261 |
| Never | 35.1295 | 0.1261 |
| Always | 24.9722 | 0.0701 |
| DP | 35.1295 | 0.1261 |


## Thí nghiệm biến đổi discount 40%

| Policy | Mean reward/step | SD giữa seed |
| --- | --- | --- |
| frozen_RL | 32.6415 | 3.3620 |
| retrained_RL | 33.6009 | 3.3403 |
| Rule | 35.1295 | 0.1261 |
| DP | 35.1295 | 0.1261 |


## Q-table minh họa seed 42

| Demand | Opponent previous | Q(no discount) | Q(discount) | Greedy action |
| --- | --- | --- | --- | --- |
| 0 | 0 | 184.212867 | 199.449036 | 1 |
| 0 | 1 | 221.956047 | 181.668010 | 0 |
| 1 | 0 | 227.279761 | 235.197513 | 1 |
| 1 | 1 | 197.471701 | 218.162589 | 1 |


## Từng seed của baseline

| Seed | RL mean | Rule mean cùng tape | RL discount (%) |
| --- | --- | --- | --- |
| 11 | 35.1825 | 35.1825 | 0.00 |
| 22 | 32.5267 | 35.0910 | 40.70 |
| 33 | 32.6863 | 35.2710 | 40.12 |
| 44 | 34.9350 | 34.9350 | 0.00 |
| 55 | 35.1680 | 35.1680 | 0.00 |


## Cặp learner trong self-play

| Seed | Learner | Eval mean | Discount (%) |
| --- | --- | --- | --- |
| 11 | 0 | 30.5514 | 19.64 |
| 11 | 1 | 32.5935 | 40.21 |
| 22 | 0 | 35.0545 | 0.00 |
| 22 | 1 | 35.1300 | 0.00 |
| 33 | 0 | 35.3565 | 0.00 |
| 33 | 1 | 35.4800 | 0.00 |
| 44 | 0 | 34.8160 | 0.00 |
| 44 | 1 | 34.7835 | 0.00 |
| 55 | 0 | 34.8630 | 0.00 |
| 55 | 1 | 35.0500 | 0.00 |


## Đối chiếu bản gốc và bản mở rộng seed 42

Cùng seed số học không tạo cùng chuỗi khi cách dùng RNG khác. Bảng này ghi hai protocol riêng; không lấy chênh lệch làm bằng chứng chất lượng một thuật toán khác.

| Protocol | Focal mean | Opponent mean |
| --- | --- | --- |
| Code gốc nguyên văn | 35.1275 | 34.9685 |
| Bản mở rộng, split RNG | 25.5591 | 24.6856 |


\begin{center}
\includegraphics[width=0.98\linewidth]{results/assignment/learning_curve.png}
\captionof{figure}{Learning curve baseline: moving average 100 episode, mean và một SD qua năm seed.}
\end{center}

\begin{center}
\includegraphics[width=0.98\linewidth]{results/assignment/learning_rates.png}
\captionof{figure}{So sánh ba learning rate với cùng epsilon schedule.}
\end{center}

\begin{center}
\includegraphics[width=0.98\linewidth]{results/assignment/exploration.png}
\captionof{figure}{So sánh ba cấu hình epsilon; mọi cấu hình đánh giá với epsilon bằng 0.}
\end{center}

\begin{center}
\includegraphics[width=0.98\linewidth]{results/assignment/evaluation.png}
\captionof{figure}{Policy đóng băng: mean và SD giữa seed; đường 35 là kỳ vọng lý thuyết.}
\end{center}

\begin{center}
\includegraphics[width=0.98\linewidth]{results/assignment/q_and_sensitivity.png}
\captionof{figure}{Q-table seed 42 và độ nhạy lợi nhuận tức thời theo discount fraction.}
\end{center}

## Mã Python cốt lõi

Đây là các đoạn mã được lấy trực tiếp từ nguồn đã thực thi. Tệp đầy đủ và bản tham chiếu có trong thư mục assignment; các đoạn bên dưới đủ để kiểm cách cập nhật, tách evaluation và tính oracle.

\lstinputlisting[firstline=60,lastline=73,caption={Q-learning và luật, trích từ mã chạy}]{assignment/agent02_experiment.py}
\lstinputlisting[firstline=106,lastline=118,caption={Quy hoạch động hữu hạn chân trời}]{assignment/agent02_experiment.py}
\lstinputlisting[firstline=120,lastline=149,caption={Đánh giá đóng băng với common random numbers}]{assignment/agent02_experiment.py}

## Bằng chứng kiểm thử

Bộ kiểm thử assignment có 12 ca, đã chạy thành công. Các ca kiểm công thức ví dụ 4.65; terminal không bootstrap; observation sau joint action; từ chối action sai; margin; bảng luật; Q không đổi khi đánh giá; tổng action counts; tái lập evaluation; DP chọn không giảm; tái lập training; và sample mean gần kỳ vọng 35 khi số episode lớn.

\begin{verbatim}
python3 -m unittest discover -s assignment -p 'test_*.py'
............
Ran 12 tests
OK
\end{verbatim}

Log thực tế được giữ trong build/assignment_tests.log. Thời lượng đo cụ thể phụ thuộc máy, nên không dùng thời lượng test làm chỉ số thuật toán. Mười hai test không chứng nhận mô hình kinh tế đúng ngoài thực tế; chúng kiểm những bất biến quan trọng của implementation.
