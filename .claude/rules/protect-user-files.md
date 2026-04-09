# Protect User Files Rule

## Activation
- Always On

## Rules

**KHÔNG được tự ý xóa file**, trừ một ngoại lệ duy nhất:

> **Ngoại lệ được phép xóa**: File do chính AI tạo ra trong **cùng một chat** (không phải session), phục vụ mục đích xử lý trung gian (temp output, intermediate script, file tạm để phân tích).

**Phân biệt "chat" và "session":**
- **Chat** = một lượt hỏi–đáp liên tục, từ tin nhắn của user đến khi AI trả lời xong. Không bao gồm các lượt trước đó trong cùng session.
- **Session** = toàn bộ cuộc hội thoại từ đầu đến cuối (nhiều chat).

**Ví dụ được phép xóa:**
- AI tạo `tmp_extract_2024.py` để chạy một lần, rồi tự xóa sau khi lấy output.
- AI tạo `docs/temp_analysis.json` để build Excel, rồi xóa sau khi xuất xong.

**Ví dụ KHÔNG được phép xóa:**
- File do user tạo hoặc commit vào repo (dù AI nghĩ là "không cần thiết").
- File do AI tạo ở chat trước trong cùng session.
- File memory, config, rules, skills, BRD, PRD, FRD bất kể nguồn gốc.
- Thư mục nguyên vẹn (kể cả rỗng) nếu không phải AI vừa tạo.

**Khi user yêu cầu xóa file:**
- Xác nhận lại: "File `[tên]` — bạn xác nhận muốn xóa không?" trước khi thực hiện.
- Nếu file có vẻ quan trọng (BRD, config, memory) → nêu rõ hậu quả trước khi hỏi.
