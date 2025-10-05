# AI Viral Video Generator

A complete FastAPI-based system for generating AI-powered ASMR videos with both REST API and command-line interfaces. Deploy easily on AWS Amplify or any cloud platform.

[video.mp4](https://github.com/user-attachments/assets/37fe24ba-e944-46ef-b6ba-cd33080afede)

[video.mp4](https://github.com/user-attachments/assets/9e27a96b-38db-46d9-94e5-b619bef07ee1)

## 🚀 Quick Start

### Option 1: Command Line Interface
```bash
# Install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Test setup
python test_setup.py

# Generate a video
python cli.py generate --wait
```

### Option 2: REST API Server
```bash
# Start the server
python cli.py server

# Visit http://localhost:8000/docs for API documentation
# Use the API endpoints to generate and manage videos
```

## Features

- **🌐 REST API**: Full FastAPI server with automatic OpenAPI documentation
- **💻 Command Line Interface**: Easy-to-use CLI for all operations  
- **⚡ Background Processing**: Asynchronous video generation with job tracking
- **📁 Video Management**: List, download, and delete generated videos
- **☁️ AWS Amplify Ready**: Configured for easy cloud deployment
- **🎬 AI-Powered Generation**: Uses GPT-4, Wavespeed AI, and Fal AI
- **🔊 ASMR Sound Integration**: Custom audio generation and video processing

## 📋 API Endpoints

- `GET /` - API information and available endpoints
- `POST /generate` - Start video generation (returns job ID)
- `GET /status/{job_id}` - Check generation progress
- `GET /videos` - List all generated videos
- `GET /videos/{video_id}/download` - Download video file
- `DELETE /videos/{video_id}` - Delete video

**Interactive Documentation**: Visit `http://localhost:8000/docs` when server is running

## 💻 Command Line Usage

```bash
# Generate a video and wait for completion
python cli.py generate --wait --output my_video.mp4

# Check job status
python cli.py status job_20241005_143022_0

# List all videos
python cli.py list

# Download a video
python cli.py download video_id_here

# Start the API server
python cli.py server --port 8000
```

## Installation

1. **Activate virtual environment and install dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp env.example .env
# Edit .env with your actual API keys
```

3. **Test your setup:**
```bash
python test_setup.py
```

## API Services Required

### OpenAI
- **Purpose**: Generate creative video ideas and detailed scene descriptions
- **Model**: GPT-4 Turbo
- **Get API Key**: https://platform.openai.com/api-keys

### Wavespeed AI (Seedance)
- **Purpose**: Generate video clips from text prompts
- **Model**: seedance-v1-pro-t2v-480p
- **Get API Key**: https://wavespeed.ai/

### Fal AI
- **Purpose**: Generate ASMR sounds and stitch videos together
- **Services**: mmaudio-v2, ffmpeg-api
- **Get API Key**: https://fal.ai/


## ☁️ AWS Amplify Deployment

### Quick Deploy to AWS Amplify

1. **Push to GitHub**: Ensure all files are committed to your repository
2. **Connect to Amplify**: Link your GitHub repository to AWS Amplify
3. **Set Environment Variables** in Amplify Console:
   - `OPENAI_API_KEY`
   - `WAVESPEED_API_KEY` 
   - `FAL_API_KEY`
   - `ENVIRONMENT=production`
4. **Deploy**: Amplify will automatically build and deploy using `amplify.yml`

Your API will be available at: `https://your-app-name.amplifyapp.com`

### Local Development vs Production

**Local Development:**
```bash
# Use the CLI for easy testing
python cli.py generate --wait
python cli.py server --port 8000
```

**Production (AWS Amplify):**
- REST API endpoints available at your Amplify URL
- Use HTTP clients or frontend applications to interact with the API
- Automatic scaling and SSL certificates provided by AWS

## 📁 Project Structure

```
asmr/
├── main.py                 # FastAPI application
├── cli.py                  # Command line interface  
├── ai_video_generator.py   # Core video generation logic
├── test_setup.py          # Setup verification script
├── requirements.txt        # Python dependencies
├── amplify.yml            # AWS Amplify configuration
├── runtime.txt            # Python version
├── Procfile               # Process configuration
├── env.example            # Environment variables template
├── generated_videos/      # Generated video files
├── video_metadata/        # Video metadata JSON files
└── README_API.md          # Detailed API documentation
```

## 🔧 Configuration

- **Video Format**: 9:16 aspect ratio (vertical for social media)
- **Clip Duration**: 10 seconds each
- **Final Video**: 30 seconds (3 clips combined)
- **Background Processing**: Jobs tracked with unique IDs
- **File Storage**: Local storage with metadata JSON files

## 📚 Additional Documentation

- **Detailed API Guide**: See `README_API.md` for comprehensive API documentation
- **Interactive Docs**: Visit `/docs` endpoint when server is running
- **CLI Help**: Run `python cli.py --help` for all available commands
