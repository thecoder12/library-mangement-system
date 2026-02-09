"""API endpoint path constants."""

# API version prefix
API_PREFIX = "/api"


class BookEndpoints:
    """Book-related endpoint paths."""
    BASE = f"{API_PREFIX}/books"
    BY_ID = "/{book_id}"


class MemberEndpoints:
    """Member-related endpoint paths."""
    BASE = f"{API_PREFIX}/members"
    BY_ID = "/{member_id}"
    BORROWED = "/{member_id}/borrowed"


class BorrowEndpoints:
    """Borrow-related endpoint paths."""
    BASE = f"{API_PREFIX}/borrows"
    BY_ID = "/{borrow_id}"
    RETURN = "/{borrow_id}/return"
