# Paper 1: Cơ chế cộng tác đa tác tử dựa trên LLM

## Hồ sơ tài liệu, phạm vi và cách tiếp cận

**Tài liệu được phân tích:** Khanh-Tung Tran, Dung Dao, Minh-Duong Nguyen, Quoc-Viet Pham, Barry O’Sullivan và Hoang D. Nguyen, *Multi-Agent Collaboration Mechanisms: A Survey of LLMs*, arXiv:2501.06322v1, công bố ngày 10/01/2025, 35 trang. Báo cáo bám bản PDF giảng viên cung cấp, không thay bản này bằng một phiên bản khác xuất hiện sau đó. Các nhận định về nội dung paper được đối chiếu trực tiếp với Sections 1–7 và các bảng, hình trong bản PDF. \cite{tran}

Đây là một bài **survey về cơ chế phối hợp**, không phải paper đề xuất một thuật toán tối ưu duy nhất và đánh giá nó bằng một thí nghiệm thống nhất. Vì vậy, câu hỏi đọc hiểu thích hợp là: tác giả tổ chức lĩnh vực như thế nào, khung phân loại có giúp phân biệt thiết kế không, và các luận điểm tổng quát được hỗ trợ đến đâu? Việc chỉ kể tên AutoGen, MetaGPT hoặc các agent nổi tiếng sẽ bỏ qua đóng góp trọng tâm của bài.

Báo cáo triển khai ba lớp: diễn giải nội dung gốc; phân tích kỹ thuật và phản biện của người viết; liên hệ với mã tutorial và assignment đã chạy. Những phương trình chi phí, thiết kế kiểm chứng và ví dụ thương mại điện tử do báo cáo phát triển sẽ được gọi rõ là phân tích hoặc đề xuất. Không có thí nghiệm gọi LLM trong bộ mã đi kèm; do đó kết quả mô phỏng chỉ minh họa cơ chế phối hợp, không tái lập benchmark của các hệ LLM được paper tổng thuật.

## Vấn đề nghiên cứu và động lực

Một LLM có thể tạo văn bản, viết mã và giải một số bài toán suy luận, nhưng vẫn có giới hạn về thông tin có sẵn, độ dài ngữ cảnh, độ tin cậy của hành động và khả năng tự kiểm tra. Tác giả đặt vấn đề chuyển từ cải thiện một mô hình đơn lẻ sang tổ chức nhiều tác tử có thể chia sẻ công việc. Ý tưởng hấp dẫn ở chỗ mỗi thành viên phụ trách một phần nhỏ hơn, có công cụ và góc nhìn riêng, rồi một cơ chế phối hợp tạo ra lời giải chung.

Tuy nhiên, phân chia công việc phát sinh một bài toán mới: làm sao kết quả của các thành viên tương thích? Một agent truy hồi có thể lấy đúng đoạn dữ liệu nhưng agent tổng hợp diễn giải sai; agent lập kế hoạch có thể đề xuất bước ngoài quyền của agent thực thi; hai agent có thể cùng sửa một tài nguyên. Khi ấy năng lực của hệ thống bị giới hạn bởi chất lượng quan hệ giữa các thành viên. Đó là lý do paper đặt **collaboration channels** ở trung tâm phân tích.

Một ví dụ xuyên suốt của báo cáo là trợ lý mua hàng. Agent danh mục truy hồi sản phẩm, agent đề xuất xếp hạng, agent kho kiểm tra số lượng và agent chính sách kiểm tra ngân sách. Nếu chỉ cộng bốn văn bản trả lời lại, hệ thống có thể khuyến nghị một sản phẩm hết hàng hoặc vượt ngân sách. Giá trị của phối hợp nằm ở điều kiện chuyển giao: ID sản phẩm phải tồn tại, giá phải lấy từ danh mục có thẩm quyền, thông tin kho phải còn mới và kết quả cuối phải được kiểm tra.

Phân tích của người viết: việc tăng số agent làm tăng số cơ hội trao đổi thông tin nhưng cũng tăng số điểm có thể hỏng. Một mô hình đơn với công cụ tốt có thể hoàn thành bài đơn giản nhanh hơn một nhóm nhiều agent. Bởi vậy, lý do xây MAS cần gắn với yêu cầu phân quyền, chuyên môn, dữ liệu phân tán hoặc quyết định tương tác, rồi kiểm tra lợi ích bằng baseline tương xứng. Đây là một luận điểm kỹ thuật cần mang theo khi đọc các lời hứa về trí tuệ tập thể.

## Đóng góp và vị trí của survey

Trong Section 1.2, tác giả nêu bốn hướng đóng góp: khảo sát cơ chế phối hợp giữa các LLM agent; đưa ra một framework tổng hợp; xem xét ứng dụng; và rút ra bài học cùng vấn đề mở. Bảng so sánh các survey ở phần đầu bài nhằm cho thấy nghiên cứu này tập trung vào phương diện *cách cộng tác diễn ra*, thay vì chỉ liệt kê ứng dụng hoặc mô tả vòng đời agent.

Đóng góp đầu tiên là một **ngôn ngữ phân tích chung**. Cùng dùng LLM nhưng một hệ có thể phối hợp qua bỏ phiếu, một hệ qua chia vai và một hệ qua mô hình dự đoán đối tác. Nếu gọi chung cả ba là “multi-agent reasoning”, người đọc sẽ khó biết yếu tố nào tạo ra hiệu quả. Framework tách loại quan hệ, chiến lược, cấu trúc và điều phối, nhờ đó cho phép mô tả một thiết kế theo nhiều chiều độc lập.

Đóng góp thứ hai là nối các hướng nghiên cứu thường nằm riêng: MAS cổ điển, hệ nhiều LLM, cộng tác người–máy, chia sẻ mô hình và mô phỏng xã hội. Phạm vi rộng giúp nhận ra những điểm chung về thông tin, mục tiêu và điều phối. Đổi lại, phạm vi này khiến một vài ví dụ khác nhau đáng kể về cơ chế: một khách hàng federated learning và một tác tử hội thoại không có cùng chu trình hành động hay độ tự chủ. Khi áp dụng framework, cần ghi rõ cấp độ trừu tượng đang xét.

Về phương pháp, bài tự mô tả việc phân tích các nghiên cứu và tổng hợp đặc trưng. Báo cáo không tìm thấy một quy trình tìm kiếm, sàng lọc và đánh giá chất lượng theo chuẩn systematic review được mô tả đầy đủ như một sơ đồ PRISMA. Do đó nên đọc các bảng của bài như bản đồ có tổ chức của tài liệu được chọn, không xem đó là thống kê bao phủ hoàn toàn mọi công bố trong lĩnh vực. Đây là giới hạn phương pháp, không làm mất giá trị của taxonomy.

## Nền tảng: MAS, LLM và collaborative AI

Section 2.1 mô tả MAS bằng bốn nhóm thành phần: tác tử, môi trường, tương tác và tổ chức. Tác tử có vai trò, năng lực và chính sách hành vi; môi trường cung cấp điều kiện để quan sát và hành động; tương tác gồm trao đổi thông tin, phối hợp hoặc thương lượng; tổ chức xác định quan hệ kiểm soát. Một hệ nhiều mô hình chỉ trở thành MAS theo nghĩa hữu ích khi có các thành viên và quan hệ tương tác đủ rõ để phân tích.

Section 2.2 đặt LLM vào vai trò bộ xử lý trung tâm của tác tử. Mô hình có thể tiếp nhận chỉ dẫn, suy luận trên văn bản và tạo lời gọi công cụ. Nhưng “LLM là bộ não” chỉ là phép diễn giải kiến trúc. Bộ nhớ, quyền truy cập, giao thức thông điệp, vòng lặp công cụ và tiêu chí dừng vẫn phải được thiết kế. Khả năng sinh một câu “đã kiểm tra kho” không đồng nghĩa với việc một truy vấn kho hợp lệ đã được thực hiện.

Section 2.3 xem collaborative AI như hướng phối hợp giữa các hệ AI hoặc giữa AI và con người. Hợp tác là một trường hợp; tranh luận, cạnh tranh và vừa hợp tác vừa cạnh tranh cũng thuộc phổ tương tác mà paper xem xét. Từ đó cần phân biệt mục tiêu ở hai cấp: hai thành viên có thể bất đồng ở cấp lập luận nhưng vẫn cùng phục vụ chất lượng đáp án cuối của hệ thống.

Ví dụ phản biện: một người viết và một người kiểm chứng có thể dùng hai system prompt khác nhau nhưng cùng một mô hình, cùng dữ liệu và cùng thiên kiến. Chia vai làm thay đổi quá trình xử lý, chưa chứng minh hai nguồn sai số độc lập. Muốn đánh giá tính bổ sung, cần đo tỷ lệ lỗi chung, độ đa dạng của bằng chứng và khả năng phát hiện sai của người kiểm chứng, thay vì đếm số persona.

## Mô hình hóa tác tử và hệ cộng tác

Ở Section 3.1, tác giả biểu diễn một agent bằng bộ $a=\{m,o,e,x,y\}$: mô hình, mục tiêu, môi trường/ngữ cảnh, đầu vào và đầu ra. Thành phần mô hình được mô tả thêm bằng kiến trúc, bộ nhớ và adapter. Với LLM, đầu vào thường là chuỗi token, ngữ cảnh chịu giới hạn cửa sổ và đầu ra có thể là văn bản hoặc hành động được mã hóa. Ký hiệu này tổ chức khái niệm, không phải một bộ phương trình bảo đảm tính tối ưu.

Hệ cộng tác gồm tập tác tử $\mathcal A$, mục tiêu chung $O$, môi trường chia sẻ $\mathcal E$, tập kênh $\mathcal C$, đầu vào và đầu ra hệ thống. Có thể diễn giải ngắn gọn:

$$y_{\mathrm{system}}=S(O,\mathcal E,x\mid \mathcal A,\mathcal C).$$

Điểm có ích là đầu ra phụ thuộc cả agent lẫn **kênh cộng tác**. Giữ nguyên các mô hình nhưng đổi ai nói trước, ai được thấy đầu ra nào và ai có quyền kết thúc có thể làm hành vi thay đổi. Điều này giải thích vì sao chỉ báo tên backbone chưa đủ để tái lập một thí nghiệm MAS.

Mỗi kênh cần mô tả: ai tham gia; mục tiêu hoặc nội dung trao đổi; loại quan hệ; cấu trúc kết nối; chiến lược đưa ra quyết định; điều kiện được tạo và kết thúc. Trong tutorial, lời gọi từ coordinator đến inventory là một kênh request–response hợp tác, tập trung, theo vai trò và có deadline. Đầu vào là danh sách ID; đầu ra là số lượng và tuổi dữ liệu. Mô tả này kiểm tra được bằng trace, khác với nhãn mơ hồ “agent kho hỗ trợ agent bán hàng”.

Framework gốc giả định các agent có nền tảng giao tiếp chung. Phân tích của báo cáo: cùng dùng tiếng Anh hoặc JSON mới giải quyết một phần cú pháp. Hai bên còn phải thống nhất đơn vị tiền, nghĩa của “available”, múi giờ, trạng thái lỗi, độ mới của dữ liệu và quyền hành động. Những chi tiết hợp đồng này quyết định liệu sự hiểu nhau có đúng ở mức vận hành hay chỉ đúng ở mức ngôn ngữ.

## Cộng tác sớm, giữa và muộn

Paper mô tả cộng tác ở các giai đoạn khác nhau. Cộng tác sớm có thể chia sẻ dữ liệu, ngữ cảnh hoặc biểu diễn đầu vào; cộng tác giữa có thể trao đổi tham số, trọng số hoặc adapter; cộng tác muộn kết hợp đầu ra hoặc hành động. Ba mức cho thấy cộng tác không đồng nghĩa với hội thoại bằng ngôn ngữ tự nhiên.

Chia sẻ ngữ cảnh giúp hai agent cùng thấy bằng chứng, nhưng có thể làm lan một nguồn sai chung. Chia sẻ mô hình giúp học từ nhiều nơi, nhưng kéo theo tương thích kiến trúc, quyền dữ liệu và bảo mật cập nhật. Kết hợp đầu ra đơn giản hơn về triển khai, nhưng không sửa được những lỗi đã bị mất khỏi các bản tóm tắt trung gian. Mỗi điểm kết nối làm thay đổi thứ thông tin còn có thể được kiểm chứng ở cuối quy trình.

Một thiết kế mua hàng có thể dùng cả ba mức: các agent đọc một catalog snapshot chung; mô hình intent được cập nhật theo dữ liệu tổng hợp; coordinator kết hợp các danh sách đề xuất đã qua kiểm tra. Tuy nhiên, bộ mã của báo cáo chỉ huấn luyện một classifier cục bộ và truyền dữ liệu có cấu trúc, không thực hiện federated learning hoặc trao đổi trọng số giữa nhiều tác tử. Việc liên hệ kiến trúc không phải tuyên bố đã triển khai mọi cấp độ trong survey.

## Ba loại quan hệ cộng tác

### Cooperation: mục tiêu được căn chỉnh

Trong hợp tác, các tác tử chia công việc để tăng chất lượng mục tiêu chung. Chuyên môn hóa giúp giảm phạm vi mỗi thành viên phải xử lý. Người tìm tài liệu có thể tập trung vào độ bao phủ; người kiểm chứng tập trung vào dẫn chứng; người biên tập tập trung vào tính mạch lạc. Các thành phần khác nhau không cần tối ưu một chỉ số cục bộ giống hệt nhau, nhưng kết quả phải phục vụ cùng tiêu chí nghiệm thu.

Rủi ro là mục tiêu cục bộ dễ lệch. Nếu agent đề xuất chỉ tối ưu điểm hấp dẫn, nó có thể chọn sản phẩm vượt ngân sách. Nếu agent tổng hợp chỉ tối ưu độ đầy đủ, nó có thể bổ sung thông tin không có trong nguồn. Vì vậy cần một hàm mục tiêu hoặc tập ràng buộc ở cấp hệ thống, cùng cơ chế kiểm tra đầu ra từng bước. “Cùng giúp người dùng” chưa phải hợp đồng phối hợp đủ chặt.

### Competition: bất đồng có cấu trúc

Cạnh tranh xuất hiện khi thành viên tối ưu lợi ích riêng hoặc được giao bảo vệ các lập luận trái chiều. Tranh luận có thể làm lộ giả định và lỗi suy luận, đặc biệt khi mỗi bên phải viện dẫn bằng chứng. Tuy nhiên, một agent phản đối mạnh không nhất thiết đưa ra phản biện đúng. Cơ chế phán quyết cần ưu tiên tính kiểm chứng, thay vì văn phong tự tin hoặc số lượng phát biểu.

Ví dụ của người viết: agent A đề xuất chọn sản phẩm p1 vì hiệu năng, agent B phản biện rằng p1 vượt ngân sách. Nếu giá p1 được xác nhận từ catalog, đây là phản biện có giá trị quyết định. Nếu B chỉ nói “có thể đắt”, coordinator chưa có đủ cơ sở. Sự khác biệt giữa phản đối và kiểm chứng phải được phản ánh trong dữ liệu thông điệp: claim, evidence, constraint và verdict nên là các trường riêng.

### Coopetition: hợp tác ở một cấp, cạnh tranh ở cấp khác

Trong coopetition, các bên có lợi ích vừa trùng vừa khác. Hai công ty có thể cùng dùng hạ tầng logistics nhưng cạnh tranh khách hàng; nhiều nhóm có thể phối hợp chia tài nguyên tính toán nhưng cạnh tranh thứ hạng. Thiết kế phải nêu rõ thứ gì được chia sẻ và thứ gì cần giữ riêng. Một mục tiêu chung không xóa bỏ xung đột lợi ích ở cấp tác tử.

Assignment bán hàng có hai lợi nhuận riêng và ảnh hưởng qua giảm giá. Nó là tương tác cạnh tranh về lợi nhuận, nhưng không tự động là trò chơi tổng bằng không: lượng mua của hai cửa hàng được lấy mẫu riêng, và không có ràng buộc tổng doanh số bằng một thị trường cố định. Gọi mọi biến động lợi nhuận là “một bên thắng thì bên kia thua” sẽ sai với mô hình đang dùng.

## Ba chiến lược: rule-based, role-based, model-based

| Chiến lược | Cơ chế chính | Thứ phải khai báo | Điểm dễ sai |
|---|---|---|---|
| Rule-based | Luật quyết định ai nói, nói khi nào, kết hợp ra sao | Điều kiện, ưu tiên, tiêu chí dừng | Luật thiếu trường hợp, xung đột thứ tự |
| Role-based | Phân công chuyên môn và trách nhiệm | Quyền, đầu vào, đầu ra, phạm vi | Chồng vai, bỏ sót nhiệm vụ, phụ thuộc dây chuyền |
| Model-based | Dự đoán môi trường, đối tác hoặc bất định để quyết định | Mô hình, quan sát, giả định, cách cập nhật | Dự đoán đối tác sai, chi phí lớn, khó kiểm chứng |

### Giao thức theo luật

Rule-based trong survey mô tả **giao thức tương tác**, chẳng hạn thứ tự tranh luận hoặc bỏ phiếu. Nó không đồng nhất với rule-based seller của assignment, nơi luật xác định hành động giảm giá. Một hệ có thể có agent học máy nhưng phối hợp theo luật cố định; ngược lại, một coordinator học cách phân việc có thể điều khiển các công cụ hoàn toàn xác định. Giữ riêng hai cấp tránh nhầm “có luật” với “không có học”.

Ưu điểm của luật là truy vết được: mỗi quyết định có điều kiện và nhánh xử lý cụ thể. Nhược điểm là khi không gian tình huống lớn, số điều kiện tăng và tương tác giữa luật khó quản lý. Thiết kế tốt thường giữ các bất biến quan trọng bằng luật, rồi cho phép mô hình đề xuất phương án bên trong miền hợp lệ. Đây là cấu trúc hybrid phù hợp với tutorial.

### Giao thức theo vai trò

Role-based đặt câu hỏi ai có chuyên môn hoặc tài nguyên thích hợp. MetaGPT là ví dụ paper dùng để minh họa quy trình có vai trò và SOP; AutoGen cung cấp cách tổ chức các agent có thể hội thoại, dùng công cụ hoặc tương tác với con người. Những ví dụ này cho thấy cấu trúc vai trò ảnh hưởng đến cách phân rã nhiệm vụ; chúng không tạo ra định lý rằng mọi quy trình nhiều vai đều tốt hơn mọi baseline. \cite{metagpt,autogen}

Một vai trò cần có khả năng bị kiểm tra và thay thế. Trong tutorial, CatalogAgent chỉ biết truy hồi ID; InventoryAgent chỉ cung cấp thông tin kho; PolicyAgent xác nhận nguồn gốc và ngân sách. Nếu thay ranker mà các hợp đồng không đổi, hệ còn chạy được. Đây là lợi ích thiết kế cụ thể của chia vai, ngay cả khi chất lượng tác vụ không tăng trên catalog nhỏ.

### Giao thức dựa trên mô hình

Model-based trong paper có thể bao gồm suy luận xác suất và Theory of Mind để dự đoán mục tiêu hoặc hành vi của bên khác. Thuật ngữ này có phạm vi khác “model-based RL” trong paper thứ hai, nơi mô hình thường là chuyển trạng thái và phần thưởng. Cả hai cùng dùng mô hình để hỗ trợ quyết định nhưng đối tượng mô hình hóa và bảo đảm lý thuyết khác nhau.

Nếu agent bán hàng dự đoán xác suất đối thủ giảm giá ở bước kế tiếp, nó có thể tính lợi nhuận kỳ vọng của các lựa chọn. Nhưng nếu đối thủ cũng cập nhật chiến lược, dự đoán vừa học sẽ lỗi thời. Cần đo chất lượng mô hình đối tác trên dữ liệu tương lai và đánh giá chính sách dưới nhiều loại đối thủ. Một mô hình mô tả tốt lịch sử chưa chắc dẫn đến quyết định tốt trong tương tác chiến lược.

## Cấu trúc giao tiếp và chi phí

### Tập trung

Trong cấu trúc tập trung, coordinator nhận yêu cầu, phân việc, thu kết quả và quyết định đầu ra. Nó giúp đặt ràng buộc và logging ở một điểm. Tutorial chọn cấu trúc này để trình tự kiểm chứng rõ và dễ tái lập. Hạn chế là coordinator có thể thành nút nghẽn và điểm hỏng chung. Chia các worker độc lập không giải quyết hỏng của chính bộ điều phối.

Với $n$ worker, một lượt request–response đến mọi worker cần xấp xỉ $2n$ thông điệp nếu bỏ qua retry. Chi phí tuyến tính này thuận tiện để dự toán. Tuy nhiên, mỗi request có thể chứa toàn bộ ngữ cảnh rất dài; số thông điệp nhỏ chưa chắc số token nhỏ. Vì vậy cần đo đồng thời số message, dung lượng payload và thời gian xử lý.

### Phi tập trung và phân tán

Trong cấu trúc phi tập trung, quyết định được chia giữa các thành viên. Cấu trúc phân tán nói về vị trí thực thi; phi tập trung nói về quyền kiểm soát. Một hệ chạy trên nhiều máy nhưng mọi quyết định qua một manager vẫn có thể là tập trung về điều khiển. Đây là phân biệt kỹ thuật của báo cáo để làm rõ những khái niệm được đặt gần nhau trong survey.

Nếu mọi agent trao đổi với mọi agent khác, một vòng có tối đa $n(n-1)$ thông điệp có hướng. Với $n=10$, đó là 90 thông điệp, chưa tính phản hồi và số vòng. Topology thưa, publish–subscribe hoặc giao tiếp theo sự kiện giúp giảm lưu lượng, nhưng cũng giới hạn thông tin mỗi thành viên nhìn thấy. Không có một topology tốt nhất độc lập với nhiệm vụ.

### Phân cấp

Cấu trúc phân cấp đưa các nhóm agent dưới manager cấp trung rồi tổng hợp lên trên. Nó giúp chia việc và giảm bề rộng ở nút gốc, nhưng làm tăng số chặng truyền. Thông tin bị tóm tắt qua nhiều cấp có thể mất chi tiết cần kiểm chứng. Một cơ chế tốt cho phép truy ngược từ kết luận về bằng chứng gốc, thay vì chỉ chuyển bản tóm tắt của bản tóm tắt.

Một cây phân cấp còn đòi hỏi chính sách khi manager con hỏng: giao lại nhóm, trả kết quả một phần hay dừng toàn nhiệm vụ? Lựa chọn phụ thuộc tác vụ. Một bản gợi ý mua hàng có thể loại sản phẩm chưa kiểm chứng; một quy trình giao dịch tài chính không thể tự coi phần thiếu là thành công. Cấu trúc giao tiếp phải gắn với nghĩa của thất bại.

## Điều phối tĩnh và động

Điều phối tĩnh thiết lập kênh và thứ tự trước khi nhận yêu cầu. Một pipeline catalog → ranker → policy → inventory là ví dụ. Ưu điểm là dễ kiểm tra số bước tối đa, quyền gọi công cụ và tình huống lỗi. Nó phù hợp khi cấu trúc tác vụ ổn định. Thêm một LLM vào từng bước không biến một quy trình đã cố định thành điều phối động.

Điều phối động cho phép tạo vai trò, chọn thành viên hoặc thay đồ thị thực hiện theo yêu cầu. Cách này có thể tiết kiệm khi chỉ gọi chuyên gia cần thiết, nhưng manager phải giải thêm bài toán lập kế hoạch. Một sơ đồ động sai có thể bỏ mất bước kiểm chứng bắt buộc. Do đó phần động nên chịu một lớp ràng buộc tĩnh: các bước tùy chọn có thể đổi, còn bất biến về nguồn gốc, quyền và xác nhận phải giữ.

Phân tích đồ thị của báo cáo: biểu diễn các bước bằng DAG $G=(V,E)$, cạnh thể hiện phụ thuộc dữ liệu. Tổng thời gian xấp xỉ đường găng cộng overhead điều phối; tổng chi phí bằng tổng công việc của mọi node được thực hiện. Song song hóa có thể giảm thời gian mà tăng tổng chi phí. Một đánh giá chỉ báo latency sẽ bỏ qua trade-off này.

## Bỏ phiếu, tranh luận và kiểm chứng

Bỏ phiếu đa số đơn giản, nhưng chỉ có lợi khi lỗi giữa các thành viên có mức độc lập đủ lớn. Giả sử ba bộ trả lời độc lập, mỗi bộ đúng với xác suất $p$, xác suất đa số đúng là $3p^2(1-p)+p^3$. Với $p=0.7$, kết quả là $0.784$. Đây là ví dụ xác suất do báo cáo tính, không phải kết quả thực nghiệm của survey.

Nếu cả ba sao chép cùng một lời giải sai, tính độc lập không còn. Khi sai số tương quan hoàn toàn, bỏ phiếu không cải thiện xác suất đúng so với một thành viên. Vì vậy nên ưu tiên đa dạng bằng chứng, công cụ hoặc cách kiểm tra thay vì chỉ đổi tên vai. Đếm phiếu có thể làm tăng độ tự tin trong khi không tăng độ đúng.

Tranh luận nhiều vòng cho phép sửa câu trả lời theo phản biện. Nghiên cứu của Du và cộng sự là một ví dụ gốc về cách nhiều mô hình đề xuất rồi trao đổi qua nhiều vòng. Nhưng kết quả cải thiện trên một số tác vụ không phải bảo đảm cho mọi cấu hình agent. Khi tái lập cần công bố số agent, số vòng, prompt, cách lấy đáp án và tổng ngân sách suy luận. \cite{debate}

Kiểm chứng bằng công cụ có vị trí khác bỏ phiếu. Nếu yêu cầu là tính tổng, trình tính có thể đưa ra phép kiểm xác định. Nếu yêu cầu là xác nhận còn hàng, chỉ dịch vụ kho có thẩm quyền mới trả lời được. Hai agent đồng ý rằng “còn hàng” không thay thế truy vấn kho. Bài học này được triển khai trực tiếp bằng trường `age_seconds` và kiểm tra freshness trong tutorial.

## Ứng dụng được survey phân tích

### Mạng 5G/B6G và Industry 5.0

Section 5.1 bàn về các hệ mạng, phân bổ tài nguyên, môi trường công nghiệp và phối hợp thông minh. Giá trị của MAS nằm ở quyết định phân tán, dữ liệu ở nhiều nơi và yêu cầu điều chỉnh theo trạng thái. Một tác tử cục bộ có thể phản ứng nhanh, trong khi cơ chế phối hợp tránh việc tối ưu cục bộ làm xấu chất lượng toàn mạng.

Thách thức triển khai là deadline, giới hạn tài nguyên và độ tin cậy. Một LLM tạo một phương án có vẻ hợp lý nhưng trả lời sau thời điểm cần hành động vẫn có thể không dùng được. Vì thế báo cáo đề xuất đánh giá tỷ lệ đáp ứng hạn, chi phí suy luận và vi phạm ràng buộc, bên cạnh chất lượng phương án. Phần này là cách chuyển chủ đề ứng dụng của survey thành tiêu chí kỹ thuật.

### Hỏi đáp và sinh ngôn ngữ

Section 5.2 xem xét phân rã câu hỏi, sử dụng chuyên gia, phản biện và tổng hợp. Một câu hỏi nhiều bước có thể cần truy hồi từ nhiều nguồn rồi hợp nhất. Chia vai giúp quan sát các bước trung gian, nhưng cũng tạo thêm khả năng mất ngữ cảnh hoặc bóp méo bằng chứng. Cần lưu provenance từ mỗi claim đến đoạn nguồn.

Đánh giá chỉ bằng độ trôi chảy sẽ bỏ qua sự thật. Với hỏi đáp, nên tách độ đúng của đáp án, độ đúng của dẫn chứng, độ bao phủ và chi phí. Với viết mã, cần test hoặc đặc tả; với tổng hợp tài liệu, cần kiểm tra mâu thuẫn nguồn. LLM làm giám khảo có thể hỗ trợ nhưng bản thân giám khảo cũng cần đánh giá sai số.

### Miền xã hội và văn hóa

Section 5.3 khảo sát mô phỏng cộng đồng, tương tác xã hội, nhân vật và hoạt động mang tính văn hóa. Các môi trường này thích hợp để nghiên cứu hành vi emergent vì nhiều thành viên có ký ức và quan hệ khác nhau. Tuy nhiên, một hành vi trông giống con người trong mô phỏng không đủ chứng minh mô hình phản ánh dân số thực.

Phản biện của người viết: kết quả mô phỏng chịu ảnh hưởng của prompt, dữ liệu tiền huấn luyện, giả định tác giả và cách thiết kế phần thưởng. Nếu dùng mô phỏng để hỗ trợ quyết định xã hội, cần đối chiếu với dữ liệu và chuyên gia bên ngoài. Gán quá nhiều thuộc tính tâm lý cho agent có thể khiến người đọc hiểu sai phạm vi của bằng chứng.

## Vấn đề mở và đánh giá phê bình

### Quản trị và quyết định tập thể

Section 6.1 đặt ra thống nhất quản trị, phân vai, phục hồi lỗi và ra quyết định chung. Một hệ đáng tin phải biết ai có quyền sửa mục tiêu, ai được gọi công cụ ghi và ai xác nhận hoàn tất. Khi manager và worker bất đồng, không thể chỉ thêm một vòng chat vô hạn; phải có cơ chế giải quyết hoặc trả quyền quyết định về người dùng.

Đề xuất của báo cáo là dùng ngân sách rõ cho vòng sửa: số lần thử, thời gian và chi phí tối đa; lưu lý do thay đổi; phân biệt “không tìm thấy lời giải” với “lỗi dịch vụ”. Bộ điều phối cần có các trạng thái kết thúc thành công, kết quả một phần, thiếu bằng chứng, hết hạn và vi phạm hợp đồng. Cách mô hình hóa này biến một cuộc hội thoại thành quy trình có thể vận hành.

### Benchmark và nguyên nhân cải thiện

Section 6.2 nhấn mạnh thiếu chuẩn đánh giá thống nhất. Một hệ nhiều agent có thể dùng nhiều token hơn baseline một agent, nên chênh lệch điểm chưa tách được tác dụng của phối hợp khỏi tác dụng của thêm tính toán. Baseline nên có phiên bản ngân sách tương đương, ví dụ một agent được dùng cùng số lượt công cụ hoặc cùng tổng token.

Ablation phải bỏ đúng thành phần đang muốn đo. Bỏ coordinator validation trong tutorial kiểm tra giá trị của validation; nó không chứng minh việc chia nhiều agent tạo ra cải thiện. So sánh B0 và B1 trên cùng bộ ca mới cho biết overhead của chia vai. So sánh B1 và B2 mới giúp xem classifier bổ sung có thay đổi khả năng định tuyến hay không.

### An toàn, tấn công và độ tin cậy

Section 6.3 lưu ý lỗi và thông tin sai có thể lan qua các kênh. Một message từ agent nội bộ vẫn có thể chứa dữ liệu không đáng tin vì agent đó đọc nguồn ngoài. Cần tách dữ liệu khỏi chỉ dẫn, xác thực schema và giới hạn quyền công cụ. Trong tutorial, một ID lạ hoặc sản phẩm vượt ngân sách bị PolicyAgent bác bỏ trước khi có kết luận sẵn hàng.

Không nên suy diễn rằng thêm nhiều agent luôn tăng an toàn. Mỗi agent thêm một bề mặt lỗi và một chuỗi phụ thuộc. Một thiết kế phòng vệ có ích khi bước kiểm chứng có thẩm quyền và thực sự chặn hành động sai. Bản ablation B3 minh họa hệ có nhiều thành viên nhưng vẫn đưa ra thông tin sai khi bỏ kiểm tra nguồn gốc và tuổi dữ liệu.

## Thiết kế nghiên cứu tiếp nối do báo cáo đề xuất

Câu hỏi nghiên cứu: khi catalog nhỏ và các ràng buộc xác định, chia vai có cải thiện tỷ lệ hoàn thành so với pipeline đơn không? Câu hỏi phụ: verification đóng góp bao nhiêu, classifier intent đóng góp bao nhiêu và độ trễ tăng bao nhiêu? Đây là các câu hỏi đủ hẹp để có đối chứng bằng mã cục bộ, thay vì khẳng định chung về mọi MAS.

Thiết kế gồm bốn kiến trúc B0–B3, cùng catalog và tập yêu cầu. Dữ liệu lỗi được tạo có chủ đích: timeout, sai envelope, dữ liệu kho cũ và output giả từ thành phần. Ground truth là trạng thái và danh sách ID hợp lệ; thành công được tính cả các ca từ chối đúng. Điều này khác với chỉ đếm số lần hệ trả được danh sách sản phẩm.

Để mở rộng thành nghiên cứu LLM, giữ nguyên hợp đồng công cụ và bộ kiểm chứng rồi thay bộ đề xuất bằng LLM. Cần công bố model version, decoding, prompt, ngân sách, số vòng, dữ liệu và trace. Chạy nhiều seed hoặc nhiều lần lấy mẫu; phân tích theo loại lỗi; báo cáo cả phân phối chi phí. Bộ mã hiện tại là nền tảng kiểm thử kiến trúc, chưa phải thí nghiệm này.

## Kết luận riêng cho Paper 1

Giá trị lớn nhất của paper là đổi trọng tâm từ số lượng agent sang cấu trúc quan hệ giữa chúng. Năm chiều actors, types, strategies, structures và coordination cho phép mô tả khá nhiều hệ trong một khung chung. Khi chuyển sang phần mềm, khung đó cần được cụ thể hóa bằng schema, quyền, nguồn dữ liệu, deadline và phép kiểm chứng.

Giới hạn cần giữ rõ là phạm vi survey rộng, các kết quả được tổng thuật đến từ những bài có cấu hình và benchmark khác nhau, và nhiều kỳ vọng về trí tuệ tập thể còn là hướng nghiên cứu. Báo cáo vì thế sử dụng paper để tổ chức câu hỏi thiết kế, rồi dùng các thực nghiệm cục bộ để kiểm tra những nhận định hẹp mà bộ mã thực sự đo được.
