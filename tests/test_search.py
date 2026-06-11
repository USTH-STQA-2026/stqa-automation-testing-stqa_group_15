"""
Search & Filter Tests (*Kiểm thử Tìm kiếm & Lọc sách*) — Library Book Borrowing System (*Hệ thống Mượn sách thư viện*)

Students must complete ALL 4 test cases in this file.
(*Sinh viên cần hoàn thành TẤT CẢ 4 test case trong file này.*)

Hints (*Gợi ý*):
    - After logging in, use flutter_fill() to type into the search box
      (*Sau khi đăng nhập, dùng flutter_fill() để nhập vào ô tìm kiếm*)
    - Search box aria-label: "Tìm kiếm theo tên sách hoặc tác giả..."
    - Category filter aria-label: "Lọc theo thể loại (VD: Công nghệ, Kinh tế...)"
    - Each book card has role="group" and aria-label containing book info
      (*Mỗi card sách có role="group" và aria-label chứa thông tin sách*)
    - Use login() helper from conftest.py to log in before testing
      (*Dùng login() helper từ conftest.py để đăng nhập trước khi test*)
"""
import os
import pytest
from conftest import (
    enable_flutter_semantics, flutter_fill, flutter_click_button,
    wait_for_flutter, login, SCREENSHOT_DIR,
)


def test_search_book_by_name(page, test_config):
    """TC-04: Search book by name – results found (*Tìm kiếm sách theo tên — tìm thấy kết quả*)"""
    login(page, test_config)

    flutter_fill(page, "Tìm kiếm theo tên sách hoặc tác giả...", "Flutter")
    wait_for_flutter(page, text="Lập trình Flutter cơ bản")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "search_book_by_name.png"))

    results = page.locator('flt-semantics[role="group"][aria-label*="Mã: BOOK"]')
    assert results.count() > 0, "Không tìm thấy kết quả nào"
    labels = [results.nth(i).get_attribute("aria-label") or "" for i in range(results.count())]
    assert any("Flutter" in label for label in labels), f"Không có sách nào chứa 'Flutter': {labels}"


def test_search_book_no_result(page, test_config):
    """TC-05: Search book – no results (*Tìm kiếm sách — không có kết quả*)"""
    login(page, test_config)

    flutter_fill(page, "Tìm kiếm theo tên sách hoặc tác giả...", "xyz_khong_ton_tai_12345")
    wait_for_flutter(page, text="Không tìm thấy sách")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "search_book_no_result.png"))

    sem_text = " ".join(page.locator("flt-semantics").all_text_contents())
    assert "Không tìm thấy sách" in sem_text, f"Expected 'Không tìm thấy sách' in: {sem_text[:200]}"
    book_cards = page.locator('flt-semantics[role="group"][aria-label*="Mã: BOOK"]')
    assert book_cards.count() == 0, f"Expected 0 books but found {book_cards.count()}"


def test_filter_by_category(page, test_config):
    """TC-06: Filter books by category 'Công nghệ' (*Lọc sách theo thể loại 'Công nghệ'*)"""
    login(page, test_config)

    flutter_fill(page, "Lọc theo thể loại (VD: Công nghệ, Kinh tế...)", "Công nghệ")
    page.locator('flt-semantics[role="group"][aria-label*="Công nghệ"]').first.wait_for(
        state="attached", timeout=10000
    )
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "filter_by_category.png"))

    results = page.locator('flt-semantics[role="group"][aria-label*="Mã: BOOK"]')
    assert results.count() > 0, "Không có sách nào sau khi lọc"
    for i in range(results.count()):
        label = results.nth(i).get_attribute("aria-label") or ""
        assert "Công nghệ" in label, f"Sách không thuộc thể loại Công nghệ: {label}"


def test_search_by_author(page, test_config):
    """TC-07: Search book by author name (*Tìm kiếm sách theo tên tác giả*)"""
    login(page, test_config)

    flutter_fill(page, "Tìm kiếm theo tên sách hoặc tác giả...", "Nguyễn Minh Đức")
    wait_for_flutter(page, text="Nguyễn Minh Đức")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "search_by_author.png"))

    results = page.locator('flt-semantics[role="group"][aria-label*="Mã: BOOK"]')
    assert results.count() > 0, "Không tìm thấy sách của tác giả"
    labels = [results.nth(i).get_attribute("aria-label") or "" for i in range(results.count())]
    assert all("Nguyễn Minh Đức" in label for label in labels), \
        f"Có sách không phải của Nguyễn Minh Đức: {labels}"
