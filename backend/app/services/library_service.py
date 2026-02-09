"""gRPC Library Service implementation using Repository Pattern."""

from datetime import date, timedelta
import grpc

from app.config import get_settings
from app.domain.entities import BookEntity, MemberEntity, BorrowRecordEntity
from app.repositories import UnitOfWork

# Import generated protobuf classes
from app.generated import library_pb2, library_pb2_grpc

settings = get_settings()


# ============================================================================
# Helper functions to convert entities to protobuf messages
# ============================================================================

def _book_to_proto(entity: BookEntity) -> library_pb2.Book:
    """Convert BookEntity to protobuf message."""
    return library_pb2.Book(
        id=entity.id,
        title=entity.title,
        author=entity.author,
        isbn=entity.isbn or "",
        published_year=entity.published_year or 0,
        genre=entity.genre or "",
        total_copies=entity.total_copies,
        available_copies=entity.available_copies,
        created_at=entity.created_at.isoformat() if entity.created_at else "",
        updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
    )


def _member_to_proto(entity: MemberEntity) -> library_pb2.Member:
    """Convert MemberEntity to protobuf message."""
    return library_pb2.Member(
        id=entity.id,
        name=entity.name,
        email=entity.email,
        phone=entity.phone or "",
        address=entity.address or "",
        membership_date=entity.membership_date.isoformat() if entity.membership_date else "",
        is_active=entity.is_active,
        created_at=entity.created_at.isoformat() if entity.created_at else "",
        updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
    )


def _borrow_record_to_proto(entity: BorrowRecordEntity) -> library_pb2.BorrowRecord:
    """Convert BorrowRecordEntity to protobuf message."""
    proto = library_pb2.BorrowRecord(
        id=entity.id,
        book_id=entity.book_id,
        member_id=entity.member_id,
        borrow_date=entity.borrow_date.isoformat() if entity.borrow_date else "",
        due_date=entity.due_date.isoformat() if entity.due_date else "",
        return_date=entity.return_date.isoformat() if entity.return_date else "",
        status=entity.status,
    )
    
    if entity.book:
        proto.book.CopyFrom(_book_to_proto(entity.book))
    if entity.member:
        proto.member.CopyFrom(_member_to_proto(entity.member))
    
    return proto


class LibraryServiceServicer(library_pb2_grpc.LibraryServiceServicer):
    """Implementation of the LibraryService gRPC service using Repository Pattern."""
    
    # =========================================================================
    # Book Operations
    # =========================================================================
    
    def CreateBook(self, request: library_pb2.CreateBookRequest, context: grpc.ServicerContext) -> library_pb2.Book:
        """Create a new book."""
        with UnitOfWork() as uow:
            # Check if ISBN already exists
            if request.isbn and uow.books.isbn_exists(request.isbn):
                context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Book with ISBN '{request.isbn}' already exists")
            
            entity = BookEntity(
                title=request.title,
                author=request.author,
                isbn=request.isbn if request.isbn else None,
                published_year=request.published_year if request.published_year else None,
                genre=request.genre if request.genre else None,
                total_copies=request.total_copies if request.total_copies > 0 else 1,
                available_copies=request.total_copies if request.total_copies > 0 else 1,
            )
            
            created = uow.books.create(entity)
            uow.commit()
            return _book_to_proto(created)
    
    def GetBook(self, request: library_pb2.GetBookRequest, context: grpc.ServicerContext) -> library_pb2.Book:
        """Get a book by ID."""
        with UnitOfWork() as uow:
            book = uow.books.get_by_id(request.id)
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.id} not found")
            return _book_to_proto(book)
    
    def UpdateBook(self, request: library_pb2.UpdateBookRequest, context: grpc.ServicerContext) -> library_pb2.Book:
        """Update an existing book."""
        with UnitOfWork() as uow:
            existing = uow.books.get_by_id(request.id)
            if not existing:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.id} not found")
            
            # Build update kwargs
            update_data = {}
            if request.title:
                update_data["title"] = request.title
            if request.author:
                update_data["author"] = request.author
            if request.isbn:
                if uow.books.isbn_exists(request.isbn, exclude_id=request.id):
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Book with ISBN '{request.isbn}' already exists")
                update_data["isbn"] = request.isbn
            if request.published_year:
                update_data["published_year"] = request.published_year
            if request.genre:
                update_data["genre"] = request.genre
            if request.total_copies > 0:
                update_data["total_copies"] = request.total_copies
            
            updated = uow.books.update(request.id, **update_data)
            uow.commit()
            return _book_to_proto(updated)
    
    def DeleteBook(self, request: library_pb2.DeleteBookRequest, context: grpc.ServicerContext) -> library_pb2.Empty:
        """Delete a book."""
        with UnitOfWork() as uow:
            book = uow.books.get_by_id(request.id)
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.id} not found")
            
            active_borrows = uow.borrows.get_active_borrows_for_book(request.id)
            if active_borrows > 0:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, 
                            f"Cannot delete book with {active_borrows} active borrow(s)")
            
            uow.books.delete_by_id(request.id)
            uow.commit()
            return library_pb2.Empty()
    
    def ListBooks(self, request: library_pb2.ListBooksRequest, context: grpc.ServicerContext) -> library_pb2.ListBooksResponse:
        """List books with pagination and optional search."""
        with UnitOfWork() as uow:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            search = request.search if request.search else None
            
            result = uow.books.list_paginated(page=page, page_size=page_size, search=search)
            
            return library_pb2.ListBooksResponse(
                books=[_book_to_proto(b) for b in result.items],
                total_count=result.total_count,
                page=result.page,
                page_size=result.page_size,
            )
    
    # =========================================================================
    # Member Operations
    # =========================================================================
    
    def CreateMember(self, request: library_pb2.CreateMemberRequest, context: grpc.ServicerContext) -> library_pb2.Member:
        """Create a new member."""
        with UnitOfWork() as uow:
            if uow.members.email_exists(request.email):
                context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Member with email '{request.email}' already exists")
            
            entity = MemberEntity(
                name=request.name,
                email=request.email,
                phone=request.phone if request.phone else None,
                address=request.address if request.address else None,
            )
            
            created = uow.members.create(entity)
            uow.commit()
            return _member_to_proto(created)
    
    def GetMember(self, request: library_pb2.GetMemberRequest, context: grpc.ServicerContext) -> library_pb2.Member:
        """Get a member by ID."""
        with UnitOfWork() as uow:
            member = uow.members.get_by_id(request.id)
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.id} not found")
            return _member_to_proto(member)
    
    def UpdateMember(self, request: library_pb2.UpdateMemberRequest, context: grpc.ServicerContext) -> library_pb2.Member:
        """Update an existing member."""
        with UnitOfWork() as uow:
            existing = uow.members.get_by_id(request.id)
            if not existing:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.id} not found")
            
            # Build update kwargs
            update_data = {}
            if request.name:
                update_data["name"] = request.name
            if request.email:
                if uow.members.email_exists(request.email, exclude_id=request.id):
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Member with email '{request.email}' already exists")
                update_data["email"] = request.email
            if request.phone:
                update_data["phone"] = request.phone
            if request.address:
                update_data["address"] = request.address
            # is_active is always included
            update_data["is_active"] = request.is_active
            
            updated = uow.members.update(request.id, **update_data)
            uow.commit()
            return _member_to_proto(updated)
    
    def DeleteMember(self, request: library_pb2.DeleteMemberRequest, context: grpc.ServicerContext) -> library_pb2.Empty:
        """Delete a member."""
        with UnitOfWork() as uow:
            member = uow.members.get_by_id(request.id)
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.id} not found")
            
            active_borrows = uow.borrows.get_active_borrows_count(request.id)
            if active_borrows > 0:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                            f"Cannot delete member with {active_borrows} active borrow(s)")
            
            uow.members.delete_by_id(request.id)
            uow.commit()
            return library_pb2.Empty()
    
    def ListMembers(self, request: library_pb2.ListMembersRequest, context: grpc.ServicerContext) -> library_pb2.ListMembersResponse:
        """List members with pagination and optional search."""
        with UnitOfWork() as uow:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            search = request.search if request.search else None
            
            result = uow.members.list_paginated(page=page, page_size=page_size, search=search)
            
            return library_pb2.ListMembersResponse(
                members=[_member_to_proto(m) for m in result.items],
                total_count=result.total_count,
                page=result.page,
                page_size=result.page_size,
            )
    
    # =========================================================================
    # Borrowing Operations
    # =========================================================================
    
    def BorrowBook(self, request: library_pb2.BorrowBookRequest, context: grpc.ServicerContext) -> library_pb2.BorrowRecord:
        """Record a book borrowing."""
        with UnitOfWork() as uow:
            # Verify book exists and is available
            book = uow.books.get_by_id(request.book_id)
            if not book:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Book with ID {request.book_id} not found")
            
            if not book.is_available:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, 
                            f"Book '{book.title}' is not available for borrowing")
            
            # Verify member exists and is active
            member = uow.members.get_by_id(request.member_id)
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.member_id} not found")
            
            if not member.can_borrow:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                            f"Member '{member.name}' is not active")
            
            # Check member's current borrow count
            current_borrows = uow.borrows.get_active_borrows_count(request.member_id)
            if current_borrows >= settings.max_books_per_member:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION,
                            f"Member has reached maximum borrow limit ({settings.max_books_per_member} books)")
            
            # Check if member already has this book borrowed
            if uow.borrows.has_active_borrow(request.book_id, request.member_id):
                context.abort(grpc.StatusCode.ALREADY_EXISTS,
                            "Member already has this book borrowed")
            
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
            
            return _borrow_record_to_proto(created)
    
    def ReturnBook(self, request: library_pb2.ReturnBookRequest, context: grpc.ServicerContext) -> library_pb2.BorrowRecord:
        """Record a book return."""
        with UnitOfWork() as uow:
            record = uow.borrows.get_by_id(request.borrow_id)
            if not record:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Borrow record with ID {request.borrow_id} not found")
            
            if record.is_returned:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Book has already been returned")
            
            # Mark as returned
            returned = uow.borrows.mark_returned(request.borrow_id)
            
            # Increase available copies
            uow.books.increase_available_copies(record.book_id)
            
            uow.commit()
            
            return _borrow_record_to_proto(returned)
    
    def GetBorrowRecord(self, request: library_pb2.GetBorrowRecordRequest, context: grpc.ServicerContext) -> library_pb2.BorrowRecord:
        """Get a borrow record by ID."""
        with UnitOfWork() as uow:
            record = uow.borrows.get_by_id(request.id)
            if not record:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Borrow record with ID {request.id} not found")
            return _borrow_record_to_proto(record)
    
    def ListBorrowRecords(self, request: library_pb2.ListBorrowRecordsRequest, context: grpc.ServicerContext) -> library_pb2.ListBorrowRecordsResponse:
        """List borrow records with pagination and filters."""
        with UnitOfWork() as uow:
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 10
            member_id = request.member_id if request.member_id > 0 else None
            book_id = request.book_id if request.book_id > 0 else None
            status = request.status if request.status else None
            
            result = uow.borrows.list_paginated(
                page=page,
                page_size=page_size,
                member_id=member_id,
                book_id=book_id,
                status=status,
            )
            
            return library_pb2.ListBorrowRecordsResponse(
                records=[_borrow_record_to_proto(r) for r in result.items],
                total_count=result.total_count,
                page=result.page,
                page_size=result.page_size,
            )
    
    def GetMemberBorrowedBooks(self, request: library_pb2.GetMemberBorrowedBooksRequest, context: grpc.ServicerContext) -> library_pb2.GetMemberBorrowedBooksResponse:
        """Get all currently borrowed books for a member."""
        with UnitOfWork() as uow:
            member = uow.members.get_by_id(request.member_id)
            if not member:
                context.abort(grpc.StatusCode.NOT_FOUND, f"Member with ID {request.member_id} not found")
            
            records = uow.borrows.get_member_active_borrows(request.member_id)
            
            return library_pb2.GetMemberBorrowedBooksResponse(
                records=[_borrow_record_to_proto(r) for r in records],
                member=_member_to_proto(member),
            )
