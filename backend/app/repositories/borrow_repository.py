"""Borrow repository - data access for borrow records."""

from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models import BorrowRecord, Book, Member
from app.domain.entities import BorrowRecordEntity, BookEntity, MemberEntity, PaginatedResult
from app.repositories.base import BaseRepository


class BorrowRepository(BaseRepository[BorrowRecordEntity, BorrowRecord]):
    """Repository for borrow record data access."""
    
    def __init__(self, session: Session):
        super().__init__(session, BorrowRecord)
    
    def _to_entity(self, model: BorrowRecord, include_relations: bool = True) -> BorrowRecordEntity:
        """Convert BorrowRecord ORM model to BorrowRecordEntity."""
        entity = BorrowRecordEntity(
            id=model.id,
            book_id=model.book_id,
            member_id=model.member_id,
            borrow_date=model.borrow_date,
            due_date=model.due_date,
            return_date=model.return_date,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        
        if include_relations:
            if model.book:
                entity.book = BookEntity(
                    id=model.book.id,
                    title=model.book.title,
                    author=model.book.author,
                    isbn=model.book.isbn,
                    published_year=model.book.published_year,
                    genre=model.book.genre,
                    total_copies=model.book.total_copies,
                    available_copies=model.book.available_copies,
                    created_at=model.book.created_at,
                    updated_at=model.book.updated_at,
                )
            if model.member:
                entity.member = MemberEntity(
                    id=model.member.id,
                    name=model.member.name,
                    email=model.member.email,
                    phone=model.member.phone,
                    address=model.member.address,
                    membership_date=model.member.membership_date,
                    is_active=model.member.is_active,
                    created_at=model.member.created_at,
                    updated_at=model.member.updated_at,
                )
        
        return entity
    
    def _to_model(self, entity: BorrowRecordEntity) -> BorrowRecord:
        """Convert BorrowRecordEntity to BorrowRecord ORM model."""
        return BorrowRecord(
            id=entity.id,
            book_id=entity.book_id,
            member_id=entity.member_id,
            borrow_date=entity.borrow_date,
            due_date=entity.due_date,
            return_date=entity.return_date,
            status=entity.status,
        )
    
    def create(self, entity: BorrowRecordEntity) -> BorrowRecordEntity:
        """Create a new borrow record."""
        model = BorrowRecord(
            book_id=entity.book_id,
            member_id=entity.member_id,
            borrow_date=entity.borrow_date,
            due_date=entity.due_date,
            status=entity.status,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def mark_returned(self, id: int, return_date: date = None) -> Optional[BorrowRecordEntity]:
        """Mark a borrow record as returned."""
        model = self._session.query(BorrowRecord).filter(BorrowRecord.id == id).first()
        if not model:
            return None
        
        model.return_date = return_date or date.today()
        model.status = "RETURNED"
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def get_active_borrows_count(self, member_id: int) -> int:
        """Get count of active borrows for a member."""
        return self._session.query(BorrowRecord).filter(
            BorrowRecord.member_id == member_id,
            BorrowRecord.status == "BORROWED"
        ).count()
    
    def get_total_borrows_count(self, member_id: int) -> int:
        """Get total count of all borrow records (active + returned) for a member."""
        return self._session.query(BorrowRecord).filter(
            BorrowRecord.member_id == member_id
        ).count()
    
    def get_total_borrows_count_for_book(self, book_id: int) -> int:
        """Get total count of all borrow records (active + returned) for a book."""
        return self._session.query(BorrowRecord).filter(
            BorrowRecord.book_id == book_id
        ).count()
    
    def get_active_borrows_for_book(self, book_id: int) -> int:
        """Get count of active borrows for a book."""
        return self._session.query(BorrowRecord).filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.status == "BORROWED"
        ).count()
    
    def has_active_borrow(self, book_id: int, member_id: int) -> bool:
        """Check if member has an active borrow for this book."""
        return self._session.query(BorrowRecord).filter(
            BorrowRecord.book_id == book_id,
            BorrowRecord.member_id == member_id,
            BorrowRecord.status == "BORROWED"
        ).first() is not None
    
    def get_member_active_borrows(self, member_id: int) -> List[BorrowRecordEntity]:
        """Get all active borrows for a member."""
        models = self._session.query(BorrowRecord).filter(
            BorrowRecord.member_id == member_id,
            BorrowRecord.status == "BORROWED"
        ).all()
        return [self._to_entity(m) for m in models]
    
    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        member_id: Optional[int] = None,
        book_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedResult[BorrowRecordEntity]:
        """List borrow records with pagination and optional filters."""
        query = self._session.query(BorrowRecord)
        
        if member_id:
            query = query.filter(BorrowRecord.member_id == member_id)
        if book_id:
            query = query.filter(BorrowRecord.book_id == book_id)
        if status:
            query = query.filter(BorrowRecord.status == status)
        
        # Search by book title/author or member name/email
        if search:
            search_pattern = f"%{search}%"
            query = query.join(Book, BorrowRecord.book_id == Book.id, isouter=True)\
                         .join(Member, BorrowRecord.member_id == Member.id, isouter=True)\
                         .filter(
                             (Book.title.ilike(search_pattern)) |
                             (Book.author.ilike(search_pattern)) |
                             (Member.name.ilike(search_pattern)) |
                             (Member.email.ilike(search_pattern))
                         )
        
        total_count = query.count()
        offset = (page - 1) * page_size
        models = query.order_by(BorrowRecord.id.desc()).offset(offset).limit(page_size).all()
        
        return PaginatedResult(
            items=[self._to_entity(m) for m in models],
            total_count=total_count,
            page=page,
            page_size=page_size,
        )
