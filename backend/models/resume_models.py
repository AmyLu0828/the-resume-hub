"""
Pydantic Models for Resume Data

This file contains:
1. Data validation models matching frontend types
2. Request/response models for API endpoints
3. Validation rules and constraints
4. Type definitions for all resume sections

Key models implemented:
- ResumeData (matches frontend ResumeData interface)
- Name, AboutMe, Education, Experience, Contact, Skill, CustomSection
- UpdateMessage (matches frontend UpdateMessage interface)
- PolishRequest (for content improvement requests)
- API response models
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
import re

# Base models matching frontend interfaces
class Name(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)

class AboutMe(BaseModel):
    description: str = Field(default="", max_length=500)
    polishedDescription: Optional[str] = Field(default=None, max_length=500)

class Contact(BaseModel):
    id: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1, max_length=20)  # Email, Phone, LinkedIn, etc.
    value: str = Field(..., min_length=1, max_length=100)
    
    @validator('value')
    def validate_contact_value(cls, v, values):
        contact_type = values.get('type', '').lower()
        if contact_type == 'email':
            # Basic email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('Invalid email format')
        elif contact_type == 'phone':
            # Basic phone validation (allow various formats)
            if not re.match(r'^[\+]?[1-9][\d]{0,15}$', re.sub(r'[\s\-\(\)]', '', v)):
                raise ValueError('Invalid phone number format')
        elif contact_type == 'linkedin':
            # Basic LinkedIn URL validation
            if not re.match(r'^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+/?$', v):
                raise ValueError('Invalid LinkedIn URL format')
        return v

class Education(BaseModel):
    id: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1, max_length=100)
    institution: str = Field(..., min_length=1, max_length=100)
    startDate: str = Field(..., min_length=1)  # Format: YYYY-MM
    endDate: str = Field(default="", min_length=0)  # Format: YYYY-MM or empty for current
    description: str = Field(default="", max_length=500)
    polishedDescription: Optional[str] = Field(default=None, max_length=500)
    
    @validator('startDate', 'endDate')
    def validate_date_format(cls, v):
        if v == "":  # Allow empty end date for current education
            return v
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('Date must be in YYYY-MM format')
        return v

class Experience(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    startDate: str = Field(..., min_length=1)  # Format: YYYY-MM
    endDate: str = Field(default="", min_length=0)  # Format: YYYY-MM or empty for current
    description: str = Field(default="", max_length=1000)
    keywords: List[str] = Field(default_factory=list)
    polishedDescription: Optional[str] = Field(default=None, max_length=1000)
    
    @validator('startDate', 'endDate')
    def validate_date_format(cls, v):
        if v == "":  # Allow empty end date for current experience
            return v
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('Date must be in YYYY-MM format')
        return v

class Skill(BaseModel):
    id: str = Field(..., min_length=1)
    skill: str = Field(..., min_length=1, max_length=50)

class CustomSection(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(default="", max_length=1000)

# Main resume data model
class ResumeData(BaseModel):
    name: Name
    aboutMe: AboutMe
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    contact: List[Contact] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    customSections: List[CustomSection] = Field(default_factory=list)

# Update message model (matches frontend UpdateMessage interface)
class UpdateMessage(BaseModel):
    section: str = Field(..., min_length=1)
    entryId: str = Field(..., min_length=1)
    changeType: Literal["add", "update", "delete"]
    content: Dict[str, Any]

# Polish request model (for content improvement)
class PolishRequest(BaseModel):
    section: str = Field(..., min_length=1)
    entryId: str = Field(..., min_length=1)
    content: Dict[str, Any]

# API Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class PolishResponse(BaseModel):
    success: bool
    improvedContent: Dict[str, Any]
    message: str

class PDFGenerationResponse(BaseModel):
    success: bool
    pdfUrl: Optional[str] = None
    message: str

class TemplatesResponse(BaseModel):
    success: bool
    templates: List[str]

# Error response model
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
