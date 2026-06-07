"""
Borrow & Return Tests (*Kiểm thử Mượn & Trả sách*) — Library Book Borrowing System (*Hệ thống Mượn sách thư viện*)

Students must complete ALL 3 test cases in this file.
(*Sinh viên cần hoàn thành TẤT CẢ 3 test case trong file này.*)

Hints (*Gợi ý*):
    - Use login() helper to log in (*Dùng login() helper để đăng nhập*)
    - "Mượn / Trả" tab: role="tab", aria-label="Mượn / Trả"
    - Available books have "Có sẵn" in aria-label, borrowed books have "Đang mượn"
      (*Sách "Có sẵn" có aria-label chứa "Có sẵn", sách "Đang mượn" chứa "Đang mượn"*)
    - Borrow button: 'flt-semantics[role="button"]:has-text("Mượn sách này")'
      (*Nút mượn*)
    - After clicking "Mượn sách này", a confirmation dialog appears — click "Mượn" again
      (*Sau khi click "Mượn sách này" sẽ hiện dialog xác nhận — cần click nút "Mượn" lần nữa*)
    - Return button: 'flt-semantics[role="button"]:has-text("Trả sách")'
      (*Nút trả*)
"""
import os
import re
import pytest
from conftest import (
    enable_flutter_semantics, flutter_fill, flutter_click_button,
    wait_for_flutter, login, SCREENSHOT_DIR,
)

DAM_TRAN_EMAIL = "dam.tran@email.com"
DAM_TRAN_PASSWORD = "password123"


def login_as_dam_tran(page, base_url):
    """Helper: đăng nhập bằng dam.tran — account chưa mượn sách nào."""
    page.goto(base_url, wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email", DAM_TRAN_EMAIL)
    flutter_fill(page, "Mật khẩu", DAM_TRAN_PASSWORD)
    flutter_click_button(page, "Đăng nhập")
    wait_for_flutter(page, text="Đăng xuất")
    enable_flutter_semantics(page)


def test_borrow_book(page, test_config):
    """TC-08: Borrow an available book (*Mượn sách có trạng thái 'Có sẵn'*)"""
    login_as_dam_tran(page, test_config["base_url"])

    # Tìm sách có sẵn đầu tiên — không hard-code book ID để test idempotent
    available_card = page.locator('flt-semantics[role="group"][aria-label*="Có sẵn"]').first
    available_card.wait_for(state="attached", timeout=10000)
    label_before = available_card.get_attribute("aria-label") or ""
    assert "Có sẵn" in label_before, f"Không tìm thấy sách nào ở trạng thái Có sẵn: {label_before}"

    # Click mượn và xác nhận dialog
    page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first.click()
    wait_for_flutter(page, text="Xác nhận mượn sách")
    enable_flutter_semantics(page)
    flutter_click_button(page, "Mượn")
    wait_for_flutter(page, text="Đang mượn")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "borrow_book.png"))

    # Verify the specific book (identified by code extracted from label_before) changed to "Đang mượn"
    m = re.search(r'Mã: (BOOK\d+)', label_before)
    book_code = m.group(1) if m else None
    if book_code:
        card = page.locator(f'flt-semantics[role="group"][aria-label*="{book_code}"]').first
        label_after = card.get_attribute("aria-label") or ""
        assert "Đang mượn" in label_after, \
            f"Book {book_code} should now be 'Đang mượn' but got: {label_after}"
    else:
        sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
        assert "Đang mượn" in sem_text or "thành công" in sem_text.lower(), \
            f"Expected borrow success but got: {sem_text[:200]}"


def test_view_borrowed_books(page, test_config):
    """TC-09: View borrowed books list (*Xem danh sách sách đang mượn — tab Mượn / Trả*)"""
    login(page, test_config)

    # Vào tab Mượn / Trả
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    wait_for_flutter(page, text="Trả sách")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "view_borrowed_books.png"))

    # Xác nhận có phiếu BR001 — Kiểm thử phần mềm nhập môn đang mượn
    # Book title nằm trong aria-label của group, dùng locator thay vì text_contents
    borrow_record = page.locator('flt-semantics[role="group"][aria-label*="Kiểm thử phần mềm nhập môn"]')
    assert borrow_record.count() > 0, "Không thấy phiếu mượn Kiểm thử phần mềm nhập môn"
    label = borrow_record.first.get_attribute("aria-label") or ""
    assert "Đang mượn" in label, f"Phiếu không ở trạng thái Đang mượn: {label}"
    assert page.locator('flt-semantics[role="button"]:has-text("Trả sách")').count() > 0, \
        "Không thấy nút Trả sách"


def test_return_book(page, test_config):
    """TC-10: Return a borrowed book (*Trả sách đang mượn*)"""
    login(page, test_config)

    # Vào tab Mượn / Trả
    page.locator('flt-semantics[role="tab"][aria-label="Mượn / Trả"]').click()
    wait_for_flutter(page, text="Trả sách")

    # Ghi lại tên sách trước khi trả để kiểm tra sau
    borrow_record = page.locator('flt-semantics[role="group"][aria-label*="Đang mượn"]').first
    record_label = borrow_record.get_attribute("aria-label") or ""
    m = re.search(r'Mã: (BOOK\d+)', record_label)
    return_book_code = m.group(1) if m else None

    # Click trả sách
    page.locator('flt-semantics[role="button"]:has-text("Trả sách")').first.click()
    wait_for_flutter(page, text="Đã trả")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "return_book.png"))

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "Đã trả" in sem_text, f"Expected 'Đã trả' but got: {sem_text[:200]}"

    # Kiểm tra sách trả về chuyển trạng thái Có sẵn trong danh sách sách
    if return_book_code:
        page.locator('flt-semantics[role="tab"]').first.click()
        wait_for_flutter(page, text="Có sẵn")
        enable_flutter_semantics(page)
        book_card = page.locator(f'flt-semantics[role="group"][aria-label*="{return_book_code}"]')
        if book_card.count() > 0:
            label_after = book_card.first.get_attribute("aria-label") or ""
            assert "Có sẵn" in label_after, \
                f"Returned book {return_book_code} should be 'Có sẵn': {label_after}"
