from math import radians, cos, sin, asin, sqrt
from geopy.geocoders import Nominatim



def get_coordinates(address):
    print(f'Inside get_coordinates path: {address}')
    # address = '1-6-4 Fukushima, Fukushima-ku, Osaka, 553-0003, Japan'
    try:
        geolocator = Nominatim(user_agent="mytesteapp2232")
        location = geolocator.geocode(address, timeout=10) ##"175 5th Avenue NYC"
        return (location.latitude, location.longitude)

    except:
        return []
    

def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    print(lon1, lat1, lon2, lon1)
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r


