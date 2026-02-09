"""REST API routes for the Library Service using Repository Pattern."""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_settings
from app.logging_config import get_logger
from app.domain.entities import BookEntity, MemberEntity, BorrowRecordEntity
from app.repositories import UnitOfWork, get_unit_of_work
from app.api.schemas import (
    BookCreate, BookUpdate, BookResponse, BookListResponse,
    MemberCreate, MemberUpdate, MemberResponse, MemberListResponse,
    BorrowRequest, BorrowRecordResponse, BorrowRecordListResponse,
    MemberBorrowedBooksResponse,
)
from app.api.constants import BookEndpoints, MemberEndpoints, BorrowEndpoints

settings = get_settings()
logger = get_logger("api.routes")

# Create routers with centralized endpoint paths
books_router = APIRouter(prefix=BookEndpoints.BASE, tags=["Books"])
members_router = APIRouter(prefix=MemberEndpoints.BASE, tags=["Members"])
borrows_router = APIRouter(prefix=BorrowEndpoints.BASE, tags=["Borrowing"])


# ============================================================================
# Helper functions to convert entities to response models
# ============================================================================

def _book_to_response(entity: BookEntity) -> dict:
    """Convert BookEntity to response dict."""
    return {
        "id": entity.id,
        "title": entity.title,
        "author": entity.author,
        "isbn": entity.isbn,
        "publishedYear": entity.published_year,
        "genre": entity.genre,
        "totalCopies": entity.total_copies,
        "availableCopies": entity.available_copies,
        "createdAt": entity.created_at.isoformat() if entity.created_at else None,
        "updatedAt": entity.updated_at.isoformat() if entity.updated_at else None,
    }


def _member_to_response(entity: MemberEntity) -> dict:
    """Convert MemberEntity to response dict."""
    return {
        "id": entity.id,
        "name": entity.name,
        "email": entity.email,
        "phone": entity.phone,
        "address": entity.address,
        "membershipDate": entity.membership_date.isoformat() if entity.membership_date else None,
        "isActive": entity.is_active,
        "createdAt": entity.created_at.isoformat() if entity.created_at else None,
        "updatedAt": entity.updated_at.isoformat() if entity.updated_at else None,
    }


def _borrow_to_response(entity: BorrowRecordEntity) -> dict:
    """Convert BorrowRecordEntity to response dict."""
    response = {
        "id": entity.id,
        "bookId": entity.book_id,
        "memberId": entity.member_id,
        "borrowDate": entity.borrow_date.isoformat() if entity.borrow_date else None,
        "dueDate": entity.due_date.isoformat() if entity.due_date else None,
        "returnDate": entity.return_date.isoformat() if entity.return_date else None,
        "status": entity.status,
        "createdAt": entity.created_at.isoformat() if entity.created_at else None,
        "updatedAt": entity.updated_at.isoformat() if entity.updated_at else None,
    }
    
    if entity.book:
        response["book"] = _book_to_response(entity.book)
    if entity.member:
        response["member"] = _member_to_response(entity.member)
    
    return response


# ============================================================================
# Book Routes
# ============================================================================

@books_router.post("", response_model=BookResponse)
def create_book(book: BookCreate, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Create a new book."""
    with uow:
        # Check if ISBN already exists
        if book.isbn and uow.books.isbn_exists(book.isbn):
            logger.warning("Duplicate ISBN attempt", extra={"isbn": book.isbn})
            raise HTTPException(status_code=409, detail=f"Book with ISBN '{book.isbn}' already exists")
        
        entity = BookEntity(
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            published_year=book.published_year,
            genre=book.genre,
            total_copies=book.total_copies,
            available_copies=book.total_copies,
        )
        
        created = uow.books.create(entity)
        uow.commit()
        
        logger.info("Book created", extra={"book_id": created.id, "title": created.title, "isbn": created.isbn})
        return _book_to_response(created)


@books_router.get("", response_model=BookListResponse)
def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """List books with pagination and optional search."""
    with uow:
        result = uow.books.list_paginated(page=page, page_size=page_size, search=search)
        return {
            "books": [_book_to_response(b) for b in result.items],
            "totalCount": result.total_count,
            "page": result.page,
            "pageSize": result.page_size,
        }


@books_router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get a book by ID."""
    with uow:
        book = uow.books.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        return _book_to_response(book)


@books_router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Update an existing book."""
    with uow:
        existing = uow.books.get_by_id(book_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        update_data = book_update.model_dump(exclude_unset=True, by_alias=False)
        
        if "isbn" in update_data and update_data["isbn"]:
            if uow.books.isbn_exists(update_data["isbn"], exclude_id=book_id):
                raise HTTPException(status_code=409, detail=f"Book with ISBN '{update_data['isbn']}' already exists")
        
        updated = uow.books.update(book_id, **update_data)
        uow.commit()
        
        return _book_to_response(updated)


@books_router.delete("/{book_id}")
def delete_book(book_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Delete a book. Books with borrow history cannot be deleted."""
    with uow:
        book = uow.books.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        # Check for active borrows
        active_borrows = uow.borrows.get_active_borrows_for_book(book_id)
        if active_borrows > 0:
            logger.warning("Cannot delete book with active borrows", extra={"book_id": book_id, "active_borrows": active_borrows})
            raise HTTPException(status_code=400, detail=f"Cannot delete book with {active_borrows} active borrow(s). Please wait for returns.")
        
        # Check for total borrow history (including returned)
        total_borrows = uow.borrows.get_total_borrows_count_for_book(book_id)
        if total_borrows > 0:
            logger.warning("Cannot delete book with borrow history", extra={"book_id": book_id, "total_borrows": total_borrows})
            raise HTTPException(status_code=400, detail=f"Cannot delete book with borrow history ({total_borrows} record(s)). Consider updating the book instead.")
        
        # No borrow history - safe to delete
        book_title = book.title
        uow.books.delete_by_id(book_id)
        uow.commit()
        
        logger.info("Book deleted", extra={"book_id": book_id, "title": book_title})
        return {"message": "Book deleted successfully"}


# ============================================================================
# Member Routes
# ============================================================================

@members_router.post("", response_model=MemberResponse)
def create_member(member: MemberCreate, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Create a new member."""
    with uow:
        if uow.members.email_exists(member.email):
            logger.warning("Duplicate email attempt", extra={"email": member.email})
            raise HTTPException(status_code=409, detail=f"Member with email '{member.email}' already exists")
        
        entity = MemberEntity(
            name=member.name,
            email=member.email,
            phone=member.phone,
            address=member.address,
        )
        
        created = uow.members.create(entity)
        uow.commit()
        
        logger.info("Member created", extra={"member_id": created.id, "member_name": created.name, "email": created.email})
        return _member_to_response(created)


@members_router.get("", response_model=MemberListResponse)
def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """List members with pagination and optional search."""
    with uow:
        result = uow.members.list_paginated(page=page, page_size=page_size, search=search)
        return {
            "members": [_member_to_response(m) for m in result.items],
            "totalCount": result.total_count,
            "page": result.page,
            "pageSize": result.page_size,
        }


@members_router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get a member by ID."""
    with uow:
        member = uow.members.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
        return _member_to_response(member)


@members_router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member_update: MemberUpdate, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Update an existing member."""
    with uow:
        existing = uow.members.get_by_id(member_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
        
        update_data = member_update.model_dump(exclude_unset=True, by_alias=False)
        
        if "email" in update_data and update_data["email"]:
            if uow.members.email_exists(update_data["email"], exclude_id=member_id):
                raise HTTPException(status_code=409, detail=f"Member with email '{update_data['email']}' already exists")
        
        updated = uow.members.update(member_id, **update_data)
        uow.commit()
        
        return _member_to_response(updated)


@members_router.delete("/{member_id}")
def delete_member(member_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Delete a member. If member has borrow history, they are deactivated instead."""
    with uow:
        member = uow.members.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
        
        # Check for active borrows - cannot delete/deactivate with unreturned books
        active_borrows = uow.borrows.get_active_borrows_count(member_id)
        if active_borrows > 0:
            raise HTTPException(status_code=400, detail=f"Cannot delete member with {active_borrows} active borrow(s). Please return all books first.")
        
        # Check for total borrow history (including returned)
        total_borrows = uow.borrows.get_total_borrows_count(member_id)
        if total_borrows > 0:
            # Deactivate instead of delete to preserve borrow history
            uow.members.update(member_id, is_active=False)
            uow.commit()
            logger.info("Member deactivated (has borrow history)", extra={"member_id": member_id, "total_borrows": total_borrows})
            return {"message": "Member deactivated successfully (has borrow history)", "deactivated": True}
        
        # No borrow history - safe to delete
        uow.members.delete_by_id(member_id)
        uow.commit()
        logger.info("Member deleted", extra={"member_id": member_id})
        return {"message": "Member deleted successfully", "deleted": True}


@members_router.get("/{member_id}/borrowed", response_model=MemberBorrowedBooksResponse)
def get_member_borrowed_books(member_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get all currently borrowed books for a member."""
    with uow:
        member = uow.members.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
        
        records = uow.borrows.get_member_active_borrows(member_id)
        
        return {
            "records": [_borrow_to_response(r) for r in records],
            "member": _member_to_response(member),
        }


# ============================================================================
# Borrow Routes
# ============================================================================

@borrows_router.post("", response_model=BorrowRecordResponse)
def borrow_book(request: BorrowRequest, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Record a book borrowing."""
    with uow:
        # Verify book exists and is available
        book = uow.books.get_by_id(request.book_id)
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {request.book_id} not found")
        
        if not book.is_available:
            logger.warning("Book not available for borrowing", extra={"book_id": request.book_id, "title": book.title})
            raise HTTPException(status_code=400, detail=f"Book '{book.title}' is not available for borrowing")
        
        # Verify member exists and is active
        member = uow.members.get_by_id(request.member_id)
        if not member:
            raise HTTPException(status_code=404, detail=f"Member with ID {request.member_id} not found")
        
        if not member.can_borrow:
            logger.warning("Inactive member borrow attempt", extra={"member_id": request.member_id, "member_name": member.name})
            raise HTTPException(status_code=400, detail=f"Member '{member.name}' is not active")
        
        # Check member's current borrow count
        current_borrows = uow.borrows.get_active_borrows_count(request.member_id)
        if current_borrows >= settings.max_books_per_member:
            logger.warning("Member borrow limit exceeded", extra={"member_id": request.member_id, "current_borrows": current_borrows, "limit": settings.max_books_per_member})
            raise HTTPException(status_code=400, detail=f"Member has reached maximum borrow limit ({settings.max_books_per_member} books)")
        
        # Check if member already has this book borrowed
        if uow.borrows.has_active_borrow(request.book_id, request.member_id):
            logger.warning("Duplicate borrow attempt", extra={"book_id": request.book_id, "member_id": request.member_id})
            raise HTTPException(status_code=409, detail="Member already has this book borrowed")
        
        # Create borrow record
        borrow_entity = BorrowRecordEntity(
            book_id=request.book_id,
            member_id=request.member_id,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=settings.default_borrow_days),
            status="BORROWED",
        )
        
        # Decrease available copies
        uow.books.decrease_available_copies(request.book_id)
        
        created = uow.borrows.create(borrow_entity)
        uow.commit()
        
        logger.info("Book borrowed", extra={
            "borrow_id": created.id,
            "book_id": request.book_id,
            "member_id": request.member_id,
            "due_date": str(created.due_date),
        })
        return _borrow_to_response(created)


@borrows_router.get("", response_model=BorrowRecordListResponse)
def list_borrow_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    member_id: Optional[int] = None,
    book_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    """List borrow records with pagination and filters. Search by book title/author or member name/email."""
    with uow:
        result = uow.borrows.list_paginated(
            page=page,
            page_size=page_size,
            member_id=member_id,
            book_id=book_id,
            status=status,
            search=search,
        )
        return {
            "records": [_borrow_to_response(r) for r in result.items],
            "totalCount": result.total_count,
            "page": result.page,
            "pageSize": result.page_size,
        }


@borrows_router.get("/{borrow_id}", response_model=BorrowRecordResponse)
def get_borrow_record(borrow_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Get a borrow record by ID."""
    with uow:
        record = uow.borrows.get_by_id(borrow_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Borrow record with ID {borrow_id} not found")
        return _borrow_to_response(record)


@borrows_router.post("/{borrow_id}/return", response_model=BorrowRecordResponse)
def return_book(borrow_id: int, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Record a book return."""
    with uow:
        record = uow.borrows.get_by_id(borrow_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Borrow record with ID {borrow_id} not found")
        
        if record.is_returned:
            logger.warning("Duplicate return attempt", extra={"borrow_id": borrow_id})
            raise HTTPException(status_code=400, detail="Book has already been returned")
        
        # Mark as returned
        returned = uow.borrows.mark_returned(borrow_id)
        
        # Increase available copies
        uow.books.increase_available_copies(record.book_id)
        
        uow.commit()
        
        logger.info("Book returned", extra={
            "borrow_id": borrow_id,
            "book_id": record.book_id,
            "member_id": record.member_id,
            "return_date": str(returned.return_date),
        })
        return _borrow_to_response(returned)
