"""
Database Schemas for Creator Social App

Each Pydantic model corresponds to a MongoDB collection. The collection name is the lowercase of the class name.
- Creator -> "creator"
- Segment -> "segment"

These schemas are used for validation when creating/editing documents.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Segment(BaseModel):
    """Content segment/category (e.g., Tech, Gaming, Beauty)."""
    name: str = Field(..., description="Display name of the segment")
    slug: str = Field(..., description="URL-friendly unique identifier")
    description: Optional[str] = Field(None, description="Short description of the segment")
    cover_image: Optional[HttpUrl] = Field(None, description="Hero/cover image for the segment")
    color: Optional[str] = Field(None, description="Hex color used in UI accents for this segment")


class Creator(BaseModel):
    """Creator profile stored in the database."""
    name: str = Field(..., description="Creator's display name")
    handle: Optional[str] = Field(None, description="Primary handle without @")
    platforms: List[str] = Field(default_factory=list, description="Platforms where the creator is active")
    avatar_url: Optional[HttpUrl] = Field(None, description="Avatar or profile image URL")
    banner_url: Optional[HttpUrl] = Field(None, description="Banner/cover image URL")
    bio: Optional[str] = Field(None, description="Short bio")
    segments: List[str] = Field(..., description="List of segment slugs the creator belongs to")
    location: Optional[str] = Field(None, description="City/Country")
    languages: List[str] = Field(default_factory=list, description="Languages the creator uses")
    website: Optional[HttpUrl] = Field(None, description="Personal site or link-in-bio")
    followers: int = Field(0, ge=0, description="Approx total followers across platforms")
    rating: float = Field(0.0, ge=0, le=5, description="Community score 0-5")
    verified: bool = Field(False, description="Verified by the community/platform")


# Example schemas kept for reference by the viewer
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
