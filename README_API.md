# ASMR Video Generator API

A FastAPI-based REST API for generating AI-powered ASMR videos that can be deployed on AWS Amplify or any cloud platform.

## 🚀 Features

- **REST API**: Full REST API with FastAPI and automatic OpenAPI documentation
- **Command Line Interface**: Easy-to-use CLI for all operations
- **Background Processing**: Asynchronous video generation with job tracking
- **Video Management**: List, download, and delete generated videos
- **AWS Amplify Ready**: Configured for easy deployment on AWS Amplify
- **Local Storage**: Videos and metadata stored locally with proper file management

## 📋 API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `POST /generate` - Start video generation (returns job ID)
- `GET /status/{job_id}` - Check generation progress
- `GET /videos` - List all generated videos
- `GET /videos/{video_id}` - Get video details
- `GET /videos/{video_id}/download` - Download video file
- `DELETE /videos/{video_id}` - Delete video and metadata
- `GET /jobs` - List all active and recent jobs

### API Documentation

When running the server, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
WAVESPEED_API_KEY=your_wavespeed_api_key_here
FAL_API_KEY=your_fal_api_key_here

# Optional Configuration
ENVIRONMENT=development
PORT=8000
```

### 3. Run the Server

**Option A: Using the CLI (Recommended)**
```bash
python cli.py server --port 8000
```

**Option B: Direct FastAPI**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Option C: Python script**
```bash
python main.py
```

## 🖥️ Command Line Interface

The CLI provides easy access to all API functionality:

### Generate a Video
```bash
# Basic generation
python cli.py generate

# With custom prompt
python cli.py generate --prompt "Custom video idea"

# Without sound
python cli.py generate --no-sound

# Generate and wait for completion
python cli.py generate --wait --output my_video.mp4
```

### Check Job Status
```bash
python cli.py status job_20241005_143022_0
```

### List Videos
```bash
# Simple list
python cli.py list

# JSON output
python cli.py list --json
```

### Download Video
```bash
python cli.py download video_id_here --output downloaded_video.mp4
```

### Delete Video
```bash
python cli.py delete video_id_here --confirm
```

### Start Server
```bash
python cli.py server --port 8000 --host 0.0.0.0
```

## 🌐 API Usage Examples

### Using curl

**Start Video Generation:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"include_sound": true}'
```

**Check Status:**
```bash
curl "http://localhost:8000/status/job_20241005_143022_0"
```

**List Videos:**
```bash
curl "http://localhost:8000/videos"
```

**Download Video:**
```bash
curl -O "http://localhost:8000/videos/job_20241005_143022_0/download"
```

### Using Python requests

```python
import requests
import time

# Start generation
response = requests.post("http://localhost:8000/generate", json={
    "include_sound": True
})
job_data = response.json()
job_id = job_data["job_id"]

# Wait for completion
while True:
    status_response = requests.get(f"http://localhost:8000/status/{job_id}")
    status = status_response.json()
    
    print(f"Status: {status['status']} - {status['progress']}")
    
    if status["status"] == "completed":
        video_id = status["result"]["video_id"]
        break
    elif status["status"] == "failed":
        print(f"Generation failed: {status['error']}")
        break
    
    time.sleep(10)

# Download the video
video_response = requests.get(f"http://localhost:8000/videos/{video_id}/download")
with open(f"{video_id}.mp4", "wb") as f:
    f.write(video_response.content)
```

## ☁️ AWS Amplify Deployment

### 1. Prepare Your Repository

Ensure these files are in your repository:
- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `amplify.yml` - Amplify build configuration
- `runtime.txt` - Python version specification
- `Procfile` - Process configuration

### 2. Deploy to AWS Amplify

1. **Connect Repository**: Link your GitHub/GitLab repository to AWS Amplify
2. **Configure Build Settings**: Amplify will automatically detect the `amplify.yml` file
3. **Set Environment Variables**: Add your API keys in the Amplify console:
   - `OPENAI_API_KEY`
   - `WAVESPEED_API_KEY`
   - `FAL_API_KEY`
   - `ENVIRONMENT=production`
4. **Deploy**: Amplify will build and deploy your application

### 3. Access Your Deployed API

Your API will be available at: `https://your-app-name.amplifyapp.com`

- API Documentation: `https://your-app-name.amplifyapp.com/docs`
- Generate Video: `POST https://your-app-name.amplifyapp.com/generate`

## 📁 File Structure

```
asmr/
├── main.py                 # FastAPI application
├── cli.py                  # Command line interface
├── ai_video_generator.py   # Core video generation logic
├── requirements.txt        # Python dependencies
├── amplify.yml            # AWS Amplify configuration
├── runtime.txt            # Python version
├── Procfile               # Process configuration
├── env.example            # Environment variables template
├── generated_videos/      # Generated video files
├── video_metadata/        # Video metadata JSON files
└── README_API.md          # This documentation
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4 |
| `WAVESPEED_API_KEY` | Yes | Wavespeed API key for video generation |
| `FAL_API_KEY` | Yes | Fal AI API key for audio and video processing |
| `ENVIRONMENT` | No | `development` or `production` (default: production) |
| `PORT` | No | Server port (default: 8000) |

### API Rate Limits

The application respects the rate limits of the underlying AI services:
- **OpenAI**: Standard GPT-4 rate limits
- **Wavespeed**: Video generation may take 2-5 minutes per clip
- **Fal AI**: Audio generation and video processing limits

## 🚨 Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Job or video not found
- **500 Internal Server Error**: Generation failures, API errors
- **503 Service Unavailable**: External API service issues

All errors return JSON with detailed error messages:
```json
{
  "detail": "Detailed error message here"
}
```

## 📊 Monitoring & Logging

- All operations are logged with timestamps
- Job progress is tracked and can be monitored via `/status/{job_id}`
- Active jobs can be viewed at `/jobs`
- Video metadata includes generation timestamps and parameters

## 🔒 Security Considerations

For production deployment:

1. **Environment Variables**: Store API keys securely in environment variables
2. **CORS**: Configure CORS origins appropriately for your domain
3. **Rate Limiting**: Consider adding rate limiting for public APIs
4. **File Storage**: Consider using cloud storage (S3) for video files in production
5. **Authentication**: Add authentication for sensitive operations

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
- Check that all required environment variables are set
- Verify API keys are valid
- Ensure port is not already in use

**Video generation fails:**
- Check API key validity and quotas
- Verify network connectivity to external APIs
- Check logs for specific error messages

**Files not found:**
- Ensure `generated_videos/` and `video_metadata/` directories exist
- Check file permissions

### Getting Help

1. Check the server logs for detailed error messages
2. Verify all API keys are correctly set
3. Test individual API endpoints using the interactive docs at `/docs`
4. Use the CLI with verbose output for debugging

## 📝 License

This project is provided as-is for educational and development purposes.
