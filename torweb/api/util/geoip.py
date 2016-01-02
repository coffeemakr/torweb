
try:
    import GeoIP
except ImportError:
    GeoIP = None


def get_country_name(country_code):
    '''
    Returns the country name form an existing code
    '''
    if GeoIP is not None and country_code in GeoIP.country_names:
        return GeoIP.country_names[country_code]
    return None
