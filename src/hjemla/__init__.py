from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class HouseEstimate:
    """
    Get the estimated value of a house given its hjemla URL
    """

    def __init__(self, hjemla_url: str, percentage: int = 100):
        """
        Get the value of a house given its hjemla URL
        :param hjemla_url: URL of the house where the value is located (Se mer modal)
                           Example: https://www.hjemla.no/boligkart?search=lat_lon_addresse-1_1234_Postnummer&z=16&showPanel=true&unit=H1234
        :param percentage: Percentage of the value to get (default 100)
        """
        # X,X - X,X millioner
        target_class = 'hjemla-estimate'

        with webdriver.Chrome() as s:
            s.get(hjemla_url)
            try:
                WebDriverWait(s, 10).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, target_class)))
            except TimeoutException:
                raise ValueError(f'Could not load prices for url {hjemla_url}')
            estimate_string = s.find_elements(By.CLASS_NAME, target_class)[0]

            self.name = s.find_elements(By.TAG_NAME, 'h1')[0].find_elements(By.TAG_NAME, 'span')[0].text

            mn, mx = estimate_string.text.replace(' ', '').split('millioner')[0].split('-')

            million = mn.split(',')[0]
            thousands = mn.split(',')[1]
            self.min = int(int(f'{million}{thousands:0<6}') * percentage / 100)

            million = mx.split(',')[0]
            thousands = mx.split(',')[1]
            self.max = int(int(f'{million}{thousands:0<6}') * percentage / 100)
            self.median = int((self.min + self.max) / 2)

    def __str__(self):
        """
        Get the string representation of the object

        :return: HouseEstimate(name=..., min=..., max=..., median=...)
        """
        return f'HouseEstimate(name={self.name}, min={self.min}, max={self.max}, median={self.median})'


def get_house_median_estimates(hjemla_urls: list[str]) -> dict[str, int]:
    """
    Get the median value of all the houses given their hjemla URLs (and percentages with a : separator)

    :param hjemla_urls: List of URLs of the houses where the values are located (Se mer modal)
    :return: Dictionary of house names and their median values
    """
    output = {}
    for hjemla_url in hjemla_urls:
        host = hjemla_url.split('https://')[1]
        url = host.split(':')[0] if ':' in host else host
        percentage = int(host.split(':')[-1]) if ':' in host else 100
        house = HouseEstimate(f'https://{url}', percentage)
        output[house.name] = house.median
    return output
