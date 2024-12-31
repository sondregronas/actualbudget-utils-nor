import requests


class HouseEstimate:
    def __init__(self, city, address, zip_code, percentage: int = 100):
        """
        Get the value of a house given its city, address and zip code
        """

        url = f"https://consumer-service.hjemla.no/public/properties/unit/{city}?streetaddress={address}&postalCode={zip_code}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        self.name = f'{data["response"]["address"]["streetName"]} {data["response"]["address"]["streetNumber"]}'
        mn = int(data["response"]["estimate"]["estimateMin"])
        mx = int(data["response"]["estimate"]["estimateMax"])

        self.min = int(mn * percentage / 100)
        self.max = int(mx * percentage / 100)
        self.median = int((self.min + self.max) / 2)

    def __str__(self):
        """
        Get the string representation of the object
        """
        return f"HouseEstimate(name={self.name}, min={self.min}, max={self.max}, median={self.median})"


def get_house_median_estimates(address_pairs: list[str]) -> dict[str, int]:
    """
    Get the median value of all the houses given their address and zip code
    """
    output = dict()
    for address_pair in address_pairs:
        address_pair, percentage = address_pair.split(":")
        city, address, zip_code = str(address_pair).split("=")
        percentage = int(percentage) if percentage else 100
        house = HouseEstimate(city, address, zip_code, percentage)
        output[house.name] = house.median
    return output
