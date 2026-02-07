"""SQLAlchemy ORM models for the library database."""

from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


class Book(Base):
    """Book model representing library books."""
    
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, index=True)
    published_year = Column(Integer)
    genre = Column(String(100))
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrow_records = relationship("BorrowRecord", back_populates="book")
    
    __table_args__ = (
        CheckConstraint('total_copies >= 0', name='positive_copies'),
        CheckConstraint('available_copies >= 0 AND available_copies <= total_copies', 
                       name='available_not_exceed_total'),
    )
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"


class Member(Base):
    """Member model representing library members."""
    
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    address = Column(Text)
    membership_date = Column(Date, default=date.today)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    borrow_records = relationship("BorrowRecord", back_populates="member")
    
    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', email='{self.email}')>"


class BorrowRecord(Base):
    """BorrowRecord model representing book borrowing transactions."""
    
    __tablename__ = "borrow_records"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    borrow_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    status = Column(String(20), nullable=False, default="BORROWED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    book = relationship("Book", back_populates="borrow_records")
    member = relationship("Member", back_populates="borrow_records")
    
    __table_args__ = (
        CheckConstraint("status IN ('BORROWED', 'RETURNED')", name='valid_status'),
        CheckConstraint('due_date >= borrow_date', name='valid_dates'),
    )
    
    def __repr__(self):
        return f"<BorrowRecord(id={self.id}, book_id={self.book_id}, member_id={self.member_id}, status='{self.status}')>"
