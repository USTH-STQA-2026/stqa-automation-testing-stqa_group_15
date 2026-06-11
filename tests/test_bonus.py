"""
Bonus Test Cases — Library Book Borrowing System
Các test case bổ sung ngoài 12 TC bắt buộc.
"""
import os
import pytest
from conftest import (
    enable_flutter_semantics, flutter_fill, flutter_click_button,
    wait_for_flutter, login, SCREENSHOT_DIR,
)

CU_LE_EMAIL = "cu.le@email.com"
CU_LE_PASSWORD = "password123"
BINH_PHAM_EMAIL = "binh.pham@email.com"
BINH_PHAM_PASSWORD = "password123"


@pytest.mark.parametrize("email,password,expected_error,screenshot_name", [
    ("nobody@test.com", "anything", "Không tìm thấy thành viên", "bonus_login_unknown_email.png"),
    ("ba.nguyen@email.com", "wrongpassword", "Mật khẩu không đúng", "bonus_login_wrong_password_param.png"),
    ("", "", "Vui lòng nhập email và mật khẩu", "bonus_login_empty_param.png"),
])
def test_bonus_login_invalid_inputs(page, test_config, email, password, expected_error, screenshot_name):
    """Bonus B2 — Data-driven: các trường hợp login thất bại."""
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)

    if email:
        flutter_fill(page, "Email", email)
    if password:
        flutter_fill(page, "Mật khẩu", password)
    flutter_click_button(page, "Đăng nhập")

    wait_for_flutter(page, text=expected_error)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, screenshot_name))

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert expected_error in sem_text, f"Expected '{expected_error}' in: {sem_text[:200]}"
    assert "Đăng nhập" in sem_text, "Should still be on login page"


def test_bonus_search_case_insensitive(page, test_config):
    """Bonus B1 — REQ-03: Tìm kiếm không phân biệt hoa/thường."""
    login(page, test_config)

    # Nhập chữ thường "flutter" → phải tìm thấy "Lập trình Flutter cơ bản"
    flutter_fill(page, "Tìm kiếm theo tên sách hoặc tác giả...", "flutter")
    # Book title nằm trong aria-label, dùng locator selector
    page.locator('flt-semantics[role="group"][aria-label*="Flutter"]').first.wait_for(
        state="attached", timeout=10000
    )
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bonus_search_case_insensitive.png"))

    results = page.locator('flt-semantics[role="group"][aria-label*="Flutter"]')
    assert results.count() > 0, "Case-insensitive search failed: 'flutter' should find Flutter books"
    label = results.first.get_attribute("aria-label") or ""
    assert "Lập trình Flutter cơ bản" in label, f"Expected Flutter book but got: {label}"


def test_bonus_suspended_member_cannot_borrow(page, test_config):
    """Bonus B1 — REQ-04: Thành viên tạm ngưng bị từ chối mượn sách."""
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email", CU_LE_EMAIL)
    flutter_fill(page, "Mật khẩu", CU_LE_PASSWORD)
    flutter_click_button(page, "Đăng nhập")
    wait_for_flutter(page, text="Đăng xuất")
    enable_flutter_semantics(page)

    page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first.click()
    wait_for_flutter(page, text="Xác nhận mượn sách")
    enable_flutter_semantics(page)
    flutter_click_button(page, "Mượn")
    wait_for_flutter(page, text="tạm ngưng")
    enable_flutter_semantics(page)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bonus_suspended_member_cannot_borrow.png"))

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "tạm ngưng" in sem_text.lower() or "không thể mượn" in sem_text.lower() or \
        "suspended" in sem_text.lower(), \
        f"Expected suspended error but got: {sem_text[:300]}"


def test_bonus_expired_member_cannot_borrow(page, test_config):
    """Bonus B1 — REQ-04: Thành viên hết hạn bị từ chối mượn sách với thông báo đúng lý do."""
    page.goto(test_config["base_url"], wait_until="networkidle", timeout=60000)
    enable_flutter_semantics(page)
    flutter_fill(page, "Email", BINH_PHAM_EMAIL)
    flutter_fill(page, "Mật khẩu", BINH_PHAM_PASSWORD)
    flutter_click_button(page, "Đăng nhập")
    wait_for_flutter(page, text="Đăng xuất")
    enable_flutter_semantics(page)

    page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")').first.click()
    wait_for_flutter(page, text="Xác nhận mượn sách")
    enable_flutter_semantics(page)
    flutter_click_button(page, "Mượn")
    wait_for_flutter(page, text="hết hạn")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bonus_expired_member_cannot_borrow.png"))

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "hết hạn" in sem_text.lower(), \
        f"Expected expired error but got: {sem_text[:200]}"
    # REQ-04: thông báo lỗi phải đúng lý do — hết hạn ≠ tạm ngưng
    assert "tạm ngưng" not in sem_text.lower(), \
        "Error message should say 'hết hạn', not 'tạm ngưng'"


def test_bonus_view_book_list_after_login(page, test_config):
    """Bonus B3 — REQ-02: Sau khi login, danh sách sách hiển thị đầy đủ thông tin."""
    login(page, test_config)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bonus_view_book_list.png"))

    # Book info nằm trong aria-label của group, dùng locator selector
    book_cards = page.locator('flt-semantics[role="group"][aria-label*="Mã: BOOK"]')
    assert book_cards.count() > 0, "Không có sách nào trong danh sách"

    first_label = book_cards.first.get_attribute("aria-label") or ""
    assert "Mã: BOOK" in first_label, f"Book card thiếu mã sách: {first_label}"
    assert "Có sẵn" in first_label or "Đang mượn" in first_label, \
        f"Book card thiếu trạng thái: {first_label}"

    # Kiểm tra có sách Flutter
    flutter_book = page.locator('flt-semantics[role="group"][aria-label*="Lập trình Flutter"]')
    assert flutter_book.count() > 0, "Không thấy sách 'Lập trình Flutter cơ bản'"
    label = flutter_book.first.get_attribute("aria-label") or ""
    assert "Nguyễn Minh Đức" in label, f"Thiếu tên tác giả: {label}"
    assert "Công nghệ" in label, f"Thiếu thể loại: {label}"


def test_bonus_borrow_already_borrowed_book(page, test_config):
    """Bonus B1 — REQ-04: Không thể mượn sách đã bị người khác mượn."""
    login(page, test_config)

    # BOOK003 đang được MEM002 mượn → không có nút "Mượn sách này"
    # BOOK003 hiển thị trên trang chủ — không cần search
    # Chờ trang home load xong
    wait_for_flutter(page, text="Đăng xuất")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "bonus_borrow_already_borrowed.png"))

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    # BOOK003 đang mượn phải hiển thị trên trang
    assert "Đang mượn" in sem_text, "BOOK003 phải hiển thị trạng thái Đang mượn"

    # Số nút "Mượn sách này" phải bằng số sách Có sẵn (không bao gồm sách đang mượn)
    borrow_btns = page.locator('flt-semantics[role="button"]:has-text("Mượn sách này")')
    available_cards = page.locator('flt-semantics[role="group"][aria-label*="Có sẵn"]')
    assert borrow_btns.count() == available_cards.count(), \
        f"Số nút mượn ({borrow_btns.count()}) phải bằng số sách Có sẵn ({available_cards.count()})"
