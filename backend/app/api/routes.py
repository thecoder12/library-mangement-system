"""REST API routes for the Library Service."""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Member, BorrowRecord
from app.config import get_settings
from app.api.schemas import (
    BookCreate, BookUpdate, BookResponse, BookListResponse,
    MemberCreate, MemberUpdate, MemberResponse, MemberListResponse,
    BorrowRequest, BorrowRecordResponse, BorrowRecordListResponse,
    MemberBorrowedBooksResponse,
)

settings = get_settings()

# Create routers
books_router = APIRouter(prefix="/api/books", tags=["Books"])
members_router = APIRouter(prefix="/api/members", tags=["Members"])
borrows_router = APIRouter(prefix="/api/borrows", tags=["Borrowing"])


# ============================================================================
# Book Routes
# ============================================================================

@books_router.post("", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book."""
    # Check if ISBN already exists
    if book.isbn:
        existing = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Book with ISBN '{book.isbn}' already exists")
    
    db_book = Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        published_year=book.published_year,
        genre=book.genre,
        total_copies=book.total_copies,
        available_copies=book.total_copies,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@books_router.get("", response_model=BookListResponse)
def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List books with pagination and optional search."""
    query = db.query(Book)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(Book.title.ilike(search_term), Book.author.ilike(search_term))
        )
    
    total_count = query.count()
    offset = (page - 1) * page_size
    books = query.order_by(Book.id).offset(offset).limit(page_size).all()
    
    return BookListResponse(
        books=books,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@books_router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a book by ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
    return book


@books_router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    """Update an existing book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
    
    update_data = book_update.model_dump(exclude_unset=True, by_alias=False)
    
    if "isbn" in update_data and update_data["isbn"]:
        existing = db.query(Book).filter(Book.isbn == update_data["isbn"], Book.id != book_id).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Book with ISBN '{update_data['isbn']}' already exists")
    
    if "total_copies" in update_data:
        diff = update_data["total_copies"] - book.total_copies
        book.available_copies = max(0, book.available_copies + diff)
    
    for field, value in update_data.items():
        if field != "total_copies" or value is not None:
            setattr(book, field, value)
    
    db.commit()
    db.refresh(book)
    return book


@books_router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
    
    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.status == "BORROWED"
    ).count()
    
    if active_borrows > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete book with {active_borrows} active borrow(s)")
    
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}


# ============================================================================
# Member Routes
# ============================================================================

@members_router.post("", response_model=MemberResponse)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """Create a new member."""
    existing = db.query(Member).filter(Member.email == member.email).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Member with email '{member.email}' already exists")
    
    db_member = Member(
        name=member.name,
        email=member.email,
        phone=member.phone,
        address=member.address,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@members_router.get("", response_model=MemberListResponse)
def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List members with pagination and optional search."""
    query = db.query(Member)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(Member.name.ilike(search_term), Member.email.ilike(search_term))
        )
    
    total_count = query.count()
    offset = (page - 1) * page_size
    members = query.order_by(Member.id).offset(offset).limit(page_size).all()
    
    return MemberListResponse(
        members=members,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@members_router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """Get a member by ID."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    return member


@members_router.put("/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, member_update: MemberUpdate, db: Session = Depends(get_db)):
    """Update an existing member."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    update_data = member_update.model_dump(exclude_unset=True, by_alias=False)
    
    if "email" in update_data and update_data["email"]:
        existing = db.query(Member).filter(Member.email == update_data["email"], Member.id != member_id).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Member with email '{update_data['email']}' already exists")
    
    for field, value in update_data.items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    return member


@members_router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """Delete a member."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.member_id == member_id,
        BorrowRecord.status == "BORROWED"
    ).count()
    
    if active_borrows > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete member with {active_borrows} active borrow(s)")
    
    db.delete(member)
    db.commit()
    return {"message": "Member deleted successfully"}


@members_router.get("/{member_id}/borrowed", response_model=MemberBorrowedBooksResponse)
def get_member_borrowed_books(member_id: int, db: Session = Depends(get_db)):
    """Get all currently borrowed books for a member."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {member_id} not found")
    
    records = db.query(BorrowRecord).filter(
        BorrowRecord.member_id == member_id,
        BorrowRecord.status == "BORROWED"
    ).all()
    
    return MemberBorrowedBooksResponse(records=records, member=member)


# ============================================================================
# Borrow Routes
# ============================================================================

@borrows_router.post("", response_model=BorrowRecordResponse)
def borrow_book(request: BorrowRequest, db: Session = Depends(get_db)):
    """Record a book borrowing."""
    # Verify book exists and is available
    book = db.query(Book).filter(Book.id == request.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book with ID {request.book_id} not found")
    
    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail=f"Book '{book.title}' is not available for borrowing")
    
    # Verify member exists and is active
    member = db.query(Member).filter(Member.id == request.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail=f"Member with ID {request.member_id} not found")
    
    if not member.is_active:
        raise HTTPException(status_code=400, detail=f"Member '{member.name}' is not active")
    
    # Check member's current borrow count
    current_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.member_id == request.member_id,
        BorrowRecord.status == "BORROWED"
    ).count()
    
    if current_borrows >= settings.max_books_per_member:
        raise HTTPException(status_code=400, 
                          detail=f"Member has reached maximum borrow limit ({settings.max_books_per_member} books)")
    
    # Check if member already has this book borrowed
    existing_borrow = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == request.book_id,
        BorrowRecord.member_id == request.member_id,
        BorrowRecord.status == "BORROWED"
    ).first()
    
    if existing_borrow:
        raise HTTPException(status_code=409, detail="Member already has this book borrowed")
    
    # Create borrow record
    borrow_record = BorrowRecord(
        book_id=request.book_id,
        member_id=request.member_id,
        borrow_date=date.today(),
        due_date=date.today() + timedelta(days=settings.default_borrow_days),
        status="BORROWED",
    )
    
    # Decrease available copies
    book.available_copies -= 1
    
    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)
    
    return borrow_record


@borrows_router.get("", response_model=BorrowRecordListResponse)
def list_borrow_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    member_id: Optional[int] = None,
    book_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List borrow records with pagination and filters."""
    query = db.query(BorrowRecord)
    
    if member_id:
        query = query.filter(BorrowRecord.member_id == member_id)
    if book_id:
        query = query.filter(BorrowRecord.book_id == book_id)
    if status:
        query = query.filter(BorrowRecord.status == status)
    
    total_count = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(BorrowRecord.id.desc()).offset(offset).limit(page_size).all()
    
    return BorrowRecordListResponse(
        records=records,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@borrows_router.get("/{borrow_id}", response_model=BorrowRecordResponse)
def get_borrow_record(borrow_id: int, db: Session = Depends(get_db)):
    """Get a borrow record by ID."""
    record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Borrow record with ID {borrow_id} not found")
    return record


@borrows_router.post("/{borrow_id}/return", response_model=BorrowRecordResponse)
def return_book(borrow_id: int, db: Session = Depends(get_db)):
    """Record a book return."""
    borrow_record = db.query(BorrowRecord).filter(BorrowRecord.id == borrow_id).first()
    if not borrow_record:
        raise HTTPException(status_code=404, detail=f"Borrow record with ID {borrow_id} not found")
    
    if borrow_record.status == "RETURNED":
        raise HTTPException(status_code=400, detail="Book has already been returned")
    
    # Update borrow record
    borrow_record.return_date = date.today()
    borrow_record.status = "RETURNED"
    
    # Increase available copies
    book = db.query(Book).filter(Book.id == borrow_record.book_id).first()
    if book:
        book.available_copies += 1
    
    db.commit()
    db.refresh(borrow_record)
    
    return borrow_record
