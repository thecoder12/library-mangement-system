"""Base repository with common CRUD operations."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Type

from sqlalchemy.orm import Session

from app.database import Base


T = TypeVar("T")  # Domain entity type
M = TypeVar("M", bound=Base)  # ORM model type


class BaseRepository(ABC, Generic[T, M]):
    """Abstract base repository with common operations."""
    
    def __init__(self, session: Session, model_class: Type[M]):
        self._session = session
        self._model_class = model_class
    
    @abstractmethod
    def _to_entity(self, model: M) -> T:
        """Convert ORM model to domain entity."""
        pass
    
    @abstractmethod
    def _to_model(self, entity: T) -> M:
        """Convert domain entity to ORM model."""
        pass
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        model = self._session.query(self._model_class).filter(
            self._model_class.id == id
        ).first()
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        models = self._session.query(self._model_class).all()
        return [self._to_entity(m) for m in models]
    
    def delete_by_id(self, id: int) -> bool:
        """Delete entity by ID. Returns True if deleted, False if not found."""
        model = self._session.query(self._model_class).filter(
            self._model_class.id == id
        ).first()
        if model:
            self._session.delete(model)
            return True
        return False
    
    def exists(self, id: int) -> bool:
        """Check if entity exists by ID."""
        return self._session.query(
            self._session.query(self._model_class).filter(
                self._model_class.id == id
            ).exists()
        ).scalar()
    
    def count(self) -> int:
        """Get total count of entities."""
        return self._session.query(self._model_class).count()
