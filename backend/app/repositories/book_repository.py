"""Book repository - data access for books."""

from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Book
from app.domain.entities import BookEntity, PaginatedResult
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[BookEntity, Book]):
    """Repository for book data access."""
    
    def __init__(self, session: Session):
        super().__init__(session, Book)
    
    def _to_entity(self, model: Book) -> BookEntity:
        """Convert Book ORM model to BookEntity."""
        return BookEntity(
            id=model.id,
            title=model.title,
            author=model.author,
            isbn=model.isbn,
            published_year=model.published_year,
            genre=model.genre,
            total_copies=model.total_copies,
            available_copies=model.available_copies,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _to_model(self, entity: BookEntity) -> Book:
        """Convert BookEntity to Book ORM model."""
        return Book(
            id=entity.id,
            title=entity.title,
            author=entity.author,
            isbn=entity.isbn,
            published_year=entity.published_year,
            genre=entity.genre,
            total_copies=entity.total_copies,
            available_copies=entity.available_copies,
        )
    
    def create(self, entity: BookEntity) -> BookEntity:
        """Create a new book."""
        model = Book(
            title=entity.title,
            author=entity.author,
            isbn=entity.isbn,
            published_year=entity.published_year,
            genre=entity.genre,
            total_copies=entity.total_copies,
            available_copies=entity.available_copies,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def update(self, id: int, **kwargs) -> Optional[BookEntity]:
        """Update a book by ID with the provided fields."""
        model = self._session.query(Book).filter(Book.id == id).first()
        if not model:
            return None
        
        # Handle total_copies specially to adjust available_copies
        if "total_copies" in kwargs and kwargs["total_copies"] is not None:
            diff = kwargs["total_copies"] - model.total_copies
            model.available_copies = max(0, model.available_copies + diff)
        
        for key, value in kwargs.items():
            if value is not None and hasattr(model, key) and key != "id":
                setattr(model, key, value)
        
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def get_by_isbn(self, isbn: str) -> Optional[BookEntity]:
        """Get book by ISBN."""
        model = self._session.query(Book).filter(Book.isbn == isbn).first()
        return self._to_entity(model) if model else None
    
    def isbn_exists(self, isbn: str, exclude_id: Optional[int] = None) -> bool:
        """Check if ISBN already exists (optionally excluding a specific book)."""
        query = self._session.query(Book).filter(Book.isbn == isbn)
        if exclude_id:
            query = query.filter(Book.id != exclude_id)
        return query.first() is not None
    
    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResult[BookEntity]:
        """List books with pagination and optional search."""
        query = self._session.query(Book)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(Book.title.ilike(search_term), Book.author.ilike(search_term))
            )
        
        total_count = query.count()
        offset = (page - 1) * page_size
        models = query.order_by(Book.id).offset(offset).limit(page_size).all()
        
        return PaginatedResult(
            items=[self._to_entity(m) for m in models],
            total_count=total_count,
            page=page,
            page_size=page_size,
        )
    
    def decrease_available_copies(self, book_id: int) -> bool:
        """Decrease available copies by 1. Returns False if no copies available."""
        model = self._session.query(Book).filter(Book.id == book_id).first()
        if not model or model.available_copies <= 0:
            return False
        model.available_copies -= 1
        return True
    
    def increase_available_copies(self, book_id: int) -> bool:
        """Increase available copies by 1."""
        model = self._session.query(Book).filter(Book.id == book_id).first()
        if not model:
            return False
        model.available_copies = min(model.available_copies + 1, model.total_copies)
        return True
