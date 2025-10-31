
import requests

def get_coords_for_location(api_key, location):
    """
    Get coordinates (latitude and longitude) for a given location using the Kakao Local Search API.
    """
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={location}"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    documents = response.json().get('documents')
    if not documents:
        return None, None
    
    # Extract latitude and longitude from the first result
    lon = documents[0].get('x')
    lat = documents[0].get('y')
    
    return lat, lon

def get_static_map_url(api_key, lat, lon, width=600, height=450):
    """
    Get a static map image URL from the Kakao Maps API.
    """
    if not lat or not lon:
        return None
        
    map_url = f"https://dapi.kakao.com/v2/map/staticmap?center={lat},{lon}&level=3&marker=true&markerpos={lat},{lon}&width={width}&height={height}"
    
    return map_url
