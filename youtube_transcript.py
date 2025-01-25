from youtube_transcript_api import YouTubeTranscriptApi
import re

import logging
logger = logging.getLogger(__name__)

def get_video_id(url):
    """Extract and validate YouTube video ID from various URL formats"""
    patterns = [
        r'(?:v=|\/v\/|embed\/|youtu.be\/)([0-9A-Za-z_-]{11})',  # Standard URL formats
        r'^([0-9A-Za-z_-]{11})$'  # Direct video ID
    ]
    
    logger.debug(f"Parsing URL: {url}")
    logger.debug(f"Original URL length: {len(url)} characters")
    
    # Remove URL encoding and extra spaces
    clean_url = url.strip().replace('%3A', ':').replace('%2F', '/')
    logger.debug(f"Cleaned URL: {clean_url}")
    
    for pattern in patterns:
        match = re.search(pattern, clean_url)
        if match:
            video_id = match.group(1)
            logger.debug(f"Pattern '{pattern}' matched. Extracted ID: {video_id}")
            
            # Strict validation
            if len(video_id) != 11:
                logger.error(f"Invalid ID length: {len(video_id)} characters")
                return None
                
            if not re.match(r'^[0-9A-Za-z_-]{11}$', video_id):
                logger.error(f"Invalid characters in ID: {video_id}")
                return None
                
            logger.info(f"Valid video ID found: {video_id}")
            return video_id
            
    logger.error(f"No valid video ID found. Failed URL: {clean_url}")
    logger.debug(f"Scanned URL parts: {clean_url.split('/')}")
    return None

def get_transcript(video_id):
    try:
        # Get English transcript by default
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def format_transcript(transcript):
    # Format the transcript into readable text
    formatted = []
    for entry in transcript:
        formatted.append(f"[{entry['start']:.2f}] {entry['text']}")
    return "\n".join(formatted)

import sys

def main():
    # Read URL from stdin
    url = sys.stdin.read().strip()
    
    if not url:
        print("No URL provided")
        return
    
    video_id = get_video_id(url)
    
    if not video_id:
        print("Invalid YouTube URL")
        return
    
    transcript = get_transcript(video_id)
    if transcript:
        print(format_transcript(transcript))

if __name__ == "__main__":
    main()
