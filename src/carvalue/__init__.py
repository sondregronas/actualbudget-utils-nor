from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class CarEstimate:
    """
    Get the estimated value of a car given its license plate

    :param license_plate: License plate of the car
    :ivar min: Minimum value of the car
    :ivar max: Maximum value of the car
    :ivar median: Median value of the car
    """

    def __init__(self, license_plate: str, percentage: int = 100):
        """
        Get the value of a car given its license plate

        :param license_plate: License plate of the car
        :param percentage: Percentage of the value to get (default 100)
        """
        url = f'https://regnr.no/{license_plate.upper()}'

        # 0: Heftelser, 1: Forhandlerpris, 2: Privatpris (min-max) 3: ..
        target_class = 'text-price'

        # If this isn't in the page, the license plate doesn't exist
        # This gets loaded when the price is loaded (otherwise it's just an SVG)
        subscript_class = 'subscript'

        with webdriver.Chrome() as s:
            s.get(url)
            try:
                # TODO: wait for SVG to disappear in the target_class instead of looking for a subscript class?
                WebDriverWait(s, 10).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, subscript_class)))
            except TimeoutException:
                raise ValueError(f'Could not load prices for license plate {license_plate}')
            elements = [element.text.replace(' ', '').replace('kr', '')
                        for element in s.find_elements(By.CLASS_NAME, target_class)]

            self.min = int(int(elements[2].split('-')[0]) * percentage / 100)
            self.max = int(int(elements[2].split('-')[1]) * percentage / 100)
            self.median = int((self.min + self.max) / 2)

    def __str__(self):
        """
        Get the string representation of the object

        :return: CarValue(min=..., max=..., median=...)
        """
        return f'CarEstimate(min={self.min}, max={self.max}, median={self.median})'


def get_car_median_estimates(license_plates: list[str]) -> dict[str, int]:
    """
    Get the median estimated value of a car given its license plate

    :param license_plates: List of license plates
    :return: Dictionary with license plates as keys and median values as values
    """
    output = dict()
    for license_plate in license_plates:
        reg = license_plate.split(':')[0] if ':' in license_plate else license_plate
        percentage = int(license_plate.split(':')[1]) if ':' in license_plate else 100
        output[reg] = CarEstimate(reg, percentage).median
    return output
