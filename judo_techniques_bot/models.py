from db import Base, session_scope
from sqlalchemy import Column, Identity
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import Boolean, DateTime, Integer, String


class Technique(Base):
    __tablename__ = "techniques"
    id = Column(Integer, Identity(), primary_key=True)
    japanese_display_name = Column(String, unique=True)
    japanese_names = Column(postgresql.ARRAY(String), default=[])
    english_names = Column(postgresql.ARRAY(String), default=[])
    video_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationships
    mention_events = relationship(
        "DetectedJudoTechniqueMentionEvent",
        back_populates="techniques",
        cascade="all, delete",
        passive_deletes=True,
    )

    # human readable representation
    def __repr__(self):
        return "<Technique(id='{}', japanese_display_name='{}', video_url={})>".format(
            self.id, self.japanese_display_name, self.video_url
        )

    @staticmethod
    def get_cached_techniques():
        dictionary_of_techniques = {}
        with session_scope() as s:
            for tech in s.query(Technique).all():
                for japanese_name in tech.japanese_names:
                    dictionary_of_techniques[japanese_name] = {
                        "id": tech.id,
                        "japanese_display_name": tech.japanese_display_name,
                        "english_names": tech.english_names,
                        "video_url": tech.video_url,
                    }

        return dictionary_of_techniques


class DetectedJudoTechniqueMentionEvent(Base):
    __tablename__ = "mention_events"
    id = Column(Integer, Identity(), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    technique_id = Column(Integer, ForeignKey("techniques.id", ondelete="CASCADE"))
    name_variant = Column(String)
    author = Column(String)
    comment_url = Column(String)
    translated = Column(Boolean)  # True if there was a reply with the translation

    # relationships
    techniques = relationship("Technique", back_populates="mention_events")

    # human readable representation
    def __repr__(self):
        return "<DetectedJudoTechniqueMentionEvent(datetime='{}', technique='{}', author={}, translated={})>".format(
            self.datetime, self.technique, self.author, self.translated
        )
