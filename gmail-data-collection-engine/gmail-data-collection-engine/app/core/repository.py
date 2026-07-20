from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        query = self.db.query(func.count(self.model.id))
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.scalar() or 0

    def exists(self, id: Any) -> bool:
        return self.db.query(self.model).filter(self.model.id == id).first() is not None

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any, soft_delete: bool = False) -> bool:
        db_obj = self.get(id)
        if not db_obj:
            return False
        if soft_delete and hasattr(db_obj, "is_active"):
            setattr(db_obj, "is_active", False)
            if hasattr(db_obj, "deleted_at"):
                import datetime
                setattr(db_obj, "deleted_at", datetime.datetime.now(datetime.timezone.utc))
            self.db.commit()
        elif soft_delete and hasattr(db_obj, "record_status"):
            setattr(db_obj, "record_status", "deleted")
            self.db.commit()
        else:
            self.db.delete(db_obj)
            self.db.commit()
        return True

    def bulk_create(self, objects_in: List[CreateSchemaType]) -> List[ModelType]:
        db_objs = [self.model(**obj.model_dump()) for obj in objects_in]
        self.db.bulk_save_objects(db_objs, return_defaults=True)
        self.db.commit()
        return db_objs
