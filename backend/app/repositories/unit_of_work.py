"""Unit of Work pattern for transaction and session management."""

from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.book_repository import BookRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.borrow_repository import BorrowRepository


class UnitOfWork:
    """
    Unit of Work pattern implementation.
    
    Provides a single transaction boundary for multiple repository operations.
    Ensures all changes are committed or rolled back together.
    
    Usage:
        with UnitOfWork() as uow:
            book = uow.books.create(book_entity)
            member = uow.members.get_by_id(member_id)
            uow.commit()
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize Unit of Work.
        
        Args:
            session: Optional existing session. If not provided, a new one is created.
        """
        self._session = session
        self._owns_session = session is None
        
        # Repositories (lazily initialized)
        self._books: Optional[BookRepository] = None
        self._members: Optional[MemberRepository] = None
        self._borrows: Optional[BorrowRepository] = None
    
    def __enter__(self) -> "UnitOfWork":
        """Enter context manager, creating session if needed."""
        if self._session is None:
            self._session = SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, handling rollback and cleanup."""
        if exc_type is not None:
            self.rollback()
        
        if self._owns_session and self._session:
            self._session.close()
    
    @property
    def session(self) -> Session:
        """Get the database session."""
        if self._session is None:
            raise RuntimeError("UnitOfWork must be used within a context manager")
        return self._session
    
    @property
    def books(self) -> BookRepository:
        """Get the book repository."""
        if self._books is None:
            self._books = BookRepository(self.session)
        return self._books
    
    @property
    def members(self) -> MemberRepository:
        """Get the member repository."""
        if self._members is None:
            self._members = MemberRepository(self.session)
        return self._members
    
    @property
    def borrows(self) -> BorrowRepository:
        """Get the borrow repository."""
        if self._borrows is None:
            self._borrows = BorrowRepository(self.session)
        return self._borrows
    
    def commit(self):
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()
    
    def flush(self):
        """Flush pending changes to the database without committing."""
        self.session.flush()


def get_unit_of_work() -> UnitOfWork:
    """
    FastAPI dependency for getting a Unit of Work instance.
    
    Usage in routes:
        @router.post("/books")
        def create_book(book: BookCreate, uow: UnitOfWork = Depends(get_unit_of_work)):
            with uow:
                result = uow.books.create(book)
                uow.commit()
                return result
    """
    return UnitOfWork()
