# Doc Progress Tracking Rule

## Activation
- Model Decision (kích hoạt khi bắt đầu session làm việc với BRD/PRD/FRD, hoặc sau khi tạo/cập nhật bất kỳ file tài liệu nào)

## Rules

- **Khi bắt đầu session mới**: Đọc `PROGRESS.md` ngay lập tức trước khi thực hiện bất kỳ thao tác nào.

- **Sau mỗi thay đổi**: Tạo hoặc cập nhật bất kỳ file BRD/PRD/FRD nào → cập nhật `PROGRESS.md` ngay trong cùng lượt làm việc đó.

- **Trạng thái hợp lệ**: `Not Started` · `In Progress` · `Pending Questions` · `Done` · `Deferred – Phase 2`

- **Đánh dấu deferred** — dùng blockquote, KHÔNG xóa hạng mục:
  ```
  > ⏸ DEFERRED – Phase 2
  > Lý do: [ghi rõ]
  > Tham chiếu: BRD section X.Y
  ```

- **File naming conventions**:

  | Loại | Thư mục | Pattern |
  |------|---------|---------|
  | BRD | `brds/` | `BRD-NEW-MAN-xx-[tên].md` |
  | PRD | `prds/` | `PRD-NEW-MAN-xx-[tên]-01.md` |
  | FRD | `frds/` | `FRD-NEW-MAN-xx-[tên]-01.md` |
