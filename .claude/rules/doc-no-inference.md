# Doc No Inference Rule

## Activation
- Model Decision (kích hoạt khi làm việc với tài liệu BRD/PRD/FRD trong `docs/`, `brds/`, `prds/`, `frds/`, `sources/`)

## Rules

- **KHÔNG** tự điền thông tin vào tài liệu nếu thông tin đó không có trong file nguồn hoặc chưa được user xác nhận trực tiếp trong conversation hiện tại.

- Những thứ **luôn phải hỏi** trước khi viết: tên menu/đường dẫn, timeout phê duyệt, tên người duyệt theo cấp, ngưỡng số lượng gây thay đổi quy trình, quy tắc đặt mã lô/phiếu, hành vi khi edge case chưa có trong nguồn.

- **Khi không chắc**, dùng công thức:
  ```
  Tôi không tìm thấy thông tin này trong file nguồn.
  Bạn muốn [phương án A] hay [phương án B]?
  ```

- **Thứ tự ưu tiên nguồn** khi có mâu thuẫn:
  1. Xác nhận trực tiếp từ user trong conversation hiện tại
  2. BRD đã duyệt trong `brds/`
  3. File nguồn chi tiết trong `sources/`
  4. File summary (`summary-brd.md`, `summary.md`)
  - Nếu có mâu thuẫn → báo cáo và hỏi trước khi viết.

- **KHÔNG** xử lý hai phân hệ hoặc hai loại tài liệu cùng lúc trong một session.
