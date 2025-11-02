import requests
import logging

logger = logging.getLogger(__name__)

def get_coords_for_location(api_key, location):
    """
    Get coordinates (latitude and longitude) for a given location using the Kakao Local Search API.
    """
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={location}"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        documents = response.json().get('documents')
        
        if not documents:
            logger.warning(f"[KakaoMap API] No documents found for location: {location}")
            return None, None
        
        # Extract latitude and longitude from the first result
        lon = documents[0].get('x')
        lat = documents[0].get('y')
        
        if lat is None or lon is None:
            logger.warning(f"[KakaoMap API] Latitude or longitude not found in the first document for location: {location}")
            return None, None
            
        return lat, lon
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"[KakaoMap API] HTTP error occurred for location {location}: {http_err} - Response: {response.text}")
        return None, None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"[KakaoMap API] Request error occurred for location {location}: {req_err}")
        return None, None
    except Exception as e:
        logger.error(f"[KakaoMap API] An unexpected error occurred for location {location}: {e}")
        return None, None

def get_static_map_url(api_key, lat, lon, width=600, height=450):
    """
    Get a static map image URL from the Kakao Maps API.
    """
    if not lat or not lon:
        return None
        
    map_url = f"https://dapi.kakao.com/v2/map/staticmap?center={lat},{lon}&level=3&marker=true&markerpos={lat},{lon}&width={width}&height={height}"
    
    return map_url