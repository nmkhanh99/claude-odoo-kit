# Mermaid Patterns – BRD Kho SPS

## Pattern 1: Luồng tuyến tính (Linear flow)
*Dùng cho: INV-01 (setup nhân sự), INV-09 (kiểm kê)*

```mermaid
flowchart TD
    Start([Bắt đầu]) --> Step1["Bước 1:<br/>Hành động A"]
    Step1 --> Step2["Bước 2:<br/>Hành động B"]
    Step2 --> Step3["Bước 3:<br/>Hành động C"]
    Step3 --> End([Hoàn tất])

    note1["Đối tượng: Actor A<br/>Module: Mod1"]
    note2["Đối tượng: Actor B<br/>Module: Mod2"]
    note3["Đối tượng: Actor C<br/>Module: Mod3"]

    note00 --- note1 --- note2 --- note3

    %% ===== STYLE =====
    style Start  fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style End    fill:#FFB6C1,stroke:#C2185B,stroke-width:2px
    style Step1  fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style Step2  fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style Step3  fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style note1  fill:#FFF9C4,stroke:#F57F17,stroke-width:1px
    style note2  fill:#FFF9C4,stroke:#F57F17,stroke-width:1px
    style note3  fill:#FFF9C4,stroke:#F57F17,stroke-width:1px
    style note00 fill:#fff,fill-opacity:0,stroke:#fff,stroke-opacity:0,color:transparent

    linkStyle 3,4,5 stroke:transparent,stroke-width:1px
```

## Pattern 2: Có QC pass/fail (Decision + 2 nhánh)
*Dùng cho: nhập kho có IQC, PQC*

```mermaid
flowchart TD
    Start([Bắt đầu]) --> Step1["Bước 1:<br/>Nhân viên QC kiểm tra"]
    Step1 --> QC{Kết quả?}
    QC -->|Pass| Validate["Bước 2:<br/>Kho xác nhận nhập"]
    QC -->|Fail| Return["Bước 3:<br/>Tạo phiếu trả NCC"]
    Validate --> End([Kết thúc])
    Return --> End

    %% ===== STYLE =====
    style Start    fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style End      fill:#FFB6C1,stroke:#C2185B,stroke-width:2px
    style Step1    fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style QC       fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style Validate fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style Return   fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
```

## Pattern 3: Multi-source (nhiều nguồn vào 1 luồng chung)
*Dùng cho: INV-03 nhập kho (5 nguồn), INV-04 xuất kho*

```mermaid
flowchart TD
    Start([Bắt đầu]) --> Source{Nguồn?}

    %% ── Nhánh 1 ──
    Source -->|"1. Nguồn A"| PathA["Bước 1.1:<br/>Xử lý A"]
    PathA --> Common["Bước 2:<br/>Xử lý chung"]

    %% ── Nhánh 2 ──
    Source -->|"2. Nguồn B"| PathB["Bước 1.2:<br/>Xử lý B"]
    PathB --> Common

    %% ── Nhánh 3 (ngoài ERP) ──
    Source -->|"3. Nguồn C\n(ngoài ERP)"| External["Theo dõi ngoài ERP<br/>Không tạo phiếu"]

    Common --> End([Kết thúc])
    External --> End

    %% ===== STYLE =====
    style Start    fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style End      fill:#FFB6C1,stroke:#C2185B,stroke-width:2px
    style Source   fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style PathA    fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style PathB    fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style Common   fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style External fill:#F5F5F5,stroke:#9E9E9E,stroke-width:1px,stroke-dasharray:4
```

## Pattern 4: Subprocess (tham chiếu luồng khác)
*Dùng khi một bước dẫn sang module khác*

```mermaid
flowchart TD
    Step1["Bước 1:<br/>Hành động A"] --> Sub[["Bước 2:<br/>→ Xem luồng INV-07"]]
    Sub --> End([Kết thúc])

    style Sub fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
```

## Pattern 5: Phê duyệt nhiều cấp (Approval workflow)
*Dùng cho: điều chỉnh tồn kho, xuất hủy*

```mermaid
flowchart TD
    Start([Bắt đầu]) --> Create["Bước 1:<br/>Nhân viên tạo đề nghị"]
    Create --> L1{Quản lý kho\nduyệt?}
    L1 -->|Duyệt| L2{Kế toán\nxác nhận?}
    L1 -->|Từ chối| Reject["Trả lại + ghi lý do"] --> End([Kết thúc])
    L2 -->|Duyệt| L3{BGĐ\nphê duyệt?}
    L2 -->|Từ chối| Reject
    L3 -->|Duyệt| Apply["Bước 4:<br/>Apply điều chỉnh"]
    L3 -->|Từ chối| Reject
    Apply --> End

    %% ===== STYLE =====
    style Start  fill:#90EE90,stroke:#2E7D32,stroke-width:2px
    style End    fill:#FFB6C1,stroke:#C2185B,stroke-width:2px
    style L1     fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style L2     fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style L3     fill:#FFE0B2,stroke:#E65100,stroke-width:2px
    style Create fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style Apply  fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
    style Reject fill:#BBDEFB,stroke:#1976D2,stroke-width:2px
```

## Lỗi thường gặp khi viết Mermaid

| Lỗi | Nguyên nhân | Fix |
|-----|------------|-----|
| Diagram không render | Ký tự `(`, `)`, `[`, `]` trong label mà không quote | Bọc label bằng `"..."` |
| `linkStyle` sai index | Đếm nhầm thứ tự arrow | Đếm từ 0, theo thứ tự khai báo `-->` |
| Node ID trùng | Dùng cùng ID cho 2 node | Đổi tên ID (không phải label) |
| Edge label xuống dòng không hiện | Dùng `\n` trong label không có quote | Bọc `"text\ntext"` |
| Annotation hiện mũi tên | Quên khai báo `linkStyle ... stroke:transparent` | Tính đúng index các link transparent |
| `stroke-dasharray` không nhận | Thiếu `stroke-width` trước | Luôn khai báo cả hai |
