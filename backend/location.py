import geocoder

def get_location():
    """Get user's current location using IP geolocation"""
    g = geocoder.ip('me')
    if g.ok:
        return g.lat, g.lng, g.city
    raise Exception("Could not determine location")