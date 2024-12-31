import requests


class CarEstimate:
    def __init__(self, license_plate: str, percentage: int = 100):
        """
        Get the value of a car given its license plate
        """
        url = f"https://regnr.no/api/pricing?query={license_plate.upper()}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if not data["estimate"]:
            raise ValueError(f"Could not find estimate for license plate {license_plate}")

        element_with_dash = data["estimate"].replace(" ", "")

        self.min = int(int(element_with_dash.split("-")[0]) * percentage / 100)
        self.max = int(int(element_with_dash.split("-")[1]) * percentage / 100)
        self.median = int((self.min + self.max) / 2)

    def __str__(self):
        """
        Get the string representation of the object

        :return: CarValue(min=..., max=..., median=...)
        """
        return f"CarEstimate(min={self.min}, max={self.max}, median={self.median})"


def get_car_median_estimates(license_plates: list[str]) -> dict[str, int]:
    """
    Get the median estimated value of a car given its license plate

    :param license_plates: List of license plates
    :return: Dictionary with license plates as keys and median values as values
    """
    output = dict()
    for license_plate in license_plates:
        reg = license_plate.split(":")[0] if ":" in license_plate else license_plate
        percentage = int(license_plate.split(":")[1]) if ":" in license_plate else 100
        output[reg] = CarEstimate(reg, percentage).median
    return output
