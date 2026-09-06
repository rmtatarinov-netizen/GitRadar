import enum
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, JSON, Boolean, Text, Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Maturity(enum.Enum):
    EARLY = "early"
    BETA = "beta"
    STABLE = "stable"

class Category(enum.Enum):
    AGENT_FRAMEWORK = "agent_framework"
    MCP_SERVER = "mcp_server"
    RAG = "rag"
    TOOL_UTILITY = "tool_utility"
    MODEL_WRAPPER = "model_wrapper"
    MONITORING_EVAL = "monitoring_eval"
    DEPLOY_INFRA = "deploy_infra"
    OTHER = "other"

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    source: Mapped[str] = mapped_column(String, default="github")
    repo_name: Mapped[str] = mapped_column(String)
    repo_url: Mapped[str] = mapped_column(String, unique=True, index=True)
    owner_login: Mapped[str] = mapped_column(String)
    owner_type: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String, index=True)
    topics: Mapped[List[str]] = mapped_column(JSON)
    stars: Mapped[int] = mapped_column(Integer, index=True)
    forks: Mapped[int] = mapped_column(Integer)
    watchers: Mapped[int] = mapped_column(Integer)
    license: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    pushed_at: Mapped[datetime] = mapped_column(DateTime)
    category: Mapped[Category] = mapped_column(String, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String)
    agent_relevance_score: Mapped[int] = mapped_column(Integer, index=True)
    maturity: Mapped[Maturity] = mapped_column(String)
    has_examples: Mapped[bool] = mapped_column(Boolean, default=False)
    has_tests: Mapped[bool] = mapped_column(Boolean, default=False)
    has_cli: Mapped[bool] = mapped_column(Boolean, default=False)
    has_sdk: Mapped[bool] = mapped_column(Boolean, default=False)
    has_api: Mapped[bool] = mapped_column(Boolean, default=False)
    integrations: Mapped[List[str]] = mapped_column(JSON)
    dependencies_summary: Mapped[Optional[str]] = mapped_column(Text)
    readme_snippet: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[List[str]] = mapped_column(JSON, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata_extra: Mapped[dict] = mapped_column(JSON, default={})
