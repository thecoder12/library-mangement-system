"""Pydantic schemas for REST API request/response validation."""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Book Schemas
# ============================================================================

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    published_year: Optional[int] = Field(None, alias="publishedYear")
    genre: Optional[str] = Field(None, max_length=100)
    total_copies: int = Field(1, ge=1, alias="totalCopies")

    class Config:
        populate_by_name = True


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    published_year: Optional[int] = Field(None, alias="publishedYear")
    genre: Optional[str] = Field(None, max_length=100)
    total_copies: Optional[int] = Field(None, ge=1, alias="totalCopies")

    class Config:
        populate_by_name = True


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str] = None
    published_year: Optional[int] = Field(None, alias="publishedYear")
    genre: Optional[str] = None
    total_copies: int = Field(alias="totalCopies")
    available_copies: int = Field(alias="availableCopies")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class BookListResponse(BaseModel):
    books: List[BookResponse]
    total_count: int = Field(alias="totalCount")
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# ============================================================================
# Member Schemas
# ============================================================================

class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="isActive")

    class Config:
        populate_by_name = True


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    membership_date: Optional[date] = Field(None, alias="membershipDate")
    is_active: bool = Field(alias="isActive")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class MemberListResponse(BaseModel):
    members: List[MemberResponse]
    total_count: int = Field(alias="totalCount")
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


# ============================================================================
# Borrow Record Schemas
# ============================================================================

class BorrowRequest(BaseModel):
    book_id: int = Field(alias="bookId")
    member_id: int = Field(alias="memberId")

    class Config:
        populate_by_name = True


class BorrowRecordResponse(BaseModel):
    id: int
    book_id: int = Field(alias="bookId")
    member_id: int = Field(alias="memberId")
    borrow_date: Optional[date] = Field(None, alias="borrowDate")
    due_date: Optional[date] = Field(None, alias="dueDate")
    return_date: Optional[date] = Field(None, alias="returnDate")
    status: str
    book: Optional[BookResponse] = None
    member: Optional[MemberResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class BorrowRecordListResponse(BaseModel):
    records: List[BorrowRecordResponse]
    total_count: int = Field(alias="totalCount")
    page: int
    page_size: int = Field(alias="pageSize")

    class Config:
        populate_by_name = True


class MemberBorrowedBooksResponse(BaseModel):
    records: List[BorrowRecordResponse]
    member: MemberResponse

    class Config:
        populate_by_name = True
