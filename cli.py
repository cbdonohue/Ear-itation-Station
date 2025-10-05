#!/usr/bin/env python3
"""
Command Line Interface for ASMR Video Generator API
Provides easy command-line access to the FastAPI endpoints
"""

import os
import sys
import json
import time
import requests
import argparse
from typing import Optional
from datetime import datetime

class ASMRVideoClient:
    """Client for interacting with the ASMR Video Generator API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def generate_video(self, custom_prompt: Optional[str] = None, include_sound: bool = True) -> dict:
        """Start video generation"""
        payload = {
            "custom_prompt": custom_prompt,
            "include_sound": include_sound
        }
        
        response = requests.post(f"{self.base_url}/generate", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id: str) -> dict:
        """Get job status"""
        response = requests.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def list_videos(self) -> list:
        """List all videos"""
        response = requests.get(f"{self.base_url}/videos")
        response.raise_for_status()
        return response.json()
    
    def get_video_info(self, video_id: str) -> dict:
        """Get video information"""
        response = requests.get(f"{self.base_url}/videos/{video_id}")
        response.raise_for_status()
        return response.json()
    
    def download_video(self, video_id: str, output_path: Optional[str] = None) -> str:
        """Download video file"""
        response = requests.get(f"{self.base_url}/videos/{video_id}/download", stream=True)
        response.raise_for_status()
        
        if not output_path:
            output_path = f"{video_id}.mp4"
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def delete_video(self, video_id: str) -> dict:
        """Delete video"""
        response = requests.delete(f"{self.base_url}/videos/{video_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id: str, timeout: int = 1800) -> dict:
        """Wait for job completion with progress updates"""
        start_time = time.time()
        last_progress = ""
        
        print(f"Waiting for job {job_id} to complete...")
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_job_status(job_id)
                
                # Print progress updates
                if status['progress'] != last_progress:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {status['progress']}")
                    last_progress = status['progress']
                
                if status['status'] == 'completed':
                    print(f"✅ Job completed successfully!")
                    return status
                elif status['status'] == 'failed':
                    print(f"❌ Job failed: {status.get('error', 'Unknown error')}")
                    return status
                
                time.sleep(10)  # Check every 10 seconds
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Error checking status: {e}")
                time.sleep(10)
        
        print(f"⏰ Job timed out after {timeout} seconds")
        return self.get_job_status(job_id)

def main():
    parser = argparse.ArgumentParser(description="ASMR Video Generator CLI")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a new video")
    gen_parser.add_argument("--prompt", help="Custom prompt for video generation")
    gen_parser.add_argument("--no-sound", action="store_true", help="Generate video without ASMR sound")
    gen_parser.add_argument("--wait", action="store_true", help="Wait for completion and download")
    gen_parser.add_argument("--output", help="Output filename for downloaded video")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("job_id", help="Job ID to check")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all videos")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get video information")
    info_parser.add_argument("video_id", help="Video ID")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download video")
    download_parser.add_argument("video_id", help="Video ID to download")
    download_parser.add_argument("--output", help="Output filename")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete video")
    delete_parser.add_argument("video_id", help="Video ID to delete")
    delete_parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start the API server")
    server_parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = ASMRVideoClient(args.url)
    
    try:
        if args.command == "generate":
            print("🎬 Starting video generation...")
            result = client.generate_video(
                custom_prompt=args.prompt,
                include_sound=not args.no_sound
            )
            
            print(f"✅ Generation started!")
            print(f"Job ID: {result['job_id']}")
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            
            if args.wait:
                print("\n⏳ Waiting for completion...")
                final_status = client.wait_for_completion(result['job_id'])
                
                if final_status['status'] == 'completed' and final_status.get('result'):
                    video_id = final_status['result']['video_id']
                    output_path = args.output or f"{video_id}.mp4"
                    
                    print(f"\n📥 Downloading video...")
                    downloaded_path = client.download_video(video_id, output_path)
                    print(f"✅ Video saved as: {downloaded_path}")
                    
                    # Print video info
                    result_info = final_status['result']
                    print(f"\n📋 Video Details:")
                    print(f"   Idea: {result_info['idea']}")
                    print(f"   Caption: {result_info['caption']}")
                    print(f"   Download URL: {args.url}{result_info['download_url']}")
        
        elif args.command == "status":
            status = client.get_job_status(args.job_id)
            print(f"Job ID: {status['job_id']}")
            print(f"Status: {status['status']}")
            print(f"Progress: {status['progress']}")
            
            if status.get('result'):
                print(f"Result: {json.dumps(status['result'], indent=2)}")
            if status.get('error'):
                print(f"Error: {status['error']}")
        
        elif args.command == "list":
            videos = client.list_videos()
            
            if args.json:
                print(json.dumps(videos, indent=2))
            else:
                if not videos:
                    print("No videos found.")
                else:
                    print(f"Found {len(videos)} videos:\n")
                    for video in videos:
                        size_mb = video['file_size'] / (1024*1024) if video['file_size'] else 0
                        print(f"🎥 {video['id']}")
                        print(f"   Idea: {video['idea']}")
                        print(f"   Created: {video['created_at']}")
                        print(f"   Size: {size_mb:.1f} MB")
                        print(f"   Status: {video['status']}")
                        print()
        
        elif args.command == "info":
            info = client.get_video_info(args.video_id)
            print(json.dumps(info, indent=2))
        
        elif args.command == "download":
            print(f"📥 Downloading video {args.video_id}...")
            output_path = client.download_video(args.video_id, args.output)
            print(f"✅ Video saved as: {output_path}")
        
        elif args.command == "delete":
            if not args.confirm:
                confirm = input(f"Are you sure you want to delete video {args.video_id}? (y/N): ")
                if confirm.lower() != 'y':
                    print("Cancelled.")
                    return
            
            result = client.delete_video(args.video_id)
            print(f"✅ {result['message']}")
        
        elif args.command == "server":
            print(f"🚀 Starting ASMR Video Generator API server...")
            print(f"   Host: {args.host}")
            print(f"   Port: {args.port}")
            print(f"   URL: http://{args.host}:{args.port}")
            print("\nPress Ctrl+C to stop the server")
            
            # Set environment variables
            os.environ["PORT"] = str(args.port)
            
            # Import and run uvicorn
            import uvicorn
            uvicorn.run(
                "main:app",
                host=args.host,
                port=args.port,
                reload=False
            )
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API server at {args.url}")
        print("Make sure the server is running with: python cli.py server")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
