# 🤖 COMPREHENSIVE DEVELOPMENT PLAN FOR AI CODING AGENTS
# UHelper - University Admission Assistant

**Document Version**: 2.0  
**Target Audience**: AI Coding Agents  
**Last Updated**: 2026-01-24  
**Project Timeline**: 12 weeks (84 days)  
**Completion Target**: April 2026

---

## 📌 EXECUTIVE SUMMARY

This document provides a comprehensive, actionable development plan for AI coding agents working on UHelper. Unlike previous plans that focus only on current code state, this plan addresses:

1. **Past Architecture Mistakes** - What went wrong and how to fix it
2. **Complete System Evolution** - From MVP to production-ready platform
3. **Missing Critical Features** - Crawlers, data pipelines, marketing systems
4. **Real-World Integration** - Actual university APIs, admission portals
5. **Production Concerns** - Security, scalability, monitoring, deployment

---

## 🚨 CRITICAL ISSUES FROM PAST DEVELOPMENT

### Issue #1: API Configuration Inconsistency
**Problem**: Code uses OpenAI's `ChatOpenAI` class but documentation mentions Claude/Anthropic API.

**Current Broken Code** (`src/agents/orchestrator.py:15-20`):
```python
self.llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # ❌ Wrong for Anthropic
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    max_tokens=100
)
```

**Root Cause**: Confusion between OpenAI-compatible APIs vs actual OpenAI API  
**Impact**: Bot cannot start without correct API configuration  
**Priority**: 🔴 CRITICAL - Must fix before any other work

**Fix Required**:
1. Choose ONE API provider (OpenAI or Anthropic/Claude)
2. Update ALL agent initialization code
3. Create proper `.env.example` with correct variables
4. Add API validation on startup
5. Document the choice in README and AGENTS.md

### Issue #2: Code Style Violations Against Project Rules
**Problem**: Multiple violations of established coding standards

**Violations Found**:
1. **Emojis in UI text** (Rule: No emojis in user-facing text)
   - Location: `src/bot.py:34-48, 100-113`
   - Fix: Remove ALL emojis from messages

2. **Raw dictionaries** (Rule: Only Pydantic models)
   - Location: `src/bot.py:58-63`
   - Fix: Create `UserSession` Pydantic model

3. **Empty try-except** (Rule: Proper error logging)
   - Location: `src/bot.py:93-96`
   - Fix: Implement structured logging with proper error handling

4. **Missing docstrings** (Rule: Google-style docs for all methods)
   - Location: Most methods across all files
   - Fix: Add comprehensive docstrings

5. **AI references in text** (Rule: No AI mentions)
   - Location: Multiple bot messages
   - Fix: Change "AI-ассистент" to just "ассистент" or "помощник"

### Issue #3: Missing Essential Configuration Files
**Problem**: No `.env.example`, `.gitignore`, or proper config management

**Missing Files**:
- `.env.example` - Template for environment variables
- `.gitignore` - Prevent committing secrets
- `config.py` - Centralized configuration management
- `logging_config.py` - Structured logging setup

**Impact**: 
- Risk of committing API keys to Git
- Inconsistent configuration across environments
- No proper logging for debugging

### Issue #4: No Data Persistence
**Problem**: All data stored in-memory dictionaries, lost on restart

**Current State**: `self.user_sessions = {}` in `bot.py:22`  
**Impact**: 
- Users lose all progress on bot restart
- Cannot track historical data
- No analytics or reporting possible

**Required**:
- Database schema design
- SQLite for development
- PostgreSQL for production
- Migration system (Alembic)
- Data models with SQLAlchemy/Pydantic

### Issue #5: No Testing Infrastructure
**Problem**: `test_project.py` only checks file existence, not actual functionality

**Missing**:
- Unit tests for agents
- Integration tests for bot flow
- Mocking for AI API calls
- Test fixtures and factories
- Coverage reporting
- CI/CD test automation

---

## 🎯 PROJECT VISION & SCOPE EXPANSION

### Current Scope (What Exists)
- ✅ Basic Telegram bot with 3 agents
- ✅ Static database of 10 Russian universities
- ✅ Simple intent detection
- ✅ Profile analysis via AI

### Expanded Scope (What's Missing)
This plan adds critical missing features:

#### 1. **Data Collection Infrastructure** 🆕
- Web crawlers for university websites
- Scrapers for admission portals (ГОС услуги, university sites)
- APIs for real-time deadline tracking
- Social media monitoring for university news
- Alumni feedback collection system

#### 2. **Marketing & Growth Systems** 🆕
- Student acquisition funnel
- Referral program ("invite friends")
- School partnership program
- Social media integration
- Analytics and attribution tracking

#### 3. **Advanced AI Features** 🆕
- Multi-agent collaboration (agents working together)
- Memory and context management
- Personalized learning paths
- Predictive analytics for admission chances
- Document generation with templates

#### 4. **Real-World Integrations** 🆕
- University official APIs (where available)
- Government portals integration
- Email/SMS notifications
- Calendar integration (Google Calendar, Apple Calendar)
- Payment systems (for premium features)

#### 5. **Production Infrastructure** 🆕
- Monitoring and alerting
- Automated deployment
- Database backups
- Rate limiting and DDoS protection
- Multi-tenant architecture

---

## 📊 PHASED IMPLEMENTATION PLAN

## **PHASE 0: CRITICAL FIXES (Days 1-7)**
**Goal**: Fix all blocking issues preventing development

### Day 1-2: API Configuration & Environment Setup
**Assignee**: AI Agent with full write access

**Tasks**:
1. **Create `.env.example` file**:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# AI Provider Configuration (Choose ONE)
# Option A: OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Option B: Anthropic Claude
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Database Configuration
DATABASE_URL=sqlite:///./uhelper.db
DATABASE_POOL_SIZE=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/uhelper.log

# Security
SECRET_KEY=your-secret-key-change-in-production
SESSION_TIMEOUT=3600
```

2. **Create `.gitignore` file**:
```gitignore
# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# OS
.DS_Store
Thumbs.db
```

3. **Fix LLM initialization in all agents**:

Create `src/config.py`:
```python
"""Configuration management for UHelper."""
import os
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Telegram
    telegram_bot_token: str = Field(..., description="Telegram Bot API Token")
    
    # AI Provider
    ai_provider: Literal["openai", "anthropic"] = Field(default="openai")
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Database
    database_url: str = "sqlite:///./uhelper.db"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/uhelper.log"
    
    # Security
    secret_key: str = Field(..., description="Secret key for encryption")
    session_timeout: int = 3600


settings = Settings()
```

4. **Create LLM factory** in `src/utils/llm_factory.py`:
```python
"""Factory for creating LLM instances."""
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from src.config import settings


def create_llm(max_tokens: int = 500):
    """Create LLM instance based on configuration.
    
    Args:
        max_tokens: Maximum tokens for response
        
    Returns:
        LLM instance (ChatOpenAI or ChatAnthropic)
        
    Raises:
        ValueError: If API keys are missing or provider is invalid
    """
    if settings.ai_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
            max_tokens=max_tokens,
            temperature=0.7,
        )
    elif settings.ai_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return ChatAnthropic(
            model=settings.anthropic_model,
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=max_tokens,
            temperature=0.7,
        )
    else:
        raise ValueError(f"Unknown AI provider: {settings.ai_provider}")
```

5. **Update all agents to use LLM factory**:
   - `src/agents/orchestrator.py`
   - `src/agents/profile_analyzer_agent.py`

### Day 3-4: Code Style Compliance
**Tasks**:

1. **Remove emojis from all user-facing text**
   - Search for all emoji unicode in `src/bot.py`
   - Replace with plain text
   - Example: "👋 Привет!" → "Здравствуйте!"

2. **Create Pydantic models for all data structures**

Create `src/models/session.py`:
```python
"""Session data models."""
from datetime import datetime
from pydantic import BaseModel, Field


class ConversationEntry(BaseModel):
    """Single conversation entry."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    user_message: str
    agent_name: str
    agent_response: str
    intent: str


class UserSession(BaseModel):
    """User session data."""
    
    user_id: str
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    conversation_history: list[ConversationEntry] = Field(default_factory=list)
    user_profile: dict = Field(default_factory=dict)  # Will be replaced with UserProfile model
    
    def add_message(self, user_msg: str, agent: str, response: str, intent: str):
        """Add a message to conversation history."""
        entry = ConversationEntry(
            user_message=user_msg,
            agent_name=agent,
            agent_response=response,
            intent=intent
        )
        self.conversation_history.append(entry)
        self.last_activity = datetime.now()
```

3. **Replace all dict usage with models** in `src/bot.py:58-63`

4. **Add proper logging**

Create `src/utils/logging_config.py`:
```python
"""Logging configuration."""
import logging
import sys
from pathlib import Path
from src.config import settings


def setup_logging():
    """Configure application logging."""
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
```

5. **Update error handling** in all files:
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await self.orchestrator.process(agent_message)
except Exception as e:
    logger.error(f"Error processing message from user {user.id}: {e}", exc_info=True)
    await message.answer("Извините, произошла ошибка. Попробуйте позже или свяжитесь с поддержкой.")
    return
```

### Day 5-6: Add Comprehensive Docstrings
**Tasks**:

1. **Add docstrings to all classes and methods** following Google style:

Example for `src/agents/base_agent.py`:
```python
class BaseAgent(ABC):
    """Base class for all AI agents.
    
    This abstract class defines the interface that all specialized agents
    must implement. Each agent should handle specific types of user intents
    and provide appropriate responses.
    
    Attributes:
        name: The name of the agent class
    """

    @abstractmethod
    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        """Process a user message and generate a response.
        
        Args:
            message: The incoming message with user intent and context
            
        Returns:
            BaseAgentMessage with agent_response populated
            
        Raises:
            ValueError: If message format is invalid
            RuntimeError: If agent processing fails
        """
        pass

    @abstractmethod
    def can_handle(self, intent: str) -> bool:
        """Check if this agent can handle the given intent.
        
        Args:
            intent: The user intent to check
            
        Returns:
            True if this agent can handle the intent, False otherwise
        """
        pass
```

2. **Run docstring linter**: `pydocstyle src/`

### Day 7: Testing & Validation
**Tasks**:

1. **Test bot startup** with new configuration
2. **Verify all imports** work correctly
3. **Test basic conversation** flow
4. **Run linters**: `ruff check src/` and `mypy src/`
5. **Fix any remaining issues**

**Deliverables**:
- ✅ Working `.env.example` file
- ✅ Proper `.gitignore`
- ✅ Fixed API configuration
- ✅ All code style violations fixed
- ✅ Comprehensive docstrings
- ✅ Structured logging
- ✅ No emoji or AI references in UI

---

## **PHASE 1: DATABASE & PERSISTENCE (Days 8-14)**
**Goal**: Add proper data persistence layer

### Day 8-9: Database Schema Design

**Tasks**:

1. **Install dependencies**:
```bash
uv add sqlalchemy alembic asyncpg psycopg2-binary
```

2. **Create database schema** in `src/models/database.py`:

```python
"""Database models using SQLAlchemy."""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """User account information."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    profile: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False)
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    messages: Mapped[list["Message"]] = relationship(back_populates="user")


class StudentProfile(Base):
    """Student academic profile and preferences."""
    
    __tablename__ = "student_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    
    # Academic info
    current_grade: Mapped[int | None] = mapped_column(Integer)  # 9, 10, 11
    grades: Mapped[dict] = mapped_column(JSON, default=dict)  # {subject: grade}
    test_scores: Mapped[dict] = mapped_column(JSON, default=dict)  # {test_name: score}
    
    # Interests and preferences
    interests: Mapped[list] = mapped_column(JSON, default=list)
    career_goals: Mapped[str | None] = mapped_column(Text)
    preferred_cities: Mapped[list] = mapped_column(JSON, default=list)
    preferred_fields: Mapped[list] = mapped_column(JSON, default=list)  # IT, Economics, etc.
    
    # Constraints
    budget_type: Mapped[str | None] = mapped_column(String(20))  # "budget", "paid", "both"
    max_tuition: Mapped[float | None] = mapped_column(Float)
    
    # Extracurricular
    olympiads: Mapped[list] = mapped_column(JSON, default=list)
    competitions: Mapped[list] = mapped_column(JSON, default=list)
    volunteer_work: Mapped[list] = mapped_column(JSON, default=list)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")


class Session(Base):
    """User session tracking."""
    
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(back_populates="session")


class Message(Base):
    """Conversation message history."""
    
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    user_message: Mapped[str] = mapped_column(Text)
    detected_intent: Mapped[str] = mapped_column(String(50))
    agent_name: Mapped[str] = mapped_column(String(100))
    agent_response: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="messages")
    session: Mapped["Session"] = relationship(back_populates="messages")


class University(Base):
    """University information."""
    
    __tablename__ = "universities"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    short_name: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(100), default="Russia")
    
    # URLs
    website: Mapped[str | None] = mapped_column(String(500))
    admission_portal: Mapped[str | None] = mapped_column(String(500))
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    data_source: Mapped[str | None] = mapped_column(String(100))  # "manual", "crawler", "api"
    
    # Relationships
    programs: Mapped[list["Program"]] = relationship(back_populates="university")


class Program(Base):
    """University program (major/specialization)."""
    
    __tablename__ = "programs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    
    name: Mapped[str] = mapped_column(String(200))
    field: Mapped[str] = mapped_column(String(100), index=True)  # IT, Economics, etc.
    degree_level: Mapped[str] = mapped_column(String(50))  # "bachelor", "master", "phd"
    duration_years: Mapped[int | None] = mapped_column(Integer)
    
    # Requirements
    required_subjects: Mapped[list] = mapped_column(JSON, default=list)  # ЕГЭ subjects
    min_score_budget: Mapped[int | None] = mapped_column(Integer)
    min_score_paid: Mapped[int | None] = mapped_column(Integer)
    
    # Costs
    tuition_fee: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="RUB")
    
    # Deadlines
    application_deadline_budget: Mapped[str | None] = mapped_column(String(50))
    application_deadline_paid: Mapped[str | None] = mapped_column(String(50))
    
    # Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationships
    university: Mapped["University"] = relationship(back_populates="programs")


class UserUniversityInterest(Base):
    """Track which universities users are interested in."""
    
    __tablename__ = "user_university_interests"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    program_id: Mapped[int | None] = mapped_column(ForeignKey("programs.id"))
    
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    priority: Mapped[int] = mapped_column(Integer, default=0)  # 1=dream, 2=target, 3=safety
    notes: Mapped[str | None] = mapped_column(Text)
```

3. **Initialize Alembic** for migrations:
```bash
uv run alembic init alembic
```

4. **Configure Alembic** in `alembic/env.py` to use async SQLAlchemy

5. **Create initial migration**:
```bash
uv run alembic revision --autogenerate -m "Initial schema"
uv run alembic upgrade head
```

### Day 10-11: Database Access Layer

**Tasks**:

1. **Create database session manager** in `src/database/session.py`:

```python
"""Database session management."""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config import settings
from src.models.database import Base


# Convert sync URL to async
async_database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")
async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(async_database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_db():
    """Get database session.
    
    Usage:
        async with get_db() as db:
            user = await db.get(User, 1)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

2. **Create repository pattern** in `src/database/repositories/`:

`src/database/repositories/user_repository.py`:
```python
"""User repository for database operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import User, StudentProfile


class UserRepository:
    """Repository for User operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User object or None if not found
        """
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self, 
        telegram_id: str, 
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None
    ) -> User:
        """Create a new user.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User first name
            last_name: User last name
            
        Returns:
            Created User object
        """
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.db.add(user)
        await self.db.flush()
        
        # Create empty profile
        profile = StudentProfile(user_id=user.id)
        self.db.add(profile)
        await self.db.flush()
        
        return user
    
    async def get_or_create_user(self, telegram_id: str, **kwargs) -> User:
        """Get existing user or create new one.
        
        Args:
            telegram_id: Telegram user ID
            **kwargs: Additional user fields
            
        Returns:
            User object
        """
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.create_user(telegram_id, **kwargs)
        return user
```

### Day 12-13: Integrate Database with Bot

**Tasks**:

1. **Update `src/bot.py`** to use database:

```python
from src.database.session import get_db, init_db
from src.database.repositories.user_repository import UserRepository
from src.database.repositories.session_repository import SessionRepository
from src.database.repositories.message_repository import MessageRepository

class UHelperBot:
    """Main bot class with database integration."""
    
    async def initialize(self):
        """Initialize bot and database."""
        await init_db()
        self.initialize_agents()
    
    async def handle_message(self, message: Message):
        """Handle incoming message with database storage."""
        user = message.from_user
        
        async with get_db() as db:
            user_repo = UserRepository(db)
            session_repo = SessionRepository(db)
            message_repo = MessageRepository(db)
            
            # Get or create user
            db_user = await user_repo.get_or_create_user(
                telegram_id=str(user.id),
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            # Get or create session
            db_session = await session_repo.get_or_create_active_session(db_user.id)
            
            # Process message
            agent_message = BaseAgentMessage(
                user_id=str(user.id),
                session_id=db_session.session_id,
                intent="",
                message=message.text,
                context={
                    "user_profile": db_user.profile.__dict__ if db_user.profile else {},
                    "conversation_history": await message_repo.get_recent_messages(
                        db_session.id, limit=10
                    )
                }
            )
            
            try:
                result = await self.orchestrator.process(agent_message)
                
                # Save message to database
                await message_repo.create_message(
                    user_id=db_user.id,
                    session_id=db_session.id,
                    user_message=message.text,
                    detected_intent=result.intent,
                    agent_name=result.agent_response["agent"],
                    agent_response=result.agent_response["response"],
                    confidence=result.agent_response.get("confidence", 0.0)
                )
                
                await message.answer(result.agent_response["response"])
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await message.answer("Извините, произошла ошибка.")
```

2. **Update bot startup** in `main.py`:

```python
async def main():
    """Main function with proper initialization."""
    load_dotenv()
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting UHelper bot...")
    
    bot = UHelperBot()
    await bot.initialize()  # Initialize database
    await bot.run()
```

### Day 14: Migration of Existing Data

**Tasks**:

1. **Migrate hardcoded universities** to database
2. **Create migration script** in `scripts/migrate_universities.py`:

```python
"""Migrate hardcoded universities to database."""
import asyncio
from src.database.session import get_db
from src.models.database import University, Program


async def migrate_universities():
    """Migrate universities from code to database."""
    # Import hardcoded data
    from src.agents.university_data_agent import UniversityDataAgent
    
    agent = UniversityDataAgent()
    universities_data = agent.universities
    
    async with get_db() as db:
        for uni_data in universities_data:
            # Create university
            university = University(
                name=uni_data["name"],
                city=uni_data["city"],
                data_source="manual"
            )
            db.add(university)
            await db.flush()
            
            # Create programs
            for program_data in uni_data["program_details"]:
                program = Program(
                    university_id=university.id,
                    name=program_data["name"],
                    required_subjects=program_data["ege_subjects"],
                    min_score_budget=program_data.get("budget_score"),
                    min_score_paid=program_data.get("paid_score"),
                    degree_level="bachelor"
                )
                db.add(program)
            
            await db.flush()
    
    print("Migration complete!")


if __name__ == "__main__":
    asyncio.run(migrate_universities())
```

3. **Run migration**: `uv run python scripts/migrate_universities.py`

4. **Update `UniversityDataAgent`** to query database instead of hardcoded dict

**Deliverables**:
- ✅ Complete database schema
- ✅ Database migrations with Alembic
- ✅ Repository pattern implementation
- ✅ Bot integrated with database
- ✅ Existing data migrated

---

## **PHASE 2: WEB CRAWLERS & DATA COLLECTION (Days 15-28)**
**Goal**: Build automated data collection infrastructure

### Overview
Currently, university data is hardcoded and quickly becomes outdated. We need:
- Web crawlers to extract university information
- Scrapers for admission portals
- Data validation and quality checks
- Automated update schedules

### Day 15-17: Crawler Infrastructure

**Tasks**:

1. **Install scraping dependencies**:
```bash
uv add playwright beautifulsoup4 lxml httpx selectolax
uv run playwright install
```

2. **Create crawler base class** in `src/crawlers/base_crawler.py`:

```python
"""Base crawler for web scraping."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import logging
from playwright.async_api import async_playwright, Browser, Page
import httpx

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Result of a crawl operation."""
    
    url: str
    success: bool
    data: dict
    error: str | None = None
    crawled_at: datetime = None
    
    def __post_init__(self):
        if self.crawled_at is None:
            self.crawled_at = datetime.now()


class BaseCrawler(ABC):
    """Base class for all web crawlers."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        """Initialize crawler.
        
        Args:
            headless: Run browser in headless mode
            timeout: Request timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.browser: Browser | None = None
    
    async def __aenter__(self):
        """Context manager entry."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.browser:
            await self.browser.close()
    
    async def crawl(self, url: str) -> CrawlResult:
        """Crawl a URL and extract data.
        
        Args:
            url: URL to crawl
            
        Returns:
            CrawlResult with extracted data
        """
        try:
            data = await self._extract_data(url)
            return CrawlResult(url=url, success=True, data=data)
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return CrawlResult(url=url, success=False, data={}, error=str(e))
    
    @abstractmethod
    async def _extract_data(self, url: str) -> dict:
        """Extract data from URL.
        
        Args:
            url: URL to extract data from
            
        Returns:
            Extracted data as dictionary
        """
        pass
    
    async def get_page(self, url: str) -> Page:
        """Get a new page and navigate to URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            Playwright Page object
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use 'async with' context.")
        
        page = await self.browser.new_page()
        await page.goto(url, timeout=self.timeout)
        return page
```

3. **Create university website crawler** in `src/crawlers/university_crawler.py`:

```python
"""Crawler for university websites."""
from bs4 import BeautifulSoup
from src.crawlers.base_crawler import BaseCrawler
import logging

logger = logging.getLogger(__name__)


class UniversityCrawler(BaseCrawler):
    """Crawler for extracting university information."""
    
    async def _extract_data(self, url: str) -> dict:
        """Extract university data from website.
        
        Args:
            url: University website URL
            
        Returns:
            Dictionary with university information
        """
        page = await self.get_page(url)
        
        # Wait for content to load
        await page.wait_for_load_state("networkidle")
        
        content = await page.content()
        soup = BeautifulSoup(content, "lxml")
        
        data = {
            "name": await self._extract_name(soup, page),
            "programs": await self._extract_programs(soup, page),
            "admission_info": await self._extract_admission_info(soup, page),
            "contacts": await self._extract_contacts(soup, page),
        }
        
        await page.close()
        return data
    
    async def _extract_name(self, soup: BeautifulSoup, page) -> str:
        """Extract university name."""
        # Try multiple selectors
        selectors = [
            "h1.university-name",
            "h1.main-title",
            "title",
            "h1"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ""
    
    async def _extract_programs(self, soup: BeautifulSoup, page) -> list[dict]:
        """Extract available programs."""
        programs = []
        
        # Common patterns for program listings
        program_containers = soup.select(".program-item, .specialty, .direction")
        
        for container in program_containers:
            program = {
                "name": self._extract_text(container, ".program-name, .title, h3"),
                "code": self._extract_text(container, ".program-code, .code"),
                "duration": self._extract_text(container, ".duration, .years"),
                "degree": self._extract_text(container, ".degree-level, .level"),
            }
            if program["name"]:
                programs.append(program)
        
        return programs
    
    async def _extract_admission_info(self, soup: BeautifulSoup, page) -> dict:
        """Extract admission information."""
        # Look for admission section
        admission_section = soup.select_one("#admission, #postupit, .admission")
        
        if not admission_section:
            return {}
        
        return {
            "requirements": self._extract_text(admission_section, ".requirements"),
            "deadlines": self._extract_text(admission_section, ".deadlines, .dates"),
            "documents": self._extract_list(admission_section, ".documents li, .doc-list li"),
            "exam_subjects": self._extract_list(admission_section, ".exams li, .ege li"),
        }
    
    async def _extract_contacts(self, soup: BeautifulSoup, page) -> dict:
        """Extract contact information."""
        return {
            "email": self._extract_text(soup, "a[href^='mailto:']"),
            "phone": self._extract_text(soup, "a[href^='tel:'], .phone"),
            "address": self._extract_text(soup, ".address, .contacts address"),
        }
    
    @staticmethod
    def _extract_text(container, selector: str) -> str:
        """Extract text from element."""
        element = container.select_one(selector)
        return element.get_text(strip=True) if element else ""
    
    @staticmethod
    def _extract_list(container, selector: str) -> list[str]:
        """Extract list of texts."""
        elements = container.select(selector)
        return [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
```

### Day 18-20: Admission Portal Scrapers

**Tasks**:

1. **Create scraper for госуслуги (government admission portal)**:

`src/crawlers/gosuslugi_scraper.py`:
```python
"""Scraper for government admission portals."""
from src.crawlers.base_crawler import BaseCrawler


class GosUslugiScraper(BaseCrawler):
    """Scraper for госуслуги education section."""
    
    BASE_URL = "https://www.gosuslugi.ru/education"
    
    async def scrape_admission_dates(self, year: int = 2026) -> dict:
        """Scrape admission dates for given year.
        
        Args:
            year: Admission year
            
        Returns:
            Dictionary with admission deadlines
        """
        url = f"{self.BASE_URL}/calendar/{year}"
        page = await self.get_page(url)
        
        # Extract deadlines
        deadlines = {}
        
        # Main application deadline
        main_deadline = await page.query_selector(".deadline-main")
        if main_deadline:
            date_text = await main_deadline.text_content()
            deadlines["main"] = date_text.strip()
        
        # Priority application (for olympiad winners)
        priority_deadline = await page.query_selector(".deadline-priority")
        if priority_deadline:
            date_text = await priority_deadline.text_content()
            deadlines["priority"] = date_text.strip()
        
        await page.close()
        return deadlines
    
    async def scrape_university_stats(self, university_id: str) -> dict:
        """Scrape statistics for specific university.
        
        Args:
            university_id: University identifier in госуслуги
            
        Returns:
            Statistics dictionary
        """
        url = f"{self.BASE_URL}/universities/{university_id}/stats"
        page = await self.get_page(url)
        
        stats = {
            "applications": await self._extract_stat(page, ".stat-applications"),
            "places": await self._extract_stat(page, ".stat-places"),
            "competition": await self._extract_stat(page, ".stat-competition"),
            "min_score": await self._extract_stat(page, ".stat-min-score"),
        }
        
        await page.close()
        return stats
    
    @staticmethod
    async def _extract_stat(page, selector: str) -> str:
        """Extract statistic value."""
        element = await page.query_selector(selector)
        if element:
            return await element.text_content()
        return ""
```

2. **Create crawler manager** in `src/crawlers/crawler_manager.py`:

```python
"""Manager for coordinating all crawlers."""
import asyncio
import logging
from datetime import datetime
from sqlalchemy import select
from src.crawlers.university_crawler import UniversityCrawler
from src.crawlers.gosuslugi_scraper import GosUslugiScraper
from src.database.session import get_db
from src.models.database import University, Program

logger = logging.getLogger(__name__)


class CrawlerManager:
    """Manages all web crawlers and data collection."""
    
    def __init__(self):
        self.university_crawler = UniversityCrawler()
        self.gosuslugi_scraper = GosUslugiScraper()
    
    async def update_all_universities(self):
        """Update information for all universities in database."""
        async with get_db() as db:
            result = await db.execute(
                select(University).where(University.is_active == True)
            )
            universities = result.scalars().all()
            
            logger.info(f"Updating {len(universities)} universities...")
            
            for university in universities:
                if university.website:
                    await self.update_university(university)
                    # Delay to avoid rate limiting
                    await asyncio.sleep(5)
            
            logger.info("University update complete")
    
    async def update_university(self, university: University):
        """Update single university information.
        
        Args:
            university: University database object
        """
        try:
            async with self.university_crawler as crawler:
                result = await crawler.crawl(university.website)
                
                if result.success:
                    # Update university data
                    await self._update_university_data(university, result.data)
                    logger.info(f"Updated {university.name}")
                else:
                    logger.error(f"Failed to update {university.name}: {result.error}")
                    
        except Exception as e:
            logger.error(f"Error updating {university.name}: {e}")
    
    async def _update_university_data(self, university: University, data: dict):
        """Update university database record with crawled data."""
        async with get_db() as db:
            # Update university
            university.last_updated = datetime.now()
            university.data_source = "crawler"
            
            # Update or create programs
            for program_data in data.get("programs", []):
                # Check if program exists
                result = await db.execute(
                    select(Program).where(
                        Program.university_id == university.id,
                        Program.name == program_data["name"]
                    )
                )
                program = result.scalar_one_or_none()
                
                if program:
                    # Update existing
                    program.last_updated = datetime.now()
                else:
                    # Create new
                    program = Program(
                        university_id=university.id,
                        name=program_data["name"],
                        degree_level=program_data.get("degree", "bachelor"),
                        duration_years=self._parse_duration(program_data.get("duration")),
                    )
                    db.add(program)
            
            await db.commit()
    
    @staticmethod
    def _parse_duration(duration_str: str | None) -> int | None:
        """Parse duration string to years."""
        if not duration_str:
            return None
        # Extract numbers from string like "4 года" or "4 years"
        import re
        match = re.search(r"\d+", duration_str)
        return int(match.group()) if match else None
```

### Day 21-23: Data Validation & Quality

**Tasks**:

1. **Create data validation** in `src/crawlers/validators.py`:

```python
"""Data validation for crawled information."""
from pydantic import BaseModel, Field, validator
from datetime import date


class UniversityData(BaseModel):
    """Validated university data."""
    
    name: str = Field(..., min_length=3, max_length=200)
    website: str | None = None
    city: str = Field(..., min_length=2)
    country: str = "Russia"
    
    @validator("website")
    def validate_website(cls, v):
        """Validate website URL."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Website must be a valid URL")
        return v


class ProgramData(BaseModel):
    """Validated program data."""
    
    name: str = Field(..., min_length=3, max_length=200)
    degree_level: str = Field(..., regex="^(bachelor|master|phd)$")
    duration_years: int | None = Field(None, ge=1, le=10)
    min_score_budget: int | None = Field(None, ge=0, le=400)
    min_score_paid: int | None = Field(None, ge=0, le=400)
    required_subjects: list[str] = Field(default_factory=list)
    
    @validator("required_subjects")
    def validate_subjects(cls, v):
        """Validate ЕГЭ subjects."""
        valid_subjects = {
            "Математика", "Русский язык", "Информатика", "Физика",
            "Химия", "Биология", "История", "Обществознание",
            "География", "Литература", "Иностранный язык"
        }
        for subject in v:
            if subject not in valid_subjects:
                raise ValueError(f"Invalid subject: {subject}")
        return v


class AdmissionDeadline(BaseModel):
    """Validated admission deadline."""
    
    deadline_type: str = Field(..., regex="^(main|priority|documents)$")
    date_str: str  # "20 июля" format
    year: int = Field(..., ge=2025, le=2030)
    
    @validator("date_str")
    def validate_date_format(cls, v):
        """Validate Russian date format."""
        # Should be like "20 июля"
        import re
        if not re.match(r"\d{1,2}\s+[а-я]+", v, re.IGNORECASE):
            raise ValueError("Invalid date format")
        return v
```

2. **Add data quality checks** in `src/crawlers/quality_checker.py`:

```python
"""Quality checks for crawled data."""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Performs quality checks on crawled data."""
    
    def check_university_data(self, data: dict) -> tuple[bool, list[str]]:
        """Check university data quality.
        
        Args:
            data: University data dictionary
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check required fields
        if not data.get("name"):
            issues.append("Missing university name")
        
        if not data.get("website"):
            issues.append("Missing website URL")
        
        # Check programs
        programs = data.get("programs", [])
        if not programs:
            issues.append("No programs found")
        elif len(programs) < 3:
            issues.append(f"Only {len(programs)} programs found (might be incomplete)")
        
        # Check for suspicious data
        if data.get("name") and len(data["name"]) < 5:
            issues.append("University name too short")
        
        is_valid = len(issues) == 0
        
        if issues:
            logger.warning(f"Data quality issues: {', '.join(issues)}")
        
        return is_valid, issues
    
    def check_program_data(self, program: dict) -> tuple[bool, list[str]]:
        """Check program data quality."""
        issues = []
        
        if not program.get("name"):
            issues.append("Missing program name")
        
        # Check score ranges
        budget_score = program.get("min_score_budget")
        if budget_score and (budget_score < 100 or budget_score > 400):
            issues.append(f"Suspicious budget score: {budget_score}")
        
        paid_score = program.get("min_score_paid")
        if paid_score and (paid_score < 100 or paid_score > 400):
            issues.append(f"Suspicious paid score: {paid_score}")
        
        # Budget score should be higher than paid
        if budget_score and paid_score and budget_score < paid_score:
            issues.append("Budget score lower than paid score")
        
        return len(issues) == 0, issues
```

### Day 24-26: Crawler Scheduling

**Tasks**:

1. **Install scheduling library**:
```bash
uv add apscheduler
```

2. **Create crawler scheduler** in `src/crawlers/scheduler.py`:

```python
"""Scheduler for automated crawling."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from src.crawlers.crawler_manager import CrawlerManager

logger = logging.getLogger(__name__)


class CrawlerScheduler:
    """Schedules automatic crawling tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.crawler_manager = CrawlerManager()
    
    def start(self):
        """Start the scheduler."""
        # Update all universities daily at 3 AM
        self.scheduler.add_job(
            self.crawler_manager.update_all_universities,
            CronTrigger(hour=3, minute=0),
            id="update_universities",
            name="Update all universities"
        )
        
        # Update госуслуги data weekly on Monday at 2 AM
        self.scheduler.add_job(
            self._update_gosuslugi_data,
            CronTrigger(day_of_week="mon", hour=2, minute=0),
            id="update_gosuslugi",
            name="Update госуслуги data"
        )
        
        self.scheduler.start()
        logger.info("Crawler scheduler started")
    
    async def _update_gosuslugi_data(self):
        """Update data from госуслуги."""
        async with self.crawler_manager.gosuslugi_scraper as scraper:
            # Update admission dates
            deadlines = await scraper.scrape_admission_dates(2026)
            logger.info(f"Updated admission deadlines: {deadlines}")
            
            # Store deadlines in database
            # TODO: Implement deadline storage
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Crawler scheduler stopped")
```

3. **Integrate with bot** in `src/bot.py`:

```python
from src.crawlers.scheduler import CrawlerScheduler

class UHelperBot:
    def __init__(self):
        # ... existing code ...
        self.crawler_scheduler = CrawlerScheduler()
    
    async def run(self):
        """Run bot with crawler scheduler."""
        # Start crawler scheduler
        self.crawler_scheduler.start()
        
        try:
            # Start bot polling
            await self.dp.start_polling(self.bot)
        finally:
            # Stop scheduler on shutdown
            self.crawler_scheduler.stop()
```

### Day 27-28: Testing & Monitoring

**Tasks**:

1. **Create crawler tests** in `tests/crawlers/`:

```python
"""Tests for web crawlers."""
import pytest
from src.crawlers.university_crawler import UniversityCrawler


@pytest.mark.asyncio
async def test_university_crawler():
    """Test university crawler."""
    async with UniversityCrawler() as crawler:
        result = await crawler.crawl("https://www.msu.ru")
        
        assert result.success
        assert result.data["name"]
        assert len(result.data["programs"]) > 0


@pytest.mark.asyncio
async def test_crawler_error_handling():
    """Test crawler handles errors gracefully."""
    async with UniversityCrawler() as crawler:
        result = await crawler.crawl("https://invalid-url-12345.com")
        
        assert not result.success
        assert result.error is not None
```

2. **Add crawler monitoring** to track success rates and performance

3. **Create admin dashboard** to view crawler status (simple Telegram commands)

**Deliverables**:
- ✅ Web crawler infrastructure
- ✅ University website crawler
- ✅ госуслуги scraper
- ✅ Data validation system
- ✅ Automated scheduling
- ✅ Monitoring and tests

---

## **PHASE 3: REMAINING AGENTS (Days 29-56)**
**Goal**: Complete all 8 agents as specified in AGENTS.md

### Day 29-35: TimelineAgent (Week 5)
### Day 36-42: ExamPrepAgent (Week 6)
### Day 43-49: DocumentAgent (Week 7)
### Day 50-56: AssessmentAgent & NotificationAgent (Week 8)

**Note**: See original DEVELOPMENT_PLAN.md for detailed breakdown of these phases.

**Additional Requirements for Each Agent**:

1. **Database models** for agent-specific data
2. **Repository pattern** for data access
3. **Unit tests** with 80%+ coverage
4. **Integration** with orchestrator
5. **API documentation** for agent methods
6. **Error handling** and logging
7. **Performance metrics** collection

---

## **PHASE 4: MARKETING & GROWTH SYSTEMS (Days 57-70)** 🆕
**Goal**: Build systems to acquire and retain users

### Day 57-59: Referral Program

**Tasks**:

1. **Create referral system** in `src/features/referrals.py`:

```python
"""Referral program implementation."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from src.models.database import Base
import secrets


class ReferralCode(Base):
    """User referral codes."""
    
    __tablename__ = "referral_codes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    total_referrals: Mapped[int] = mapped_column(Integer, default=0)


class Referral(Base):
    """Track referrals."""
    
    __tablename__ = "referrals"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    code_used: Mapped[str] = mapped_column(String(20))
    referred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    reward_claimed: Mapped[bool] = mapped_column(Boolean, default=False)


class ReferralManager:
    """Manages referral program."""
    
    @staticmethod
    def generate_code(user_id: int) -> str:
        """Generate unique referral code."""
        return f"UH{user_id:06d}{secrets.token_hex(3).upper()}"
    
    async def create_referral_code(self, user_id: int) -> str:
        """Create referral code for user."""
        code = self.generate_code(user_id)
        
        async with get_db() as db:
            referral_code = ReferralCode(user_id=user_id, code=code)
            db.add(referral_code)
            await db.commit()
        
        return code
    
    async def apply_referral(self, new_user_id: int, code: str) -> bool:
        """Apply referral code when new user joins."""
        async with get_db() as db:
            # Find code
            result = await db.execute(
                select(ReferralCode).where(ReferralCode.code == code)
            )
            ref_code = result.scalar_one_or_none()
            
            if not ref_code:
                return False
            
            # Create referral record
            referral = Referral(
                referrer_id=ref_code.user_id,
                referred_id=new_user_id,
                code_used=code
            )
            db.add(referral)
            
            # Update count
            ref_code.total_referrals += 1
            
            await db.commit()
            return True
```

2. **Add bot commands** for referrals:

```python
@dp.message(Command("invite"))
async def invite_command(message: Message):
    """Generate and share referral link."""
    user_id = message.from_user.id
    
    async with get_db() as db:
        # Get or create referral code
        code = await referral_manager.get_or_create_code(user_id)
        
        referral_link = f"https://t.me/YourBotUsername?start={code}"
        
        await message.answer(
            f"Пригласите друзей и получите бонусы!\n\n"
            f"Ваша реферальная ссылка:\n{referral_link}\n\n"
            f"За каждого друга вы получаете:\n"
            f"• Расширенный анализ профиля\n"
            f"• Приоритетную поддержку\n"
            f"• Доступ к premium функциям"
        )


@dp.message(Command("mystats"))
async def stats_command(message: Message):
    """Show referral statistics."""
    user_id = message.from_user.id
    
    async with get_db() as db:
        stats = await referral_manager.get_stats(user_id)
        
        await message.answer(
            f"Ваша статистика:\n\n"
            f"Приглашено друзей: {stats['total']}\n"
            f"Активных: {stats['active']}\n"
            f"Бонусов получено: {stats['rewards']}"
        )
```

### Day 60-63: School Partnership Program

**Tasks**:

1. **Create partnership models** in `src/models/partnerships.py`:

```python
"""Partnership models for schools."""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from src.models.database import Base


class School(Base):
    """Partner schools."""
    
    __tablename__ = "schools"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="Russia")
    contact_email: Mapped[str | None] = mapped_column(String(200))
    contact_person: Mapped[str | None] = mapped_column(String(200))
    partnership_code: Mapped[str] = mapped_column(String(50), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class SchoolStudent(Base):
    """Track which students are from partner schools."""
    
    __tablename__ = "school_students"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"))
    grade: Mapped[int | None] = mapped_column(Integer)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
```

2. **Create school onboarding flow**:
   - Special `/school` command with partnership code
   - Bulk invitation for teachers to share with students
   - Analytics dashboard for schools to track student progress

3. **Partnership benefits**:
   - Customized university recommendations for school region
   - Group sessions for career counseling
   - Priority support for partner school students

### Day 64-66: Social Media Integration

**Tasks**:

1. **Add sharing functionality**:

```python
@dp.message(Command("share"))
async def share_command(message: Message):
    """Share bot with friends."""
    share_text = (
        "Я использую UHelper для подготовки к поступлению в университет! "
        "Бот помогает выбрать вуз, спланировать подготовку и не пропустить дедлайны. "
        "Попробуйте сами: https://t.me/YourBotUsername"
    )
    
    # Create inline keyboard with share buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться в Telegram", switch_inline_query=share_text)],
        [InlineKeyboardButton(text="Скопировать ссылку", callback_data="copy_link")]
    ])
    
    await message.answer("Поделитесь ботом с друзьями:", reply_markup=keyboard)
```

2. **Create social media templates** for success stories

3. **Track** social media referrals with UTM parameters

### Day 67-70: Analytics & Attribution

**Tasks**:

1. **Add analytics tracking** in `src/analytics/tracker.py`:

```python
"""Analytics tracking."""
from sqlalchemy import Column, String, Integer, DateTime, JSON
from src.models.database import Base


class UserEvent(Base):
    """Track user events for analytics."""
    
    __tablename__ = "user_events"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    event_data: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    
    # Attribution
    source: Mapped[str | None] = mapped_column(String(50))  # "referral", "organic", "school"
    campaign: Mapped[str | None] = mapped_column(String(100))
    

class AnalyticsTracker:
    """Track user analytics."""
    
    async def track_event(
        self, 
        user_id: int, 
        event_type: str, 
        event_data: dict = None,
        source: str = None,
        campaign: str = None
    ):
        """Track an event."""
        async with get_db() as db:
            event = UserEvent(
                user_id=user_id,
                event_type=event_type,
                event_data=event_data or {},
                source=source,
                campaign=campaign
            )
            db.add(event)
            await db.commit()
    
    async def get_funnel_metrics(self, days: int = 30) -> dict:
        """Calculate funnel metrics."""
        # Implement funnel analysis:
        # 1. Bot started
        # 2. Profile created
        # 3. University searched
        # 4. University saved
        # 5. Timeline created
        pass
```

2. **Create analytics dashboard** (simple Telegram admin commands):

```python
@dp.message(Command("analytics"))
async def analytics_command(message: Message):
    """Show analytics (admin only)."""
    if not is_admin(message.from_user.id):
        return
    
    analytics = await tracker.get_summary(days=7)
    
    await message.answer(
        f"Analytics (Last 7 days):\n\n"
        f"New users: {analytics['new_users']}\n"
        f"Active users: {analytics['active_users']}\n"
        f"Total messages: {analytics['messages']}\n"
        f"Referrals: {analytics['referrals']}\n"
        f"Conversion rate: {analytics['conversion_rate']:.1f}%"
    )
```

**Deliverables**:
- ✅ Referral program with rewards
- ✅ School partnership system
- ✅ Social media sharing
- ✅ Analytics and attribution tracking
- ✅ Admin analytics dashboard

---

## **PHASE 5: TESTING & QUALITY (Days 71-77)**
**Goal**: Comprehensive testing infrastructure

### Day 71-73: Unit & Integration Tests

**Tasks**:

1. **Setup pytest properly**:

```bash
uv add --group dev pytest pytest-asyncio pytest-cov pytest-mock faker
```

2. **Create test fixtures** in `tests/conftest.py`:

```python
"""Pytest fixtures."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.database import Base
from src.database.session import get_db
from src.bot import UHelperBot


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    yield async_session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_bot():
    """Create test bot instance."""
    bot = UHelperBot()
    await bot.initialize()
    yield bot
```

3. **Write comprehensive tests**:

`tests/agents/test_orchestrator.py`:
```python
"""Tests for OrchestratorAgent."""
import pytest
from src.agents.orchestrator import OrchestratorAgent
from src.models.base import BaseAgentMessage


@pytest.mark.asyncio
async def test_intent_detection_university_search():
    """Test intent detection for university search."""
    orchestrator = OrchestratorAgent([])
    
    message = "Какие университеты в Москве с IT?"
    intent = await orchestrator._detect_intent(message, {})
    
    assert intent == "university_search"


@pytest.mark.asyncio
async def test_intent_detection_profile_analysis():
    """Test intent detection for profile analysis."""
    orchestrator = OrchestratorAgent([])
    
    message = "Проанализируй мой профиль"
    intent = await orchestrator._detect_intent(message, {})
    
    assert intent == "profile_analysis"
```

4. **Test coverage requirement**: Minimum 80% code coverage

### Day 74-75: End-to-End Testing

**Tasks**:

1. **Create E2E test scenarios**:

```python
"""End-to-end tests."""
import pytest
from src.bot import UHelperBot
from tests.utils.mock_telegram import MockTelegramMessage


@pytest.mark.asyncio
async def test_full_user_journey(test_bot):
    """Test complete user journey."""
    bot = test_bot
    
    # 1. User starts bot
    start_msg = MockTelegramMessage(text="/start", user_id=12345)
    await bot.handle_message(start_msg)
    
    # 2. User searches for universities
    search_msg = MockTelegramMessage(
        text="Какие IT университеты в Москве?",
        user_id=12345
    )
    await bot.handle_message(search_msg)
    
    # 3. User provides profile info
    profile_msg = MockTelegramMessage(
        text="У меня 5 по математике, 4 по физике",
        user_id=12345
    )
    await bot.handle_message(profile_msg)
    
    # Verify database state
    async with get_db() as db:
        user = await db.get(User, telegram_id="12345")
        assert user is not None
        assert len(user.messages) >= 3
```

### Day 76-77: Performance Testing

**Tasks**:

1. **Load testing** with locust:

```python
"""Load tests for bot."""
from locust import User, task, between
import asyncio


class BotUser(User):
    wait_time = between(1, 5)
    
    @task
    def send_message(self):
        """Simulate user sending message."""
        asyncio.run(self.send_test_message())
    
    async def send_test_message(self):
        # Simulate bot interaction
        pass
```

2. **Database performance tests**
3. **AI API call optimization** (caching, batching)

**Deliverables**:
- ✅ 80%+ test coverage
- ✅ All agents tested
- ✅ E2E test scenarios
- ✅ Performance benchmarks
- ✅ CI/CD integration

---

## **PHASE 6: PRODUCTION DEPLOYMENT (Days 78-84)**
**Goal**: Deploy to production with monitoring

### Day 78-80: Infrastructure Setup

**Tasks**:

1. **Choose hosting** (Railway, Fly.io, or DigitalOcean)

2. **Create Dockerfile**:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application
COPY . .

# Run migrations
RUN uv run alembic upgrade head

# Start bot
CMD ["uv", "run", "python", "main.py"]
```

3. **Setup PostgreSQL database**

4. **Configure environment variables** in hosting platform

### Day 81-82: Monitoring & Logging

**Tasks**:

1. **Setup Sentry** for error tracking:

```bash
uv add sentry-sdk
```

```python
import sentry_sdk
from src.config import settings

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.environment,
    traces_sample_rate=0.1,
)
```

2. **Setup structured logging** with loguru:

```bash
uv add loguru
```

3. **Health check endpoint** for monitoring:

```python
from aiogram import types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


async def health_check(request):
    """Health check endpoint."""
    return web.json_response({"status": "ok"})


app = web.Application()
app.router.add_get("/health", health_check)
```

### Day 83-84: Launch & Documentation

**Tasks**:

1. **Final testing** on staging environment

2. **Create user documentation**:
   - Getting started guide
   - Feature overview
   - FAQs
   - Troubleshooting

3. **Deploy to production**

4. **Monitor initial launch**:
   - Error rates
   - Response times
   - User engagement

5. **Prepare rollback plan** in case of issues

**Deliverables**:
- ✅ Production deployment
- ✅ Monitoring and alerting
- ✅ User documentation
- ✅ Rollback procedures
- ✅ Launch post-mortem

---

## 📈 SUCCESS METRICS

### Technical Metrics
- Response time < 2 seconds (95th percentile)
- Error rate < 1%
- Test coverage > 80%
- Database query time < 100ms
- Crawler success rate > 90%

### User Metrics
- Daily active users > 100 (Month 1)
- User retention > 50% (Day 7)
- Average session duration > 5 minutes
- Feature adoption > 60%
- User satisfaction > 4.0/5.0

### Business Metrics
- School partnerships > 5
- Referral rate > 20%
- Conversion to profile creation > 70%
- University database coverage > 50 universities
- Data freshness < 7 days

---

## 🚀 POST-LAUNCH ROADMAP

### Month 2-3: Feature Expansion
- Mobile app (React Native)
- Web platform
- Advanced ML recommendations
- Integration with official university APIs
- Premium subscription tier

### Month 4-6: Scale
- International universities (100+)
- Multi-language support
- White-label solution for schools
- API for third-party integrations
- Alumni success stories

---

## 📚 APPENDIX A: TECHNOLOGY STACK

### Core Technologies
- **Python 3.12+** - Main language
- **Aiogram 3.x** - Telegram bot framework
- **SQLAlchemy 2.x** - ORM
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation
- **LangChain** - AI orchestration

### AI & ML
- **OpenAI GPT-4** or **Anthropic Claude** - LLM
- **LangGraph** - Agent workflows
- **scikit-learn** - ML recommendations (future)

### Data Collection
- **Playwright** - Browser automation
- **BeautifulSoup4** - HTML parsing
- **httpx** - HTTP client

### Infrastructure
- **PostgreSQL** - Production database
- **Redis** - Caching (future)
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

### Monitoring
- **Sentry** - Error tracking
- **Loguru** - Structured logging
- **Prometheus** - Metrics (future)

### Testing
- **pytest** - Test framework
- **pytest-asyncio** - Async testing
- **pytest-cov** - Coverage
- **Faker** - Test data generation

---

## 📚 APPENDIX B: FILE STRUCTURE

```
uhelper/
├── .github/
│   └── workflows/
│       ├── tests.yml          # CI/CD for tests
│       └── deploy.yml         # Deployment workflow
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
├── docs/
│   ├── DEVELOPMENT_PLAN.md
│   ├── DEVELOPMENT_PLAN4AGENTS.md  # This file
│   ├── PRODUCTION_RELEASE_PLAN.md
│   ├── API.md                 # API documentation
│   └── USER_GUIDE.md          # User manual
├── logs/                      # Application logs
├── scripts/
│   ├── migrate_universities.py
│   ├── backup_db.py
│   └── seed_data.py
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── bot.py                 # Main bot class
│   ├── agents/                # AI agents
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── orchestrator.py
│   │   ├── university_data_agent.py
│   │   ├── profile_analyzer_agent.py
│   │   ├── timeline_agent.py
│   │   ├── exam_prep_agent.py
│   │   ├── document_agent.py
│   │   ├── assessment_agent.py
│   │   └── notification_agent.py
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── database.py
│   │   ├── session.py
│   │   └── partnerships.py
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── repositories/
│   │       ├── user_repository.py
│   │       ├── university_repository.py
│   │       └── session_repository.py
│   ├── crawlers/              # Web crawlers
│   │   ├── __init__.py
│   │   ├── base_crawler.py
│   │   ├── university_crawler.py
│   │   ├── gosuslugi_scraper.py
│   │   ├── crawler_manager.py
│   │   ├── scheduler.py
│   │   ├── validators.py
│   │   └── quality_checker.py
│   ├── features/              # Feature modules
│   │   ├── __init__.py
│   │   ├── referrals.py
│   │   └── partnerships.py
│   ├── analytics/             # Analytics tracking
│   │   ├── __init__.py
│   │   └── tracker.py
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── llm_factory.py
│       ├── logging_config.py
│       └── helpers.py
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── agents/
│   │   ├── test_orchestrator.py
│   │   ├── test_university_data_agent.py
│   │   └── test_profile_analyzer.py
│   ├── crawlers/
│   │   └── test_university_crawler.py
│   ├── database/
│   │   └── test_repositories.py
│   └── e2e/
│       └── test_user_journey.py
├── .env.example              # Environment template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── main.py                   # Application entry point
├── pyproject.toml            # Project configuration
├── README.md
└── uv.lock
```

---

## 📚 APPENDIX C: COMMON PITFALLS & SOLUTIONS

### Pitfall #1: API Rate Limiting
**Problem**: Hitting LLM API rate limits  
**Solution**:
- Implement exponential backoff
- Cache common responses
- Use cheaper models for simple tasks
- Batch requests when possible

### Pitfall #2: Database N+1 Queries
**Problem**: Loading related objects causes many queries  
**Solution**:
- Use SQLAlchemy `selectinload()` or `joinedload()`
- Implement proper eager loading
- Profile queries with SQL logging

### Pitfall #3: Memory Leaks in Long-Running Process
**Problem**: Bot consumes more memory over time  
**Solution**:
- Properly close database sessions
- Clear conversation history periodically
- Monitor memory usage
- Restart bot daily (with crawler scheduler)

### Pitfall #4: Crawler Breaking on Website Changes
**Problem**: University websites change HTML structure  
**Solution**:
- Use multiple selectors as fallbacks
- Implement data quality checks
- Alert on crawler failures
- Manual review of new universities

### Pitfall #5: Time Zone Issues
**Problem**: Deadline dates wrong for different time zones  
**Solution**:
- Store all dates in UTC
- Convert to user timezone for display
- Validate date parsing carefully

---

## 📚 APPENDIX D: AI CODING AGENT INSTRUCTIONS

### For AI Agents Working on This Project

**General Guidelines**:
1. Always read this document first before making changes
2. Follow the phased approach - don't skip ahead
3. Fix critical issues (Phase 0) before adding features
4. Write tests for all new code
5. Update documentation when adding features
6. Follow the project code style rules strictly

**Before Each Coding Session**:
1. Review current project state
2. Identify which phase you're in
3. Check for blocking issues
4. Verify dependencies are installed
5. Run existing tests

**During Coding**:
1. Make small, focused commits
2. Write comprehensive docstrings
3. Add type hints to all functions
4. Log errors properly (never empty except)
5. Validate all user input
6. Use Pydantic models, not raw dicts

**After Coding**:
1. Run linters: `ruff check src/`
2. Run type checker: `mypy src/`
3. Run tests: `pytest`
4. Check coverage: `pytest --cov=src`
5. Test manually in Telegram
6. Update relevant documentation

**Key Commands**:
```bash
# Install dependencies
uv sync

# Run bot
uv run python main.py

# Run tests
uv run pytest

# Run linter
uv run ruff check src/

# Type check
uv run mypy src/

# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

**When Stuck**:
1. Check error logs in `logs/uhelper.log`
2. Review database with: `sqlite3 uhelper.db`
3. Test specific agent in isolation
4. Ask for clarification rather than guessing
5. Review similar working code in project

---

## 🎓 CONCLUSION

This comprehensive plan addresses all aspects of building UHelper from an MVP to a production-ready platform:

✅ **Fixes Past Mistakes** - API config, code style, missing files  
✅ **Complete Feature Set** - All 8 agents, database, crawlers, marketing  
✅ **Real-World Integration** - University APIs, госуслуги, referrals  
✅ **Production Ready** - Testing, monitoring, deployment, documentation  
✅ **Growth Oriented** - Analytics, partnerships, viral features  

**Total Timeline**: 84 days (12 weeks)  
**Complexity**: High - suitable for experienced developers or AI agents  
**Expected Outcome**: Production-ready Telegram bot serving 100s of users  

This plan is designed for AI coding agents to work autonomously while maintaining high code quality and following best practices. Each phase builds upon previous work systematically.

**Good luck with the implementation! 🚀**
