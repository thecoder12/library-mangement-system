"""Domain entities - pure Python business objects (no ORM dependencies)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Generic, TypeVar


T = TypeVar("T")


@dataclass
class BookEntity:
    """Book domain entity."""
    
    title: str
    author: str
    id: Optional[int] = None
    isbn: Optional[str] = None
    published_year: Optional[int] = None
    genre: Optional[str] = None
    total_copies: int = 1
    available_copies: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def is_available(self) -> bool:
        """Check if book has copies available for borrowing."""
        return self.available_copies > 0
    
    @property
    def borrowed_copies(self) -> int:
        """Get number of currently borrowed copies."""
        return self.total_copies - self.available_copies


@dataclass
class MemberEntity:
    """Member domain entity."""
    
    name: str
    email: str
    id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    membership_date: Optional[date] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def can_borrow(self) -> bool:
        """Check if member is eligible to borrow books."""
        return self.is_active


@dataclass
class BorrowRecordEntity:
    """Borrow record domain entity."""
    
    book_id: int
    member_id: int
    borrow_date: date
    due_date: date
    id: Optional[int] = None
    return_date: Optional[date] = None
    status: str = "BORROWED"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Optional related entities (for when we need to include them)
    book: Optional[BookEntity] = None
    member: Optional[MemberEntity] = None
    
    @property
    def is_returned(self) -> bool:
        """Check if the book has been returned."""
        return self.status == "RETURNED"
    
    @property
    def is_overdue(self) -> bool:
        """Check if the borrow is overdue."""
        if self.is_returned:
            return False
        return date.today() > self.due_date
    
    @property
    def days_until_due(self) -> int:
        """Get days until due date (negative if overdue)."""
        return (self.due_date - date.today()).days


@dataclass
class PaginatedResult(Generic[T]):
    """Generic paginated result container."""
    
    items: List[T]
    total_count: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total_count + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
