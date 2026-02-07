"""gRPC Library Service implementation."""

from datetime import date, timedelta
from typing import Optional
import grpc

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import Book, Member, BorrowRecord
from app.config import get_settings

# Import generated protobuf classes (will be generated from .proto)
from app.generated import library_pb2, library_pb2_grpc

settings = get_settings()


def _book_to_proto(book: Book) -> library_pb2.Book:
    """Convert Book model to protobuf message."""
    return library_pb2.Book(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn or "",
        published_year=book.published_year or 0,
        genre=book.genre or "",
        total_copies=book.total_copies,
        available_copies=book.available_copies,
        created_at=book.created_at.isoformat() if book.created_at else "",
        updated_at=book.updated_at.isoformat() if book.updated_at else "",
    )


def _member_to_proto(member: Member) -> library_pb2.Member:
    """Convert Member model to protobuf message."""
    return library_pb2.Member(
        id=member.id,
        name=member.name,
        email=member.email,
        phone=member.phone or "",
        address=member.address or "",
        membership_date=member.membership_date.isoformat() if member.membership_date else "",
        is_active=member.is_active,
        created_at=member.created_at.isoformat() if member.created_at else "",
        updated_at=member.updated_at.isoformat() if member.updated_at else "",
    )


def _borrow_record_to_proto(record: BorrowRecord, include_relations: bool = True) -> library_pb2.BorrowRecord:
    """Convert BorrowRecord model to protobuf message."""
    proto = library_pb2.BorrowRecord(
        id=record.id,
        book_id=record.book_id,
        member_id=record.member_id,
        borrow_date=record.borrow_date.isoformat() if record.borrow_date else "",
        due_date=record.due_date.isoformat() if record.due_date else "",
        return_date=record.return_date.isoformat() if record.return_date else "",
        status=record.status,
    )
    
    if include_relations:
        if record.book:
            proto.book.CopyFrom(_book_to_proto(record.book))
        if record.member:
            proto.member.CopyFrom(_member_to_proto(record.member))
    
    return proto


class LibraryServiceServicer(library_pb2_grpc.LibraryServiceServicer):
    """Implementation of the LibraryService gRPC service."""
    
    # =========================================================================
    # Book Operations
    # =========================================================================
    
    def CreateBook(self, request: library_pb2.CreateBookRequest, context: grpc.ServicerContext) -> library_pb2.Book:
        """Create a new book."""
        with get_db_session() as db:
            # Check if ISBN already exists
            if request.isbn:
                existing = db.query(Book).filter(Book.isbn == request.isbn).first()
                if existing:
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Book with ISBN '{request.isbn}' already exists")
            
            book = Book(
                title=request.title,
                author=request.author,
                isbn=request.isbn if request.isbn else None,
                published_year=request.published_year if request.published_year else None,
                genre=request.genre if request.genre else None,
                total_copies=request.total_copies if request.total_copies > 0 else 1,
                available_copies=request.total_copies if request.total_copies > 0 else 1,
            )
            db.add(book)
            db.flush()
            db.refresh(book)
            return _book_to_proto(book)
    
    def GetBook(self, request: library_pb2.GetBookRequest, context: grpc.ServicerContext) -> library_pb2.Book:
        """Get a book by ID."""
        with get_db_session() as db:
            book = db.query(Book).filter(Book.id == request.id).first()
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.id} not found")
            return _book_to_proto(book)
    
    def UpdateBook(self, request: library_pb2.UpdateBookRequest, context: grpc.ServicerContext) -> library_pb2.Book:
        """Update an existing book."""
        with get_db_session() as db:
            book = db.query(Book).filter(Book.id == request.id).first()
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.id} not found")
            
            # Update fields if provided
            if request.title:
                book.title = request.title
            if request.author:
                book.author = request.author
            if request.isbn:
                # Check for duplicate ISBN
                existing = db.query(Book).filter(Book.isbn == request.isbn, Book.id != request.id).first()
                if existing:
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Book with ISBN '{request.isbn}' already exists")
                book.isbn = request.isbn
            if request.published_year:
                book.published_year = request.published_year
            if request.genre:
                book.genre = request.genre
            if request.total_copies > 0:
                # Adjust available copies proportionally
                diff = request.total_copies - book.total_copies
                book.total_copies = request.total_copies
                book.available_copies = max(0, book.available_copies + diff)
            
            db.flush()
            db.refresh(book)
            return _book_to_proto(book)
    
    def DeleteBook(self, request: library_pb2.DeleteBookRequest, context: grpc.ServicerContext) -> library_pb2.Empty:
        """Delete a book."""
        with get_db_session() as db:
            book = db.query(Book).filter(Book.id == request.id).first()
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.id} not found")
            
            # Check if book has active borrows
            active_borrows = db.query(BorrowRecord).filter(
                BorrowRecord.book_id == request.id,
                BorrowRecord.status == "BORROWED"
            ).count()
            
            if active_borrows > 0:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, 
                            f"Cannot delete book with {active_borrows} active borrow(s)")
            
            db.delete(book)
            return library_pb2.Empty()
    
    def ListBooks(self, request: library_pb2.ListBooksRequest, context: grpc.ServicerContext) -> library_pb2.ListBooksResponse:
        """List books with pagination and optional search."""
        with get_db_session() as db:
            query = db.query(Book)
            
            # Apply search filter
            if request.search:
                search_term = f"%{request.search}%"
                query = query.filter(
                    or_(
                        Book.title.ilike(search_term),
                        Book.author.ilike(search_term)
                    )
                )
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            offset = (page - 1) * page_size
            
            books = query.order_by(Book.id).offset(offset).limit(page_size).all()
            
            return library_pb2.ListBooksResponse(
                books=[_book_to_proto(book) for book in books],
                total_count=total_count,
                page=page,
                page_size=page_size,
            )
    
    # =========================================================================
    # Member Operations
    # =========================================================================
    
    def CreateMember(self, request: library_pb2.CreateMemberRequest, context: grpc.ServicerContext) -> library_pb2.Member:
        """Create a new member."""
        with get_db_session() as db:
            # Check if email already exists
            existing = db.query(Member).filter(Member.email == request.email).first()
            if existing:
                context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Member with email '{request.email}' already exists")
            
            member = Member(
                name=request.name,
                email=request.email,
                phone=request.phone if request.phone else None,
                address=request.address if request.address else None,
            )
            db.add(member)
            db.flush()
            db.refresh(member)
            return _member_to_proto(member)
    
    def GetMember(self, request: library_pb2.GetMemberRequest, context: grpc.ServicerContext) -> library_pb2.Member:
        """Get a member by ID."""
        with get_db_session() as db:
            member = db.query(Member).filter(Member.id == request.id).first()
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.id} not found")
            return _member_to_proto(member)
    
    def UpdateMember(self, request: library_pb2.UpdateMemberRequest, context: grpc.ServicerContext) -> library_pb2.Member:
        """Update an existing member."""
        with get_db_session() as db:
            member = db.query(Member).filter(Member.id == request.id).first()
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.id} not found")
            
            # Update fields if provided
            if request.name:
                member.name = request.name
            if request.email:
                # Check for duplicate email
                existing = db.query(Member).filter(Member.email == request.email, Member.id != request.id).first()
                if existing:
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Member with email '{request.email}' already exists")
                member.email = request.email
            if request.phone:
                member.phone = request.phone
            if request.address:
                member.address = request.address
            # is_active can be explicitly set
            member.is_active = request.is_active
            
            db.flush()
            db.refresh(member)
            return _member_to_proto(member)
    
    def DeleteMember(self, request: library_pb2.DeleteMemberRequest, context: grpc.ServicerContext) -> library_pb2.Empty:
        """Delete a member."""
        with get_db_session() as db:
            member = db.query(Member).filter(Member.id == request.id).first()
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.id} not found")
            
            # Check if member has active borrows
            active_borrows = db.query(BorrowRecord).filter(
                BorrowRecord.member_id == request.id,
                BorrowRecord.status == "BORROWED"
            ).count()
            
            if active_borrows > 0:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                            f"Cannot delete member with {active_borrows} active borrow(s)")
            
            db.delete(member)
            return library_pb2.Empty()
    
    def ListMembers(self, request: library_pb2.ListMembersRequest, context: grpc.ServicerContext) -> library_pb2.ListMembersResponse:
        """List members with pagination and optional search."""
        with get_db_session() as db:
            query = db.query(Member)
            
            # Apply search filter
            if request.search:
                search_term = f"%{request.search}%"
                query = query.filter(
                    or_(
                        Member.name.ilike(search_term),
                        Member.email.ilike(search_term)
                    )
                )
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            offset = (page - 1) * page_size
            
            members = query.order_by(Member.id).offset(offset).limit(page_size).all()
            
            return library_pb2.ListMembersResponse(
                members=[_member_to_proto(member) for member in members],
                total_count=total_count,
                page=page,
                page_size=page_size,
            )
    
    # =========================================================================
    # Borrowing Operations
    # =========================================================================
    
    def BorrowBook(self, request: library_pb2.BorrowBookRequest, context: grpc.ServicerContext) -> library_pb2.BorrowRecord:
        """Record a book borrowing."""
        with get_db_session() as db:
            # Verify book exists and is available
            book = db.query(Book).filter(Book.id == request.book_id).first()
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.book_id} not found")
            
            if book.available_copies <= 0:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, 
                            f"Book '{book.title}' is not available for borrowing")
            
            # Verify member exists and is active
            member = db.query(Member).filter(Member.id == request.member_id).first()
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.member_id} not found")
            
            if not member.is_active:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                            f"Member '{member.name}' is not active")
            
            # Check member's current borrow count
            current_borrows = db.query(BorrowRecord).filter(
                BorrowRecord.member_id == request.member_id,
                BorrowRecord.status == "BORROWED"
            ).count()
            
            if current_borrows >= settings.max_books_per_member:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                            f"Member has reached maximum borrow limit ({settings.max_books_per_member} books)")
            
            # Check if member already has this book borrowed
            existing_borrow = db.query(BorrowRecord).filter(
                BorrowRecord.book_id == request.book_id,
                BorrowRecord.member_id == request.member_id,
                BorrowRecord.status == "BORROWED"
            ).first()
            
            if existing_borrow:
                context.abort(grpc.StatusCode.ALREADY_EXISTS,
                            f"Member already has this book borrowed")
            
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
            db.flush()
            db.refresh(borrow_record)
            
            return _borrow_record_to_proto(borrow_record)
    
    def ReturnBook(self, request: library_pb2.ReturnBookRequest, context: grpc.ServicerContext) -> library_pb2.BorrowRecord:
        """Record a book return."""
        with get_db_session() as db:
            # Find the borrow record
            borrow_record = db.query(BorrowRecord).filter(BorrowRecord.id == request.borrow_id).first()
            if not borrow_record:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Borrow record with ID {request.borrow_id} not found")
            
            if borrow_record.status == "RETURNED":
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Book has already been returned")
            
            # Update borrow record
            borrow_record.return_date = date.today()
            borrow_record.status = "RETURNED"
            
            # Increase available copies
            book = db.query(Book).filter(Book.id == borrow_record.book_id).first()
            if book:
                book.available_copies += 1
            
            db.flush()
            db.refresh(borrow_record)
            
            return _borrow_record_to_proto(borrow_record)
    
    def GetBorrowRecord(self, request: library_pb2.GetBorrowRecordRequest, context: grpc.ServicerContext) -> library_pb2.BorrowRecord:
        """Get a borrow record by ID."""
        with get_db_session() as db:
            record = db.query(BorrowRecord).filter(BorrowRecord.id == request.id).first()
            if not record:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Borrow record with ID {request.id} not found")
            return _borrow_record_to_proto(record)
    
    def ListBorrowRecords(self, request: library_pb2.ListBorrowRecordsRequest, context: grpc.ServicerContext) -> library_pb2.ListBorrowRecordsResponse:
        """List borrow records with pagination and filters."""
        with get_db_session() as db:
            query = db.query(BorrowRecord)
            
            # Apply filters
            if request.member_id > 0:
                query = query.filter(BorrowRecord.member_id == request.member_id)
            if request.book_id > 0:
                query = query.filter(BorrowRecord.book_id == request.book_id)
            if request.status:
                query = query.filter(BorrowRecord.status == request.status)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            offset = (page - 1) * page_size
            
            records = query.order_by(BorrowRecord.id.desc()).offset(offset).limit(page_size).all()
            
            return library_pb2.ListBorrowRecordsResponse(
                records=[_borrow_record_to_proto(record) for record in records],
                total_count=total_count,
                page=page,
                page_size=page_size,
            )
    
    def GetMemberBorrowedBooks(self, request: library_pb2.GetMemberBorrowedBooksRequest, context: grpc.ServicerContext) -> library_pb2.GetMemberBorrowedBooksResponse:
        """Get all currently borrowed books for a member."""
        with get_db_session() as db:
            member = db.query(Member).filter(Member.id == request.member_id).first()
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.member_id} not found")
            
            records = db.query(BorrowRecord).filter(
                BorrowRecord.member_id == request.member_id,
                BorrowRecord.status == "BORROWED"
            ).all()
            
            return library_pb2.GetMemberBorrowedBooksResponse(
                records=[_borrow_record_to_proto(record) for record in records],
                member=_member_to_proto(member),
            )
