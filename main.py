#!/usr/bin/env python3
"""
FastAPI ASMR Video Generator
A REST API for generating and managing ASMR videos using AI
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
import requests
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai_video_generator import AIVideoGenerator, VideoIdea, VideoScene

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ASMR Video Generator API",
    description="Generate and manage AI-powered ASMR videos",
    version="1.0.0"
)

# Add CORS middleware for web deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing videos and metadata
VIDEOS_DIR = Path("generated_videos")
METADATA_DIR = Path("video_metadata")
VIDEOS_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)

# Pydantic models for API
class VideoGenerationRequest(BaseModel):
    custom_prompt: Optional[str] = None
    include_sound: bool = True

class VideoGenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str

class VideoInfo(BaseModel):
    id: str
    filename: str
    idea: str
    caption: str
    status: str
    created_at: str
    file_size: Optional[int] = None
    duration: Optional[int] = None
    video_url: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory job tracking (in production, use Redis or database)
active_jobs: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ASMR Video Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/generate - Start video generation",
            "status": "/status/{job_id} - Check generation status",
            "videos": "/videos - List all videos",
            "download": "/videos/{video_id}/download - Download video",
            "delete": "/videos/{video_id} - Delete video"
        }
    }

@app.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Start video generation process"""
    try:
        # Generate unique job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(active_jobs)}"
        
        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "started",
            "progress": "Initializing video generation...",
            "created_at": datetime.now().isoformat(),
            "request": request.dict()
        }
        
        # Start background task
        background_tasks.add_task(
            run_video_generation,
            job_id,
            request.custom_prompt,
            request.include_sound
        )
        
        return VideoGenerationResponse(
            job_id=job_id,
            status="started",
            message="Video generation started. Use /status/{job_id} to check progress."
        )
        
    except Exception as e:
        logger.error(f"Error starting video generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a video generation job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = active_jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job_data["status"],
        progress=job_data["progress"],
        result=job_data.get("result"),
        error=job_data.get("error")
    )

@app.get("/videos", response_model=List[VideoInfo])
async def list_videos():
    """List all generated videos"""
    videos = []
    
    try:
        # Scan video directory for files
        for video_file in VIDEOS_DIR.glob("*.mp4"):
            # Look for corresponding metadata file
            metadata_file = METADATA_DIR / f"{video_file.stem}.json"
            
            if metadata_file.exists():
                async with aiofiles.open(metadata_file, 'r') as f:
                    metadata = json.loads(await f.read())
                
                # Get file stats
                file_stats = video_file.stat()
                
                videos.append(VideoInfo(
                    id=video_file.stem,
                    filename=video_file.name,
                    idea=metadata.get("idea", "Unknown"),
                    caption=metadata.get("caption", "No caption"),
                    status=metadata.get("status", "completed"),
                    created_at=metadata.get("timestamp", datetime.fromtimestamp(file_stats.st_ctime).isoformat()),
                    file_size=file_stats.st_size,
                    video_url=metadata.get("final_video_url")
                ))
        
        # Sort by creation time (newest first)
        videos.sort(key=lambda x: x.created_at, reverse=True)
        return videos
        
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos/{video_id}")
async def get_video_info(video_id: str):
    """Get detailed information about a specific video"""
    metadata_file = METADATA_DIR / f"{video_id}.json"
    video_file = VIDEOS_DIR / f"{video_id}.mp4"
    
    if not metadata_file.exists() or not video_file.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        async with aiofiles.open(metadata_file, 'r') as f:
            metadata = json.loads(await f.read())
        
        file_stats = video_file.stat()
        
        return {
            "id": video_id,
            "filename": video_file.name,
            "metadata": metadata,
            "file_size": file_stats.st_size,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/videos/{video_id}/download")
async def download_video(video_id: str):
    """Download a generated video file"""
    video_file = VIDEOS_DIR / f"{video_id}.mp4"
    
    if not video_file.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        path=str(video_file),
        media_type="video/mp4",
        filename=f"{video_id}.mp4"
    )

@app.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """Delete a generated video and its metadata"""
    video_file = VIDEOS_DIR / f"{video_id}.mp4"
    metadata_file = METADATA_DIR / f"{video_id}.json"
    
    deleted_files = []
    
    if video_file.exists():
        video_file.unlink()
        deleted_files.append("video")
    
    if metadata_file.exists():
        metadata_file.unlink()
        deleted_files.append("metadata")
    
    if not deleted_files:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "message": f"Deleted {', '.join(deleted_files)} for video {video_id}",
        "deleted_files": deleted_files
    }

@app.get("/jobs")
async def list_active_jobs():
    """List all active and recent jobs"""
    return {
        "active_jobs": len([j for j in active_jobs.values() if j["status"] in ["started", "processing"]]),
        "total_jobs": len(active_jobs),
        "jobs": active_jobs
    }

async def run_video_generation(job_id: str, custom_prompt: Optional[str], include_sound: bool):
    """Background task to run video generation"""
    try:
        # Update job status
        active_jobs[job_id]["status"] = "processing"
        active_jobs[job_id]["progress"] = "Initializing AI video generator..."
        
        # Initialize the generator
        generator = AIVideoGenerator()
        
        # Step 1: Generate video idea
        active_jobs[job_id]["progress"] = "Generating creative video idea..."
        idea = generator.generate_creative_video_idea()
        logger.info(f"Job {job_id}: Generated idea: {idea.idea}")
        
        # Step 2: Generate detailed scenes
        active_jobs[job_id]["progress"] = "Creating detailed video scenes..."
        scenes = generator.generate_detailed_video_prompts(idea)
        logger.info(f"Job {job_id}: Generated {len(scenes)} scenes")
        
        # Step 3: Generate video clips
        active_jobs[job_id]["progress"] = "Generating video clips (this may take several minutes)..."
        video_urls = generator.generate_video_clips(scenes, idea)
        logger.info(f"Job {job_id}: Generated {len(video_urls)} video clips")
        
        # Step 4: Generate ASMR sounds (if requested)
        sound_urls = []
        if include_sound and video_urls:
            active_jobs[job_id]["progress"] = "Generating ASMR sounds..."
            for i, video_url in enumerate(video_urls):
                try:
                    sound_url = generator.generate_asmr_sound(video_url, idea)
                    sound_urls.append(sound_url)
                    logger.info(f"Job {job_id}: Generated sound for clip {i+1}")
                except Exception as e:
                    logger.warning(f"Job {job_id}: Sound generation failed for clip {i+1}: {e}")
                    sound_urls.append(None)
        else:
            sound_urls = [None] * len(video_urls)
        
        # Step 5: Merge video clips
        active_jobs[job_id]["progress"] = "Merging video clips into final video..."
        final_video_url = generator.merge_video_clips(video_urls, sound_urls)
        logger.info(f"Job {job_id}: Final video URL: {final_video_url}")
        
        # Step 6: Download and save the final video
        active_jobs[job_id]["progress"] = "Downloading and saving final video..."
        video_filename = await download_and_save_video(final_video_url, job_id)
        
        # Step 7: Save metadata
        metadata = {
            "job_id": job_id,
            "idea": idea.idea,
            "caption": idea.caption,
            "environment": idea.environment,
            "sound": idea.sound,
            "status": idea.status,
            "scenes": [scene.description for scene in scenes],
            "video_urls": video_urls,
            "sound_urls": sound_urls,
            "final_video_url": final_video_url,
            "local_filename": video_filename,
            "timestamp": datetime.now().isoformat(),
            "include_sound": include_sound
        }
        
        metadata_file = METADATA_DIR / f"{job_id}.json"
        async with aiofiles.open(metadata_file, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
        
        # Update job status to completed
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = "Video generation completed successfully!"
        active_jobs[job_id]["result"] = {
            "video_id": job_id,
            "filename": video_filename,
            "idea": idea.idea,
            "caption": idea.caption,
            "final_video_url": final_video_url,
            "download_url": f"/videos/{job_id}/download"
        }
        
        logger.info(f"Job {job_id}: Completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["progress"] = f"Generation failed: {str(e)}"
        active_jobs[job_id]["error"] = str(e)

async def download_and_save_video(video_url: str, job_id: str) -> str:
    """Download video from URL and save locally"""
    try:
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"asmr_video_{timestamp}_{job_id}.mp4"
        filepath = VIDEOS_DIR / filename
        
        # Download the video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        # Save to local file
        async with aiofiles.open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                await f.write(chunk)
        
        logger.info(f"Video saved as {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    
    # Check for required environment variables
    required_env_vars = [
        'OPENAI_API_KEY',
        'WAVESPEED_API_KEY', 
        'FAL_API_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set the following environment variables:")
        for var in missing_vars:
            logger.error(f"  export {var}=your_api_key_here")
        exit(1)
    
    # Run the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
