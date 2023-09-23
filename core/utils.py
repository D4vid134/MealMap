import datetime
import json
import random
import requests
from geopy.distance import geodesic
import concurrent.futures

GOOGLE_API_KEY = "HIDDEN"

def fetch_json_data(url):
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(e)
        return None

def extract_random_restaurant(json_data):
    data = json.loads(json_data)
    results_array = data.get("results", [])

    if not results_array:
        # Using a dict instead of the model instance to avoid database-related operations
        return {
            "name": "NO RESULTS PLEASE INCREASE DISTANCE",
            "rating": 5.0,
            "open_now": False,
            "lat": 0.0,
            "lng": 0.0,
            "place_id": "1",
            "formatted_address": "1"
        }

    random_result = random.choice(results_array)

    name = random_result.get("name", "")
    rating = random_result.get("rating", 0.0)
    open_now = random_result.get("opening_hours", {}).get("open_now", False)
    location = random_result.get("geometry", {}).get("location", {})
    lat = location.get("lat", 0.0)
    lng = location.get("lng", 0.0)
    place_id = random_result.get("place_id", "")
    formatted_address = random_result.get("formatted_address", "")

    return {
        "name": name,
        "rating": rating,
        "open_now": open_now,
        "lat": lat,
        "lng": lng,
        "place_id": place_id,
        "formatted_address": formatted_address
    }
    
def get_all_restaurants(json_data):
    data = json.loads(json_data)
    results_array = data.get("results", [])
    
    if not results_array:
        return [
            {
            "name": "NO RESULTS",
            "rating": 5.0,
            "open_now": False,
            "lat": 0.0,
            "lng": 0.0,
            "place_id": "1",
            "formatted_address": "1",
            }
        ]

    all_restaurants = []

    for result in results_array:
        name = result.get("name", "")
        rating = result.get("rating", 0.0)
        open_now = result.get("opening_hours", {}).get("open_now", False)
        location = result.get("geometry", {}).get("location", {})
        lat = location.get("lat", 0.0)
        lng = location.get("lng", 0.0)
        place_id = result.get("place_id", "")
        formatted_address = result.get("formatted_address", "")

        restaurant = {
            "name": name,
            "rating": rating,
            "open_now": open_now,
            "lat": lat,
            "lng": lng,
            "place_id": place_id,
            "formatted_address": formatted_address
        }
        all_restaurants.append(restaurant)

    return all_restaurants
    
def get_number_of_results(json_data):
    data = json.loads(json_data)
    results_array = data.get("results", [])
    return len(results_array)

def get_specific_restaurant(name, address, keywords):
    json_data = fetch_json_data(f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=restaurant%20{name}%20{address}%20{keywords}&inputtype=textquery&fields=place_id,name,rating,formatted_address,geometry&key={GOOGLE_API_KEY}")
    data = json.loads(json_data)
    results_array = data.get("candidates", [])

    if not results_array:
        return {
            "name": "NO RESULTS",
            "rating": 5.0,
            "open_now": False,
            "lat": 0.0,
            "lng": 0.0,
            "place_id": "1",
            "formatted_address": "1"
        }

    result = results_array[0]

    name = result.get("name", "")
    rating = result.get("rating", 0.0)
    open_now = result.get("opening_hours", {}).get("open_now", False)
    location = result.get("geometry", {}).get("location", {})
    lat = location.get("lat", 0.0)
    lng = location.get("lng", 0.0)
    place_id = result.get("place_id", "")
    formatted_address = result.get("formatted_address", "")

    return {
        "name": name,
        "rating": rating,
        "open_now": open_now,
        "lat": lat,
        "lng": lng,
        "place_id": place_id,
        "formatted_address": formatted_address
    }

def get_distance_between(coord1, coord2):
    return round(geodesic(coord1, coord2).miles,2)

def get_restaurant_details(place_id):
    json_data = fetch_json_data(f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={GOOGLE_API_KEY}")
    data = json.loads(json_data)
    result = data.get("result", {})
    name = result.get("name", "")
    address = result.get("formatted_address", "")
    weekday_text = result.get("opening_hours", {}).get("weekday_text", [])
    delivery = result.get("delivery", False)
    pickup = result.get("pickup", False)
    dinein = result.get("dinein", False)
    phone_number = result.get("formatted_phone_number", "")
    photo_references = []
    for photo in result.get("photos", []):
        photo_ref = photo.get("photo_reference")
        if photo_ref:
            photo_references.append(photo_ref)
    rating = result.get("rating", 0.0)
    reviews = result.get("reviews", [])
    for review in reviews:
        review["time"] = datetime.datetime.fromtimestamp(int(review["time"]))
    website = result.get("website", "")
    place_id = result.get("place_id", "")
    
    return {
        "name": name,
        "address": address,
        "weekday_text": weekday_text,
        "delivery": delivery,
        "pickup": pickup,
        "dinein": dinein,
        "phone_number": phone_number,
        "photo_references": photo_references,
        "rating": rating,
        "reviews": reviews,
        "website": website,
        "place_id": place_id
    }
    
def get_filtered_restaurants_concurrently(nearby_restaurants, user_location_coords, min_rating):
    
    def get_restaurant_extra_details(restaurant):
        if restaurant['rating'] < min_rating:
            return None
        restaurant_location_coords = (restaurant['lat'], restaurant['lng'])
        restaurant['distance'] = get_distance_between(user_location_coords, restaurant_location_coords)
        restaurant['details'] = get_restaurant_details(restaurant['place_id'])
        return restaurant

    filtered_restaurants = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(get_restaurant_extra_details, nearby_restaurants)
        for result in results:
            if result:
                filtered_restaurants.append(result)
    return filtered_restaurants
    
