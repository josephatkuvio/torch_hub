import imagehash

from typing import ClassVar, List, Optional
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, func, Table, Boolean, Column
from sqlalchemy.orm import Mapped, relationship, mapped_column
from torch_web import Base
from flask_security import RoleMixin, UserMixin
from io import BytesIO
     

class Institution(Base):
    __tablename__ = "institution"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(150))
    code = mapped_column(String(10))
    created_date = mapped_column(DateTime(timezone=True), default=func.now())    
    deleted_date = mapped_column(DateTime(timezone=True), nullable=True)
    collections = relationship("Collection")
    users: Mapped[List["User"]] = relationship(back_populates="institution")


class Collection(Base):
    __tablename__ = "collection"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(150))
    code = mapped_column(String(10))
    deleted_date = mapped_column(DateTime(timezone=True), nullable=True)
    institution_id = mapped_column(Integer, ForeignKey("institution.id"))
    tasks: Mapped[List["CollectionTask"]] = relationship("CollectionTask", back_populates="collection", lazy="selectin")
    specimens: Mapped[List["Specimen"]] = relationship("Specimen", back_populates="collection")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class CollectionTask(Base):
    __tablename__ = "collection_tasks"
    id = mapped_column(Integer, primary_key=True)
    collection_id = mapped_column(Integer, ForeignKey("collection.id"))
    func_name = mapped_column(String(50))
    name = mapped_column(String(100))
    sort_order = mapped_column(Integer())
    description = mapped_column(String())
    collection: Mapped["Collection"] = relationship("Collection", back_populates="tasks")
    parameters: Mapped[List["CollectionTaskParameter"]] = relationship("CollectionTaskParameter", back_populates="task", lazy="selectin")

    def parameters_dict(self):
        return { p.name: p.value for p in self.parameters }


class CollectionTaskParameter(Base):
    __tablename__ = "collection_tasks_parameters"
    id = mapped_column(Integer, primary_key=True)
    collection_task_id = mapped_column(Integer, ForeignKey("collection_tasks.id"))
    name = mapped_column(String())
    value = mapped_column(String())
    task: Mapped["CollectionTask"] = relationship("CollectionTask", back_populates="parameters")


class Specimen(Base):
    __tablename__ = "specimen"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(150))
    create_date = mapped_column(DateTime(timezone=True), default=func.now())
    upload_path = mapped_column(Text)
    barcode = mapped_column(String(20))
    collection_id = mapped_column(Integer, ForeignKey("collection.id"))
    catalog_number = mapped_column(String(150))
    flow_run_id = mapped_column(String(150))
    flow_run_state = mapped_column(String(150))
    failed_task = mapped_column(String(150))
    deleted = mapped_column(Integer, default=0)
    has_dng = mapped_column(Integer, default=0)
    images: Mapped[List["SpecimenImage"]] = relationship("SpecimenImage", back_populates="specimen", lazy="selectin")
    tasks: Mapped[List["SpecimenTask"]] = relationship("SpecimenTask", back_populates="specimen")
    collection: Mapped["Collection"] = relationship("Collection", back_populates="specimens")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def card_image(self):
        if self.images is None or len(self.images) == 0:
            return None;

        sorted_images = sorted(self.images, key=lambda x: x.width or 100000)
        return sorted_images[0]
    
    def image_bytes(self):
        for img in self.images:
            if img.size == 'FULL':
                return img.image_bytes
        
        return None


class SpecimenTask(Base):
    __tablename__ = "specimen_tasks"
    id = mapped_column(Integer, primary_key=True)
    specimen_id = mapped_column(Integer, ForeignKey("specimen.id"))
    func_name = mapped_column(String())
    name = mapped_column(String())
    sort_order = mapped_column(Integer())
    description = mapped_column(String())
    batch_id = mapped_column(String())
    start_date = mapped_column(DateTime(timezone=True), default=func.now())
    end_date = mapped_column(DateTime(timezone=True))
    run_state = mapped_column(String())
    run_message = mapped_column(String())
    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="tasks")
    parameters: Mapped[List["SpecimenTaskParameter"]] = relationship("SpecimenTaskParameter", back_populates="task", lazy="selectin")


class SpecimenTaskParameter(Base):
    __tablename__ = "specimen_tasks_parameters"
    id = mapped_column(Integer, primary_key=True)
    specimen_task_id = mapped_column(Integer, ForeignKey("specimen_tasks.id"))
    name = mapped_column(String())
    value = mapped_column(String())
    task: Mapped["SpecimenTask"] = relationship("SpecimenTask", back_populates="parameters")


class SpecimenImage(Base):
    __tablename__ = "specimenimage"
    id = mapped_column(Integer, primary_key=True)
    size = mapped_column(String(20))
    height = mapped_column(Integer)
    width = mapped_column(Integer)
    url = mapped_column(Text)
    create_date = mapped_column(DateTime(timezone=True), default=func.now())
    specimen_id = mapped_column(Integer, ForeignKey("specimen.id"))
    specimen: Mapped["Specimen"] = relationship("Specimen", back_populates="images")
    external_url = mapped_column(Text)
    hash_a = mapped_column(String(16))
    hash_b = mapped_column(String(16))
    hash_c = mapped_column(String(16))
    hash_d = mapped_column(String(16))
    image_bytes: ClassVar[Optional[BytesIO]] = None
   
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def average_hash(self):
        return imagehash.hex_to_hash(f'{self.hash_a}{self.hash_b}{self.hash_c}{self.hash_d}')


roles_users = Table(
    "roles_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("role_id", Integer, ForeignKey("role.id")),
)


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(80), unique=True)
    description = mapped_column(String(255))


class User(Base, UserMixin):
    __tablename__ = "user"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(150), unique=True)
    password = mapped_column(String(150))
    first_name = mapped_column(String(150))
    last_name = mapped_column(String(150))
    active = mapped_column(Boolean)
    confirmed_at = mapped_column(DateTime)
    institution_id = mapped_column(Integer, ForeignKey("institution.id"))
    institution = relationship("Institution", back_populates="users")
    fs_uniquifier = mapped_column(String(255), unique=True, nullable=False)
    roles: Mapped[List[Role]] = relationship(secondary=roles_users)

    

class CollectionUser(Base):
    __tablename__ = "collection_users"
    id = mapped_column(Integer, primary_key=True)
    collection_id = mapped_column(Integer, ForeignKey("collection.id"))
    user_id = mapped_column(Integer, ForeignKey("user.id"))
    role = mapped_column(String(50))
    date_added = mapped_column(DateTime(timezone=True), default=func.now())