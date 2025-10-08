from sqlalchemy import create_engine, Column, Integer, String, Text, JSON ,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os
env_path='C:/Users/ParsRayaneh/LLM_engineering/llm_engineering/Agent_Project/.env'
load_dotenv(env_path)
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    field = Column(String)
    institution = Column(String)
    years_of_experience = Column(Integer, nullable=True)
    skills = Column(Text) 
    projects = Column(Text)
    interests = Column(Text)
    summary = Column(Text)
    evaluation = Column(Text)
    chat_history = Column(Text, nullable=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True) 
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
#Base.metadata.create_all(bind=engine)