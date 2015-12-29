
try:
    import GeoIP
except ImportError:
    GeoIP = None


def get_country_name(cc):
    if GeoIP is not None and cc in GeoIP.country_names:
        return GeoIP.country_names[cc]
    return None
