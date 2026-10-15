# Nương dòng bình yên — giai đoạn 01

Đây là **một tác phẩm dự kiến**, được nghiên cứu qua nhiều góc nhìn. File hiện tại là thư viện chi tiết rời, chưa ghép thành tác phẩm hoàn chỉnh. Vị trí các món trên bàn trưng bày không phải vị trí cuối cùng và bàn này lớn hơn 20 cm. Giới hạn **20 × 20 cm** áp dụng cho tác phẩm sau khi ghép, không áp dụng cho bàn thư viện.

## Ý tưởng

Ba chú ngựa trắng đứng nghỉ, gặm cỏ, uống nước bên một dòng suối liên tục. Núi tạo sự che chở, tán cây tạo nhịp nghỉ, mặt trời ấm và mây mềm tạo cảm giác thiên nhiên yên bình. Ba tầng là nhịp địa hình, không mang ý nghĩa hơn–thua. Mặt trăng/ngọc tròn trong ảnh được giữ như một chi tiết tùy chọn; có thể bỏ ở bước bố cục để bớt rối và tránh cảm giác hai nguồn sáng cạnh tranh.

## Mở file

- `Nuong_dong_binh_yen_components_v01.blend`: 20 bộ phận đặt tách nhau; các collection A01–A20 tương ứng mã trong bảng đo.
- `assets/`: mỗi thành phần là một thư viện `.blend` riêng, có gốc ở tâm đáy. Dùng File → Append → Collection trong file chính, hoặc trong một scene đã đặt Unit Scale = 0.01, để lấy vào cảnh khác. Các thư viện collection không mang theo cấu hình đơn vị của scene. Không dùng tọa độ bàn trưng bày làm tọa độ lắp.
- `renders/`: ảnh chụp từ Blender, gồm tổng quan và ảnh từng thành phần. Đây là render của mesh đã dựng, không phải hình ảnh AI thay cho mô hình.
- `measurements/components.csv` và `.json`: kích thước đo bằng cm từ hình học thực tế sau khi áp dụng modifier/curve. Quy ước: X trái–phải, Y trước–sau, Z cao; trước là Y âm.
- `measurements/validation.json`: kết quả đọc lại file để kiểm tra; phân biệt rõ nội dung đã kiểm và chưa kiểm.
- `Phieu_thiet_ke_giai_doan_01.pdf`: bản thuyết minh, bảng kích thước, khuôn mặt bằng 1:1 và sơ đồ cao độ. In ở **Actual size / 100%**, kiểm tra thước 50 mm trước khi dùng.

Trong Blender, **1 đơn vị tọa độ = 1 cm**, Unit Scale = 0.01. X/Y/Z trong báo cáo đều là kích thước thật dự kiến. Chưa xuất STL ở giai đoạn này vì nhiều mô-đun là cụm mesh chồng nhau dành cho nghiên cứu nặn tay, chưa xử lý thành khối kín duy nhất.

## Cơ sở của số đo

Chỉ có kích thước đế 20 × 20 cm là yêu cầu xác định từ người dùng. Ảnh tham khảo do AI tạo không chứa dữ liệu camera hoặc phép đo đáng tin cậy; các góc cũng thay đổi hình học. Không thể truy ngược một bộ kích thước thật chính xác từ ảnh đó. Những con số ở đây là **bộ kích thước thiết kế mới**, thống nhất và đo kiểm được, không phải kết quả đo một vật thể có sẵn.

Giữ ngựa ở quy mô gần nhau, không thu nhỏ ngựa trên đỉnh để tạo phối cảnh giả. Đây là tiểu cảnh cách điệu: ngựa, cây và núi không dùng cùng tỉ lệ với địa hình ngoài đời. Tỉ lệ ngựa được dựng từ các khối giải phẫu thân, vai, hông, cổ, đầu, chân; không phải mẫu quét giải phẫu dùng cho nghiên cứu động vật.

## Kích thước chủ đạo (cm)

| Bộ phận | X × Y × Z | Ghi chú |
|---|---|---|
| Đế | 20 × 20 × 1,2 | Kích thước ngoài hoàn thiện |
| Núi tầng 1 | 19 × 18,8 × 4 | Bờ trước thấp; đỉnh tầng ở khoảng Z = 5,2 |
| Núi tầng 2 | 14,2 × 12,8 × 6 | Mặt tầng dự kiến Z = 11,2 |
| Núi tầng 3 | 9,2 × 8,5 × 6 | Mặt tầng dự kiến Z = 17,2 |
| Cụm đỉnh phía sau | 4,2 × 3,6 × 8,3 | Cao nhất ở Z = 25,5 |
| Ngựa đứng | 6,7 × 2,15 × 6,3 | Dáng thư thái, bốn chân làm điểm tựa |
| Ngựa gặm cỏ | 7,1 × 2,2 × 4,8 | Cổ hạ thấp |
| Ngựa uống nước | 7,1 × 2,2 × 4,65 | Bậc bờ trước thấp; miệng/nước chưa ghép kiểm |
| Tùng | 3,6 × 3,4 × 7,2 | Một mẫu để nhân bản khi cần |
| Cây tán rộng | 6,2 × 4,6 × 5,8 | Tán chia mảng để dễ nặn |
| Mặt trời | 6,2 × 0,45 × 6,2 | Mép cao nhất dự kiến Z = 27,9 |
| Ngọc/mặt trăng tùy chọn | 2,6 × 2,6 × 2,6 | Cần chốt có giữ hay không khi ghép |
| Cụm mây | 6 × 1,4 × 1,8 | Không được treo lơ lửng khi nặn |
| Cỏ | 2,2 × 1,8 × 1,1 | Cụm lá dày, không làm từng sợi mảnh |
| Cành lá | 2,8 × 1,8 × 0,6 | Cụm mẫu; có thể khắc gân trên mảng lớn |
| Mặt suối thấp | 5,6 × 7,6 × 0,32 | Màu men/xanh đục; chưa giả định dùng resin |
| Thác thấp | 2,2 × 2,6 × 4 | Một mô-đun riêng |
| Thác giữa / trên | mỗi đoạn 2,2 × 2,6 × 6 | Điểm nối sẽ sửa khi ghép |
| Hoa và rêu | 2,2 × 1,8 × 0,6 | Chi tiết phụ, có thể đơn giản hóa |

Chiều cao 27,9 cm là mốc v01, không phải ràng buộc người dùng. Chiều ngang và chiều sâu của **toàn bộ** tác phẩm, kể cả tán cây, đuôi ngựa, mặt trời và mây, phải nằm trong khung 20 × 20 cm. Vị trí dự kiến trong JSON hiện đáp ứng giới hạn hộp bao; chưa chứng minh tất cả các bộ phận không xuyên nhau.

## Các quyết định còn mở trước khi làm bằng đất

1. Xác định loại đất, có nung hay không, yêu cầu môn học và thời gian còn lại. Chưa biết vật liệu thì chưa chọn lõi xốp, giấy, dây kim loại, keo hoặc độ dày vỏ cố định.
2. Nếu vật liệu co ngót: lấy thông số nhà sản xuất và thử một thanh mẫu có vạch đo 100 mm theo đúng quy trình. Gọi s là độ co dài đo được, kích thước ướt tham khảo = kích thước hoàn thiện / (1 − s). Ví dụ minh họa s = 0,08 thì 20 cm cần khoảng 21,74 cm khi ướt; **8% không phải thông số đã xác định cho đất của bạn**. Độ co có thể khác theo phương và quy trình.
3. Chốt yêu cầu 20 × 20 cm là kích thước sau khô/nung hay kích thước lúc nộp trên một đế cứng. Mặc định thiết kế hiện tại hiểu là kích thước hoàn thiện, gồm cả lớp sơn phủ.
4. Lõi núi phải nhẹ và tương thích vật liệu; không khuyến nghị nặn đặc toàn bộ khối cao 28 cm. Vật liệu không nung có thể dùng lõi phù hợp; đất gốm cần phương án rỗng/thoát khí và tư vấn quy trình từ giảng viên/xưởng.
5. Chân ngựa, tai, ngọn cây và nhánh chìa là vùng dễ gãy. Chỉ có số đo hộp bao chưa đủ đánh giá độ bền. Ở bước kế tiếp phải đo tiết diện nhỏ nhất, điều chỉnh dáng và quyết định có lõi đỡ tương thích hay không.
6. Mặt trời, ngọc và mây cần bệ/chốt nối thật giấu sau núi hoặc cây; không sao chép phần “lơ lửng” của ảnh AI.

## Bước tiếp theo — chưa thực hiện

Sau khi xem lại riêng từng bộ phận, tinh chỉnh đặc biệt ba ngựa và độ thô của đá. Sau đó mới tạo **một** cảnh lắp, khoét đường nước, đặt đủ điểm tiếp xúc móng, chỉnh miệng ngựa chạm mặt suối, bố trí điểm đỡ và kiểm tra từ bốn góc của cùng một mesh. Cuối cùng mới khóa ánh sáng, màu, kích thước thi công và thứ tự nặn.

Không gọi bộ mẫu này là bản sản xuất cuối cùng. Không cộng bề dày và chiều cao từng món để suy ra chiều cao cuối: nhiều món nằm ở các cao độ khác nhau.

## Tái tạo

Yêu cầu: Blender 4.3.x; Python có Pillow và ReportLab để tạo tài liệu PDF/contact sheet. Các công cụ này đã có trong environment hiện tại. Render dùng CPU, không cần tài khoản dịch vụ tạo model bên ngoài.

Từ `/workspace/3D_Test`:

```sh
blender -b -t 4 --python-exit-code 1 --python design/stage_01/scripts/build_components.py
blender -b -t 4 --python-exit-code 1 --python design/stage_01/scripts/validate_components.py
python3 design/stage_01/scripts/prepare_documents.py
```

Nếu chỉ cần render lại file đã lưu:

```sh
blender -b -t 4 --python-exit-code 1 --python design/stage_01/scripts/render_components.py
```

Các script của giai đoạn 01 không thay đổi cấu hình môi trường hay cài dependency của ứng dụng.
