#!/usr/bin/env python3
"""
AI Viral Video Generator
Converts the n8n workflow into a sequential Python script for generating AI videos with ASMR sounds.
"""

import os
import json
import time
import requests
import openai
from typing import Dict, List, Any
import logging
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VideoIdea:
    """Data class for video idea metadata"""
    caption: str
    idea: str
    environment: str
    sound: str
    status: str = "for production"

@dataclass
class VideoScene:
    """Data class for individual video scenes"""
    description: str

class AIVideoGenerator:
    """Main class for AI video generation pipeline"""
    
    def __init__(self):
        """Initialize the video generator with API credentials"""
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.wavespeed_api_key = os.getenv('WAVESPEED_API_KEY')
        self.fal_api_key = os.getenv('FAL_API_KEY')
        
        # API endpoints
        self.wavespeed_url = "https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-t2v-480p"
        self.fal_audio_url = "https://queue.fal.run/fal-ai/mmaudio-v2"
        self.fal_ffmpeg_url = "https://queue.fal.run/fal-ai/ffmpeg-api/compose"
        
    def generate_creative_video_idea(self) -> VideoIdea:
        """Generate a creative video idea using GPT-4"""
        logger.info("Generating creative video idea...")
        
        system_prompt = """**Role:**  
You are an AI designed to generate **one immersive, realistic idea** based on a user-provided topic. Your output must be formatted as a **single-line JSON array** and follow the rules below exactly.

---

### RULES

1. **Number of ideas**  
   - Return **only one idea**.

2. **Topic**  
   - The user will provide a keyword (e.g., “glass cutting ASMR,” “wood carving sounds,” “satisfying rock splits”).

3. **Idea**  
   - Maximum 13 words.  
   - Describe a viral-worthy, original, or surreal moment related to the topic.

4. **Caption**  
   - Short, punchy, viral-friendly.  
   - Include **one emoji**.  
   - Exactly **12 hashtags** in this order:  
     1. 4 topic-relevant hashtags  
     2. 4 all-time most popular hashtags  
     3. 4 currently trending hashtags (based on live research)  
   - All in lowercase.

5. **Environment**  
   - Maximum 20 words.  
   - Must match the action in the Idea exactly.  
   - Specify location (studio table, natural terrain, lab bench…), visual details (dust particles, polished surface, subtle reflections…), and style (macro close-up, cinematic slow-motion, minimalist…).

6. **Sound**  
   - Maximum 15 words.  
   - Describe the primary sound for the scene (to feed into an audio model).

7. **Status**  
   - Always set to `"for production"`.

---

### OUTPUT FORMAT (single-line JSON array)

```json
[
  {
    "Caption": "Your short viral title with emoji #4_topic_hashtags #4_all_time_popular_hashtags #4_trending_hashtags",
    "Idea": "Your idea under 13 words",
    "Environment": "Your vivid setting under 20 words matching the action",
    "Sound": "Your primary sound description under 15 words",
    "Status": "for production"
  }
]
"""

        user_prompt = """Generate a creative concept involving:

A solid, hard material or element being sliced cleanly with a sharp blade. Your response must follow this structure:

"(Color) (Material) shaped like a (random everyday object)"

For inspiration, imagine examples like: obsidian shaped like a chess piece, quartz shaped like a coffee mug, sapphire shaped like a seashell, or titanium shaped like a leaf.

Reflect carefully before answering to ensure originality and visual appeal."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",  # Using gpt-4-turbo as per user preference
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            idea_data = json.loads(content)[0]
            return VideoIdea(
                caption=idea_data['Caption'],
                idea=idea_data['Idea'],
                environment=idea_data['Environment'],
                sound=idea_data['Sound'],
                status=idea_data['Status']
            )
            
        except Exception as e:
            logger.error(f"Error generating video idea: {e}")
            raise

    def generate_detailed_video_prompts(self, idea: VideoIdea) -> List[VideoScene]:
        """Generate detailed video prompts with multiple scenes"""
        logger.info("Generating detailed video prompts...")
        
        system_prompt = """Role: You are a prompt-generation AI specializing in cinematic, ASMR-style video prompts. Your task is to generate a multi-scene video sequence that vividly shows a sharp knife actively cutting through a specific object in a clean, high-detail setting.

Your writing must follow this style:

Sharp, precise cinematic realism.

Macro-level detail with tight focus on the blade interacting with the object.

The knife must always be in motion — slicing, splitting, or gliding through the material. Never idle or static.

Camera terms are allowed (e.g. macro view, tight angle, over-the-blade shot).

Each scene must contain all of the following, expressed through detailed visual language:

✅ The main object or subject (from the Idea)

✅ The cutting environment or surface (from the Environment)

✅ The texture, structure, and behavior of the material as it’s being cut

✅ A visible, sharp blade actively cutting

Descriptions should show:

The physical makeup of the material — is it translucent, brittle, dense, reflective, granular, fibrous, layered, or fluid-filled?

How the material responds to the blade — resistance, cracking, tearing, smooth separation, tension, vibration.

The interaction between the blade and the surface — light reflection, buildup of particles, contact points, residue or dust.

Any ASMR-relevant sensory cues like particle release, shimmer, or subtle movement, but always shown visually — not narrated.

Tone:

Clean, clinical, visual.

No poetic metaphors, emotion, or storytelling.

Avoid fantasy or surreal imagery.

All description must feel physically grounded and logically accurate.

Length:

Each scene must be between 1,000 and 2,000 characters.

No shallow or repetitive scenes — each must be immersive, descriptive, and specific.

Each scene should explore a distinct phase of the cutting process, a different camera perspective, or a new behavior of the material under the blade.

Inputs:

Idea: "{{ $json.idea }}"
Environment: "{{ $json.environment_prompt }}"
Sound: "{{ $json.sound_prompt }}"

Format:

Idea: "..."
Environment: "..."
Sound: "..."

Scene 1: "..."
Scene 2: "..."
Scene 3: "..."
Scene 4: "..."
Scene 5: "..."
Scene 6: "..."
Scene 7: "..."
Scene 8: "..."
Scene 9: "..."
Scene 10: "..."
Scene 11: "..."
Scene 12: "..."
Scene 13: "..."
"""

        user_prompt = f"""Give me 3 video prompts based on the previous idea

Idea: "{idea.idea}"
Environment: "{idea.environment}"
Sound: "{idea.sound}" """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",  # Using gpt-4-turbo as per user preference
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract scene descriptions from the response
            scenes = []
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('Scene '):
                    scene_desc = line.split(':', 1)[1].strip().strip('"')
                    scenes.append(VideoScene(description=scene_desc))
            
            return scenes[:3]  # Return first 3 scenes as in original workflow
            
        except Exception as e:
            logger.error(f"Error generating video prompts: {e}")
            raise

    def generate_video_clips(self, scenes: List[VideoScene], idea: VideoIdea) -> List[str]:
        """Generate video clips using Seedance AI"""
        logger.info("Generating video clips...")
        
        video_urls = []
        
        for i, scene in enumerate(scenes):
            logger.info(f"Generating clip {i+1}/{len(scenes)}")
            
            prompt = f"VIDEO THEME: {idea.idea} | WHAT HAPPENS IN THE VIDEO: {scene.description} | WHERE THE VIDEO IS SHOT: {idea.environment}"
            
            payload = {
                "aspect_ratio": "9:16",
                "duration": 10,
                "prompt": prompt
            }
            
            headers = {
                "Authorization": f"Bearer {self.wavespeed_api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(self.wavespeed_url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                prediction_id = result['data']['id']
                
                # Poll for completion with smart waiting
                logger.info(f"Waiting for clip {i+1} generation...")
                video_url = self._poll_wavespeed_completion(prediction_id, headers, f"clip {i+1}")
                video_urls.append(video_url)
                
                logger.info(f"Clip {i+1} generated successfully")
                
            except Exception as e:
                logger.error(f"Error generating clip {i+1}: {e}")
                raise
        
        return video_urls

    def _poll_wavespeed_completion(self, prediction_id: str, headers: dict, item_name: str, max_wait_time: int = 300) -> str:
        """Smart polling for Wavespeed AI completion"""
        result_url = f"https://api.wavespeed.ai/api/v3/predictions/{prediction_id}/result"
        start_time = time.time()
        poll_interval = 5  # Start with 5 second intervals
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(result_url, headers=headers)
                response.raise_for_status()
                
                result_data = response.json()
                
                # Log the full response for debugging
                if time.time() - start_time < 10:  # Only log first few responses
                    logger.info(f"{item_name} response: {json.dumps(result_data, indent=2)}")
                
                # Check different possible status locations
                status = result_data.get('status', 'unknown')
                if status == 'unknown':
                    # Try alternative status locations
                    status = result_data.get('data', {}).get('status', 'unknown')
                
                if status in ['succeeded', 'completed']:
                    logger.info(f"{item_name} completed successfully!")
                    return result_data['data']['outputs'][0]
                elif status == 'failed':
                    error_msg = result_data.get('error', 'Unknown error')
                    raise Exception(f"{item_name} generation failed: {error_msg}")
                elif status in ['starting', 'processing', 'pending', 'running']:
                    elapsed = int(time.time() - start_time)
                    logger.info(f"{item_name} still processing... ({elapsed}s elapsed)")
                    time.sleep(poll_interval)
                    # Increase poll interval gradually to avoid overwhelming the API
                    poll_interval = min(poll_interval + 2, 15)
                else:
                    elapsed = int(time.time() - start_time)
                    logger.info(f"{item_name} status: {status}, waiting... ({elapsed}s elapsed)")
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Polling request failed for {item_name}: {e}, retrying...")
                time.sleep(poll_interval)
        
        raise Exception(f"{item_name} generation timed out after {max_wait_time} seconds")

    def _poll_fal_completion(self, request_id: str, headers: dict, item_name: str, base_url: str, max_wait_time: int = 300) -> str:
        """Smart polling for Fal AI completion"""
        # Use the correct Fal AI status endpoint format
        status_url = f"https://queue.fal.run/fal-ai/mmaudio-v2/requests/{request_id}/status"
        start_time = time.time()
        poll_interval = 5
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(status_url, headers=headers)
                
                if response.status_code == 400:
                    # Check if it's actually an error or just "in progress"
                    try:
                        error_data = response.json()
                        if "Request is still in progress" in error_data.get('detail', ''):
                            # This is normal - request is still processing
                            elapsed = int(time.time() - start_time)
                            logger.info(f"{item_name} still processing... ({elapsed}s elapsed)")
                            time.sleep(poll_interval)
                            poll_interval = min(poll_interval + 2, 15)
                            continue
                        else:
                            # This is a real error
                            logger.error(f"Bad request for {item_name}: {response.text}")
                            logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
                            raise Exception(f"Bad request for {item_name}: {response.text}")
                    except:
                        # If we can't parse the response, treat as error
                        logger.error(f"Bad request for {item_name}: {response.text}")
                        raise Exception(f"Bad request for {item_name}: {response.text}")
                
                response.raise_for_status()
                
                result_data = response.json()
                status = result_data.get('status', 'unknown')
                
                # Log response for debugging
                if time.time() - start_time < 10:
                    logger.info(f"{item_name} status response: {json.dumps(result_data, indent=2)}")
                
                if status in ['completed', 'COMPLETED']:
                    logger.info(f"{item_name} completed successfully!")
                    
                    # Get the result from the response_url
                    if 'response_url' in result_data:
                        result_response = requests.get(result_data['response_url'], headers=headers)
                        result_response.raise_for_status()
                        result_content = result_response.json()
                        
                        # Handle different response structures for the actual result
                        if 'video' in result_content and 'url' in result_content['video']:
                            return result_content['video']['url']
                        elif 'video_url' in result_content:
                            return result_content['video_url']
                        elif 'output' in result_content and 'video' in result_content['output']:
                            return result_content['output']['video']['url']
                        else:
                            logger.error(f"Unexpected result structure for {item_name}: {json.dumps(result_content, indent=2)}")
                            raise Exception(f"Could not find video URL in result for {item_name}")
                    else:
                        # Fallback to checking the status response directly
                        if 'video' in result_data and 'url' in result_data['video']:
                            return result_data['video']['url']
                        elif 'video_url' in result_data:
                            return result_data['video_url']
                        elif 'output' in result_data and 'video' in result_data['output']:
                            return result_data['output']['video']['url']
                        else:
                            logger.error(f"Unexpected response structure for {item_name}: {json.dumps(result_data, indent=2)}")
                            raise Exception(f"Could not find video URL in response for {item_name}")
                elif status == 'failed':
                    error_msg = result_data.get('error', 'Unknown error')
                    raise Exception(f"{item_name} generation failed: {error_msg}")
                elif status in ['IN_QUEUE', 'IN_PROGRESS', 'queued', 'in_progress', 'processing']:
                    elapsed = int(time.time() - start_time)
                    logger.info(f"{item_name} still processing... ({elapsed}s elapsed)")
                    time.sleep(poll_interval)
                    poll_interval = min(poll_interval + 2, 15)
                else:
                    elapsed = int(time.time() - start_time)
                    logger.info(f"{item_name} status: {status}, waiting... ({elapsed}s elapsed)")
                    time.sleep(poll_interval)
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Polling request failed for {item_name}: {e}, retrying...")
                time.sleep(poll_interval)
        
        raise Exception(f"{item_name} generation timed out after {max_wait_time} seconds")

    def generate_asmr_sound(self, video_url: str, idea: VideoIdea) -> str:
        """Generate ASMR sound using Fal AI"""
        logger.info("Generating ASMR sound...")
        
        payload = {
            "prompt": f"ASMR Soothing sound effects. {idea.sound}",
            "duration": 10,
            "video_url": video_url
        }
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Making request to: {self.fal_audio_url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(self.fal_audio_url, json=payload, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                response.raise_for_status()
            
            result = response.json()
            logger.info(f"API response: {json.dumps(result, indent=2)}")
            request_id = result['request_id']
            
            # Poll for sound generation completion
            logger.info("Waiting for sound generation...")
            sound_url = self._poll_fal_completion(request_id, headers, "ASMR sound", "https://queue.fal.run/fal-ai/mmaudio-v2/requests/")
            
            logger.info("ASMR sound generated successfully")
            return sound_url
            
        except Exception as e:
            logger.error(f"Error generating ASMR sound: {e}")
            raise

    def merge_video_clips(self, video_urls: List[str], sound_urls: List[str] = None) -> str:
        """Merge video clips into final video using Fal AI FFmpeg API"""
        logger.info("Merging video clips...")
        
        # Create keyframes for video stitching
        video_keyframes = []
        for i, url in enumerate(video_urls):
            video_keyframes.append({
                "url": url,
                "timestamp": i * 10,  # Each clip is 10 seconds
                "duration": 10
            })
        
        # Create tracks array with video
        tracks = [
            {
                "id": "1",
                "type": "video",
                "keyframes": video_keyframes
            }
        ]
        
        # Add audio tracks for each clip if sound URLs are provided
        if sound_urls and any(sound_urls):
            logger.info("Adding ASMR sounds to final video...")
            audio_keyframes = []
            for i, sound_url in enumerate(sound_urls):
                if sound_url:  # Only add if sound URL exists
                    audio_keyframes.append({
                        "url": sound_url,
                        "timestamp": i * 10,  # Each sound matches its video clip
                        "duration": 10
                    })
            
            if audio_keyframes:  # Only add audio track if we have valid sound URLs
                tracks.append({
                    "id": "2",
                    "type": "audio",
                    "keyframes": audio_keyframes
                })
        
        payload = {
            "tracks": tracks
        }
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.fal_ffmpeg_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            request_id = result['request_id']
            
            # Poll for video rendering completion
            logger.info("Waiting for video rendering...")
            final_video_url = self._poll_fal_completion(request_id, headers, "video rendering", "https://queue.fal.run/fal-ai/ffmpeg-api/requests/")
            
            logger.info("Video clips merged successfully")
            return final_video_url
            
        except Exception as e:
            logger.error(f"Error merging video clips: {e}")
            raise

    def log_results(self, idea: VideoIdea, final_video_url: str):
        """Log the final results"""
        logger.info("Video generation completed!")
        
        data = {
            "idea": idea.idea,
            "caption": idea.caption,
            "production": idea.status,
            "environment_prompt": idea.environment,
            "sound_prompt": idea.sound,
            "final_output": final_video_url,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Final results: {json.dumps(data, indent=2)}")

    def run_pipeline(self):
        """Run the complete AI video generation pipeline"""
        logger.info("Starting AI video generation pipeline...")
        
        try:
            # Step 1: Generate creative video idea
            idea = self.generate_creative_video_idea()
            logger.info(f"Generated idea: {idea.idea}")
            
            # Step 2: Generate detailed video prompts
            scenes = self.generate_detailed_video_prompts(idea)
            logger.info(f"Generated {len(scenes)} video scenes")
            
            # Step 3: Generate video clips
            video_urls = self.generate_video_clips(scenes, idea)
            logger.info(f"Generated {len(video_urls)} video clips")
            
            # Step 4: Generate ASMR sounds for each clip
            sound_urls = []
            if video_urls:
                for i, video_url in enumerate(video_urls):
                    try:
                        logger.info(f"Generating ASMR sound for clip {i+1}/{len(video_urls)}")
                        sound_url = self.generate_asmr_sound(video_url, idea)
                        sound_urls.append(sound_url)
                        logger.info(f"Generated ASMR sound for clip {i+1}: {sound_url}")
                    except Exception as e:
                        logger.warning(f"ASMR sound generation failed for clip {i+1}: {e}")
                        logger.info(f"Continuing without sound for clip {i+1}...")
                        sound_urls.append(None)
            else:
                sound_urls = [None] * len(video_urls)
            
            # Step 5: Merge video clips with ASMR sounds
            final_video_url = self.merge_video_clips(video_urls, sound_urls)
            logger.info(f"Final video URL: {final_video_url}")
            
            # Step 6: Log final results
            self.log_results(idea, final_video_url)
            
            logger.info("Pipeline completed successfully!")
            return {
                "idea": idea,
                "scenes": scenes,
                "video_urls": video_urls,
                "sound_urls": sound_urls,
                "final_video_url": final_video_url
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

def main():
    """Main function to run the AI video generator"""
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
        return
    
    # Initialize and run the generator
    generator = AIVideoGenerator()
    result = generator.run_pipeline()
    
    print("\n" + "="*50)
    print("AI VIDEO GENERATION COMPLETED!")
    print("="*50)
    print(f"Idea: {result['idea'].idea}")
    print(f"Final Video URL: {result['final_video_url']}")
    print("="*50)

if __name__ == "__main__":
    main()
