import re
import xml.etree.ElementTree as Element

import requests

from configuration import URL,HEADERS,ALL_CATEGORIES

ENCODING = 'utf-8'
CATEGORY_TAG = 'CategoryArray/Category'


def remove_namespace(string):
    """Removes the namespace attribute from XML string.
    Args:
        string - str, the XML returned from Ebay API
    """
    return re.sub(' xmlns="[^"]+"', '', string, count=1)

def get_categories():
    """Fetches the categories from Ebay API.
    """
    try:
        print('Contacting Ebay GetCategories API...')

        request = requests.post(URL, data=ALL_CATEGORIES, headers=HEADERS)
        response = request.content
        response = response.decode(ENCODING)
        # parse XML with namespaces
        response = remove_namespace(response)
        root = Element.fromstring(response)

        categories = root.findall(CATEGORY_TAG)
        return categories

    except requests.ConnectionError:
        print('Check your internet connection status and try again')
        exit(1)
    except requests.exceptions.RequestException as error:
        print(error)
        exit(1)

if __name__ == '__main__':
    categories = get_categories()
    for category in categories:
        print(category.find('CategoryID').text, category.find('CategoryParentID').text)