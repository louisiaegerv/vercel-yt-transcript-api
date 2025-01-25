from http.server import BaseHTTPRequestHandler
import subprocess
import logging
from urllib.parse import parse_qs, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Parse query parameters from API request
            parsed_api_url = urlparse(self.path)
            query_params = parse_qs(parsed_api_url.query)
            
            if 'video_id' not in query_params:
                self.send_response(400)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write('{"error": "Missing video_id parameter"}'.encode('utf-8'))
                return
                
            video_id = query_params['video_id'][0]
            
            # Validate video ID format
            if not video_id or len(video_id) != 11:
                raise ValueError(f"Invalid video ID: {video_id}")
            
            logger.info(f"Received video ID: {video_id}")
            
            # Call the youtube_transcript.py script
            result = subprocess.run(
                ["python", "youtube_transcript.py"],
                input=video_id,
                text=True,
                capture_output=True
            )
            
            if result.returncode != 0:
                error_msg = f"Error fetching transcript: {result.stderr}"
                logger.error(error_msg)
                self.send_response(400)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(f'{{"error": "{error_msg}"}}'.encode('utf-8'))
                return
                
            logger.info(f"Successfully fetched transcript for video ID: {video_id}")
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(f'{{"transcript": "{result.stdout.strip()}"}}'.encode('utf-8'))
            
        except Exception as e:
            error_msg = f"Internal server error: {str(e)}"
            logger.error(error_msg)
            self.send_response(500)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "{error_msg}"}}'.encode('utf-8'))
