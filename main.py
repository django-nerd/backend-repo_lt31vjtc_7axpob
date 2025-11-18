import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Creator, Segment

app = FastAPI(title="Creator Social API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Creator Social API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# ----- Seed data endpoint (idempotent) -----
class SeedResponse(BaseModel):
    segments_created: int
    creators_created: int


@app.post("/seed", response_model=SeedResponse)
def seed_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    segments_seed = [
        {
            "name": "Technology",
            "slug": "technology",
            "description": "Tech reviews, coding, gadgets",
            "color": "#60A5FA"
        },
        {
            "name": "Gaming",
            "slug": "gaming",
            "description": "Let\"s plays, esports, streaming",
            "color": "#A78BFA"
        },
        {
            "name": "Lifestyle",
            "slug": "lifestyle",
            "description": "Wellness, productivity, daily vlogs",
            "color": "#34D399"
        },
        {
            "name": "Education",
            "slug": "education",
            "description": "Explainers, tutorials, lectures",
            "color": "#F59E0B"
        }
    ]

    creators_seed = [
        {
            "name": "TechNova",
            "handle": "technova",
            "platforms": ["YouTube", "X", "TikTok"],
            "avatar_url": "https://i.pravatar.cc/150?img=11",
            "bio": "Deep dives into emerging tech.",
            "segments": ["technology"],
            "followers": 1200000,
            "rating": 4.7,
            "verified": True
        },
        {
            "name": "GamePulse",
            "handle": "gamepulse",
            "platforms": ["Twitch", "YouTube"],
            "avatar_url": "https://i.pravatar.cc/150?img=12",
            "bio": "Strategy breakdowns and chill streams.",
            "segments": ["gaming"],
            "followers": 860000,
            "rating": 4.5,
            "verified": True
        },
        {
            "name": "DailyFlow",
            "handle": "dailyflow",
            "platforms": ["Instagram", "YouTube"],
            "avatar_url": "https://i.pravatar.cc/150?img=13",
            "bio": "Wellness routines that actually stick.",
            "segments": ["lifestyle"],
            "followers": 430000,
            "rating": 4.3,
            "verified": False
        },
        {
            "name": "ProfLearn",
            "handle": "proflearn",
            "platforms": ["YouTube", "Udemy"],
            "avatar_url": "https://i.pravatar.cc/150?img=14",
            "bio": "Clear, concise CS courses.",
            "segments": ["education", "technology"],
            "followers": 650000,
            "rating": 4.8,
            "verified": True
        }
    ]

    # Upsert-like behavior: avoid duplicates by slug/handle
    seg_coll = db["segment"]
    created_segments = 0
    for seg in segments_seed:
        if not seg_coll.find_one({"slug": seg["slug"]}):
            seg_id = seg_coll.insert_one({**seg}).inserted_id
            created_segments += 1

    crt_coll = db["creator"]
    created_creators = 0
    for crt in creators_seed:
        if not crt_coll.find_one({"handle": crt.get("handle")}):
            crt_id = crt_coll.insert_one({**crt}).inserted_id
            created_creators += 1

    return SeedResponse(segments_created=created_segments, creators_created=created_creators)


# ----- Public API -----
class CreatorOut(BaseModel):
    id: str
    name: str
    handle: Optional[str] = None
    avatar_url: Optional[str] = None
    segments: List[str]
    followers: int
    rating: float
    verified: bool


class SegmentOut(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    color: Optional[str] = None


@app.get("/segments", response_model=List[SegmentOut])
def list_segments():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("segment")
    res = []
    for d in docs:
        res.append(SegmentOut(
            name=d.get("name"), slug=d.get("slug"), description=d.get("description"), color=d.get("color")
        ))
    return res


@app.get("/top-creators", response_model=List[CreatorOut])
def top_creators(segment: Optional[str] = Query(None, description="Filter by segment slug"), limit: int = 8):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filt = {}
    if segment:
        filt = {"segments": {"$in": [segment]}}
    docs = db["creator"].find(filt).sort("followers", -1).limit(limit)
    res: List[CreatorOut] = []
    for d in docs:
        res.append(CreatorOut(
            id=str(d.get("_id")),
            name=d.get("name"),
            handle=d.get("handle"),
            avatar_url=d.get("avatar_url"),
            segments=d.get("segments", []),
            followers=int(d.get("followers", 0)),
            rating=float(d.get("rating", 0)),
            verified=bool(d.get("verified", False)),
        ))
    return res


# Health/simple hello
@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Creator Social backend!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
