from http.server import BaseHTTPRequestHandler
import logging
from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptAvailable,
    VideoUnavailable,
    TooManyRequests
)
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_video_id(video_id):
    """Validate YouTube video ID format"""
    if not video_id or len(video_id) != 11:
        return False
    return bool(re.match(r'^[0-9A-Za-z_-]{11}$', video_id))

def format_transcript(transcript):
    """Format transcript entries into readable text"""
    return "\n".join(
        f"[{entry['start']:.2f}] {entry['text']}"
        for entry in transcript
    )

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Parse query parameters from API request
            parsed_api_url = urlparse(self.path)
            query_params = parse_qs(parsed_api_url.query)
            logger.info(f"parsed_api_url: {parsed_api_url}")
            logger.info(f"query_params: {query_params}")
                
            if 'video_id' not in query_params:
                self.send_error_response(400, "Missing video_id parameter")
                return
                
            video_id = query_params['video_id'][0]
            
            # Validate video ID format
            if not validate_video_id(video_id):
                self.send_error_response(400, f"Invalid video ID format: {video_id}")
                return
            
            logger.info(f"Fetching transcript for video ID: {video_id}")
            
            try:
                # Get English transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                logger.info(f"transcript: {transcript}")

                formatted = format_transcript(transcript)
                logger.info(f"formatted: {formatted}")
                
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(f'{{"transcript": "{formatted}"}}'.encode('utf-8'))
                logger.info(f"Successfully fetched transcript for video ID: {video_id}")
                
            except TranscriptsDisabled:
                self.send_error_response(400, "Transcripts are disabled for this video")
            except NoTranscriptAvailable:
                self.send_error_response(400, "No transcript available for this video")
            except VideoUnavailable:
                self.send_error_response(404, "Video not found or unavailable")
            except TooManyRequests:
                self.send_error_response(429, "Too many requests, please try again later")
            except Exception as e:
                self.send_error_response(500, f"Failed to fetch transcript: {str(e)}")
                
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")

    def send_error_response(self, status_code, message):
        """Helper method to send error responses"""
        logger.error(f"Error {status_code}: {message}")
        self.send_response(status_code)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(f'{{"error": "{message}"}}'.encode('utf-8'))
