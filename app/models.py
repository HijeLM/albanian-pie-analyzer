from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, nullable=False, index=True)
    normalized = Column(String, nullable=False, index=True)
    language = Column(String, default="sq")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    entries = relationship("Entry", back_populates="word")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    year = Column(Integer)
    author = Column(String)
    reliability_weight = Column(Float, default=1.0)

    entries = relationship("Entry", back_populates="source")


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    root = Column(String)
    meaning = Column(Text)
    part_of_speech = Column(String)
    notes = Column(Text)
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    word = relationship("Word", back_populates="entries")
    source = relationship("Source", back_populates="entries")
    cognates = relationship("Cognate", back_populates="entry")
    evolutions = relationship("Evolution", back_populates="entry")


class Cognate(Base):
    __tablename__ = "cognates"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"), nullable=False)
    language = Column(String, nullable=False)
    word = Column(String, nullable=False)
    meaning = Column(String)

    entry = relationship("Entry", back_populates="cognates")


class Evolution(Base):
    __tablename__ = "evolutions"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"), nullable=False)
    stage = Column(String, nullable=False)  # PIE, Proto-Albanian, Old Albanian, Albanian
    form = Column(String, nullable=False)

    entry = relationship("Entry", back_populates="evolutions")
