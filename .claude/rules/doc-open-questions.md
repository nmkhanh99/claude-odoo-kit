# Doc Open Questions Rule

## Activation
- Model Decision (kích hoạt khi bắt đầu viết BRD/PRD/FRD hoặc khi gặp thông tin chưa đủ để viết)

## Rules

Áp dụng quy trình 4 bước bắt buộc khi có thông tin chưa rõ:

- **Bước 1 — Hỏi trước khi viết**: Liệt kê toàn bộ câu hỏi chưa rõ. Hỏi user và **chờ trả lời** trước khi bắt đầu viết. KHÔNG tự ghi câu hỏi vào tài liệu thay vì hỏi trực tiếp.

- **Bước 2 — Phân tích câu trả lời**: Kiểm tra có phát sinh thêm câu hỏi không (edge case, mâu thuẫn). Nếu có → hỏi tiếp. Lặp đến khi không còn câu hỏi tồn đọng.

- **Bước 3 — Xử lý sau khi hỏi**: Câu đã trả lời → áp dụng vào nội dung, KHÔNG đưa vào bảng Open Questions. Chỉ ghi vào bảng Open Questions khi user xác nhận rõ ràng: "Chưa biết" / "Cần hỏi lại KH" / "Chờ bộ phận X xác nhận". KHÔNG tự quyết định ghi OQ khi chưa có xác nhận.

- **Bước 4 — Phân loại impact** (chỉ khi được phép ghi):
  ```
  | # | Câu hỏi | Trạng thái | Blocking? | Trả lời |
  | 1 | [Cụ thể] | Chờ KH | Blocking F3 / Không blocking | |
  ```
  - Blocking: không thể code/config nếu chưa trả lời — ghi rõ feature bị block.
  - Non-blocking: có workaround tạm — ghi rõ workaround.
  - KHÔNG tự điền cột "Trả lời" nếu chưa có xác nhận từ user.
