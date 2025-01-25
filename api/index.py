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
            # Parse URL parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            if 'url' not in query_params:
                self.send_response(400)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write('{"error": "Missing URL parameter"}'.encode('utf-8'))
                return
                
            url = query_params['url'][0]
            logger.info(f"Received transcript request for URL: {url}")
            
            # Call the youtube_transcript.py script
            result = subprocess.run(
                ["python", "youtube_transcript.py"],
                input=url,
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
                
            logger.info(f"Successfully fetched transcript for URL: {url}")
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(f'{{"transcript": {result.stdout}}}'.encode('utf-8'))
            
        except Exception as e:
            error_msg = f"Internal server error: {str(e)}"
            logger.error(error_msg)
            self.send_response(500)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "{error_msg}"}}'.encode('utf-8'))
