"""Member repository - data access for members."""

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Member
from app.domain.entities import MemberEntity, PaginatedResult
from app.repositories.base import BaseRepository


class MemberRepository(BaseRepository[MemberEntity, Member]):
    """Repository for member data access."""
    
    def __init__(self, session: Session):
        super().__init__(session, Member)
    
    def _to_entity(self, model: Member) -> MemberEntity:
        """Convert Member ORM model to MemberEntity."""
        return MemberEntity(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            address=model.address,
            membership_date=model.membership_date,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def _to_model(self, entity: MemberEntity) -> Member:
        """Convert MemberEntity to Member ORM model."""
        return Member(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            address=entity.address,
            membership_date=entity.membership_date,
            is_active=entity.is_active,
        )
    
    def create(self, entity: MemberEntity) -> MemberEntity:
        """Create a new member."""
        model = Member(
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            address=entity.address,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def update(self, id: int, **kwargs) -> Optional[MemberEntity]:
        """Update a member by ID with the provided fields."""
        model = self._session.query(Member).filter(Member.id == id).first()
        if not model:
            return None
        
        for key, value in kwargs.items():
            if hasattr(model, key) and key != "id":
                # Allow setting is_active to False explicitly
                if key == "is_active" or value is not None:
                    setattr(model, key, value)
        
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)
    
    def get_by_email(self, email: str) -> Optional[MemberEntity]:
        """Get member by email."""
        model = self._session.query(Member).filter(Member.email == email).first()
        return self._to_entity(model) if model else None
    
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email already exists (optionally excluding a specific member)."""
        query = self._session.query(Member).filter(Member.email == email)
        if exclude_id:
            query = query.filter(Member.id != exclude_id)
        return query.first() is not None
    
    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> PaginatedResult[MemberEntity]:
        """List members with pagination and optional search."""
        query = self._session.query(Member)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(Member.name.ilike(search_term), Member.email.ilike(search_term))
            )
        
        total_count = query.count()
        offset = (page - 1) * page_size
        models = query.order_by(Member.id).offset(offset).limit(page_size).all()
        
        return PaginatedResult(
            items=[self._to_entity(m) for m in models],
            total_count=total_count,
            page=page,
            page_size=page_size,
        )
