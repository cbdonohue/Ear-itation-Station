# AI Viral Video Generator

This Python script converts the n8n workflow for generating AI viral videos with ASMR sounds into a sequential Python implementation.

[video.mp4](https://github.com/user-attachments/assets/37fe24ba-e944-46ef-b6ba-cd33080afede)

[video.mp4](https://github.com/user-attachments/assets/9e27a96b-38db-46d9-94e5-b619bef07ee1)


## Features

- **AI-Powered Idea Generation**: Uses GPT-4 to generate creative video concepts
- **Detailed Scene Creation**: Generates multiple detailed video scenes for each idea
- **Video Generation**: Creates video clips using Seedance AI (Wavespeed)
- **ASMR Sound Generation**: Adds custom ASMR sounds using Fal AI
- **Video Stitching**: Combines multiple clips into a final video
- **Result Logging**: Logs all generation results with timestamps

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env_example.txt .env
# Edit .env with your actual API keys
```

3. Set your API keys:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
export WAVESPEED_API_KEY=your_wavespeed_api_key_here
export FAL_API_KEY=your_fal_api_key_here
```

## Usage

Run the script:
```bash
python ai_video_generator.py
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


## Workflow Steps

1. **Generate Creative Idea**: AI creates a viral-worthy video concept
2. **Create Scene Descriptions**: Detailed prompts for multiple video scenes
3. **Generate Video Clips**: Each scene becomes a 10-second video clip
4. **Add ASMR Sound**: Custom audio generation for the first clip
5. **Stitch Videos**: Combine all clips into a final 30-second video
6. **Log Results**: Output all generation data with timestamps

## Configuration

- Video aspect ratio: 9:16 (vertical for social media)
- Clip duration: 10 seconds each
- Final video: 30 seconds (3 clips)
- Sound duration: 10 seconds

## Error Handling

The script includes comprehensive error handling and logging:
- API request failures are caught and logged
- Generation timeouts are handled gracefully
- All steps are logged with timestamps

## Notes

- All API calls include proper rate limiting and error handling
- Results are logged to console with full metadata for easy tracking
