"""
Professional API client for traffic sources
"""

import requests
import re
import time
import logging
import random
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import json

from src.models.models import TrafficConfig, APIType, CodeRequest
from src.core.config import config
from src.core.database import db

@dataclass
class APIResponse:
    """API response model"""
    success: bool
    code: str = ""
    error_message: str = ""
    processing_time: float = 0.0
    raw_response: str = ""

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if request can be made"""
        now = time.time()
        # Remove old requests
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        return len(self.requests) < self.max_requests
    
    def add_request(self) -> None:
        """Add a request to the limiter"""
        self.requests.append(time.time())

class TrafficAPIClient:
    """Professional API client for traffic sources"""
    
    def __init__(self):
        self.base_url = config.get('api_config.base_url', 'https://traffic-user.net')
        self.timeout = config.get('api_config.request_timeout', 30)
        self.max_retries = config.get('api_config.max_retries', 3)
        self.retry_delay = config.get('api_config.retry_delay', 2)
        self.user_agent = config.get('api_config.user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Rate limiter
        rate_limit_config = config.get('api_config.rate_limit', {})
        self.rate_limiter = RateLimiter(
            max_requests=rate_limit_config.get('requests_per_minute', 60),
            time_window=60
        )
        
        # Session for connection pooling
        self.session = self._create_session()
        
        # API token
        self.api_token = "c9463ee4a9d2abdcb9f9b7ac2e6a5acb"
        
        logging.info("TrafficAPIClient initialized")
    
    def _create_session(self) -> requests.Session:
        """Create configured requests session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configure adapters for retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def generate_code(self, traffic_config: TrafficConfig, user_id: int) -> APIResponse:
        """Generate code for given traffic configuration"""
        start_time = time.time()
        
        # Check rate limit
        if not self.rate_limiter.can_make_request():
            return APIResponse(
                success=False,
                error_message="Rate limit exceeded. Please try again later.",
                processing_time=time.time() - start_time
            )
        
        self.rate_limiter.add_request()
        
        try:
            if traffic_config.api_type == APIType.GET_MA:
                response = self._generate_ma_code(traffic_config)
            elif traffic_config.api_type == APIType.GET_MD:
                response = self._generate_md_code(traffic_config)
            else:
                response = APIResponse(
                    success=False,
                    error_message=f"Unsupported API type: {traffic_config.api_type}",
                    processing_time=time.time() - start_time
                )
            
            response.processing_time = time.time() - start_time
            
            # Log the request
            self._log_request(traffic_config, user_id, response)
            
            return response
            
        except Exception as e:
            logging.error(f"Error generating code for {traffic_config.name}: {e}")
            return APIResponse(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _generate_ma_code(self, config: TrafficConfig) -> APIResponse:
        """Generate MA type code"""
        try:
            # Step 1: Get initial data
            step1_response = self._make_request('GET', config.url)
            if not step1_response:
                return APIResponse(
                    success=False,
                    error_message="Failed to fetch initial data"
                )
            
            # Extract code from response
            match = re.search(config.regex_pattern, step1_response.text)
            if not match:
                return APIResponse(
                    success=False,
                    error_message="Could not extract code from response"
                )
            
            ma_code = match.group(1)
            
            # Step 2: Submit to API
            api_url = urljoin(self.base_url, "/layma")
            payload = {
                'token': self.api_token,
                'codexn': config.codexn,
                'url': config.url,
                'loaitraffic': config.loai_traffic,
                'ma': ma_code,
                'clk': config.clk
            }
            
            api_response = self._make_request('POST', api_url, data=payload)
            if not api_response:
                return APIResponse(
                    success=False,
                    error_message="Failed to submit to API"
                )
            
            # Parse response
            try:
                result = api_response.json()
                if result.get('success'):
                    return APIResponse(
                        success=True,
                        code=result.get('code', ''),
                        raw_response=api_response.text
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=result.get('message', 'Unknown API error'),
                        raw_response=api_response.text
                    )
            except json.JSONDecodeError:
                # Fallback to text parsing
                if "success" in api_response.text.lower():
                    return APIResponse(
                        success=True,
                        code=api_response.text.strip(),
                        raw_response=api_response.text
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message="Invalid API response format",
                        raw_response=api_response.text
                    )
                    
        except Exception as e:
            logging.error(f"Error in _generate_ma_code: {e}")
            return APIResponse(
                success=False,
                error_message=f"MA generation error: {str(e)}"
            )
    
    def _generate_md_code(self, config: TrafficConfig) -> APIResponse:
        """Generate MD type code"""
        try:
            # Step 1: Get initial data
            step1_response = self._make_request('GET', config.url)
            if not step1_response:
                return APIResponse(
                    success=False,
                    error_message="Failed to fetch initial data"
                )
            
            # Extract code from response
            match = re.search(config.regex_pattern, step1_response.text)
            if not match:
                return APIResponse(
                    success=False,
                    error_message="Could not extract code from response"
                )
            
            md_code = match.group(1)
            
            # Step 2: Submit to API
            api_url = urljoin(self.base_url, "/laymd")
            payload = {
                'token': self.api_token,
                'codexn': config.codexn,
                'url': config.url,
                'loaitraffic': config.loai_traffic,
                'md': md_code,
                'clk': config.clk
            }
            
            api_response = self._make_request('POST', api_url, data=payload)
            if not api_response:
                return APIResponse(
                    success=False,
                    error_message="Failed to submit to API"
                )
            
            # Parse response
            try:
                result = api_response.json()
                if result.get('success'):
                    return APIResponse(
                        success=True,
                        code=result.get('code', ''),
                        raw_response=api_response.text
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message=result.get('message', 'Unknown API error'),
                        raw_response=api_response.text
                    )
            except json.JSONDecodeError:
                # Fallback to text parsing
                if "success" in api_response.text.lower():
                    return APIResponse(
                        success=True,
                        code=api_response.text.strip(),
                        raw_response=api_response.text
                    )
                else:
                    return APIResponse(
                        success=False,
                        error_message="Invalid API response format",
                        raw_response=api_response.text
                    )
                    
        except Exception as e:
            logging.error(f"Error in _generate_md_code: {e}")
            return APIResponse(
                success=False,
                error_message=f"MD generation error: {str(e)}"
            )
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                # Add random delay to avoid being detected
                if attempt > 0:
                    delay = self.retry_delay * (2 ** (attempt - 1)) + random.uniform(0.5, 1.5)
                    time.sleep(delay)
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Check for successful response
                if response.status_code in [200, 201]:
                    return response
                elif response.status_code == 429:  # Rate limited
                    logging.warning(f"Rate limited on attempt {attempt + 1}")
                    if attempt < self.max_retries:
                        time.sleep(60)  # Wait longer for rate limit
                        continue
                else:
                    logging.warning(f"HTTP {response.status_code} on attempt {attempt + 1}: {url}")
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Timeout on attempt {attempt + 1}: {url}")
            except requests.exceptions.ConnectionError:
                logging.warning(f"Connection error on attempt {attempt + 1}: {url}")
            except Exception as e:
                logging.error(f"Request error on attempt {attempt + 1}: {e}")
            
            if attempt == self.max_retries:
                logging.error(f"Max retries exceeded for: {url}")
                break
        
        return None
    
    def _log_request(self, traffic_config: TrafficConfig, user_id: int, response: APIResponse) -> None:
        """Log the API request"""
        try:
            request = CodeRequest(
                user_id=user_id,
                traffic_type=traffic_config.name,
                success=response.success,
                error_message=response.error_message,
                generated_code=response.code,
                processing_time=response.processing_time
            )
            
            db.log_code_request(request)
            
        except Exception as e:
            logging.error(f"Error logging request: {e}")
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self._make_request('GET', self.base_url)
            return response is not None and response.status_code == 200
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, any]:
        """Get API health status"""
        try:
            start_time = time.time()
            is_healthy = self.test_connection()
            response_time = time.time() - start_time
            
            return {
                'healthy': is_healthy,
                'response_time': response_time,
                'base_url': self.base_url,
                'rate_limit_status': {
                    'requests_made': len(self.rate_limiter.requests),
                    'max_requests': self.rate_limiter.max_requests,
                    'time_window': self.rate_limiter.time_window
                }
            }
        except Exception as e:
            logging.error(f"Error getting health status: {e}")
            return {
                'healthy': False,
                'error': str(e)
            }

# Global API client instance
api_client = TrafficAPIClient()
