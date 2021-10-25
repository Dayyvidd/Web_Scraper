from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import PySimpleGUI as Sg
import webbrowser
import time

layout = [
    [Sg.Text("Product URLS:")],
    [Sg.Button("Update List", key="-UPDATE-"), Sg.Button("Refresh", key="-REFRESH-")],
    [Sg.Listbox(values=[], enable_events=True, size=(60, 20), key="-URL LIST-")]
]

window = Sg.Window("High Demand Products", layout=layout)

fqdn = "https://www.bestbuy.com"


def open_browser(url):
    webbrowser.open(url)


# Fake_user_agent
ua = UserAgent()

# Selenium and web_driver options.
chrome_options = Options()
chrome_options.add_argument("user-agent=" + ua.random)
# "Headless" argument is so that selenium does not open the web browser when application is launched.
chrome_options.add_argument("--headless")
# This option waits until DOMContentLoaded event is returned.
chrome_options.page_load_strategy = "none"
driver = webdriver.Chrome(options=chrome_options)


def generate_page():
    # Get's desired URL using Chrome driver
    driver.get(
            "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory="
            "abcat0507002&id=pcat17071&iht=n&ks=960&list=y&qp=chipsetmanufacture_facet%3DChi"
            "pset%20Manufacturer~NVIDIA%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~"
            "NVIDIA%20GeForce%20RTX%203060%20Ti%5Egpusv_facet%3DGraphics%20Processing%20Unit%20"
            "(GPU)~NVIDIA%20GeForce%20RTX%203070%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)"
            "~NVIDIA%20GeForce%20RTX%203070%20Ti%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~"
            "NVIDIA%20GeForce%20RTX%203080%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%"
            "20RTX%203080%20Ti%5Egpusv_facet%3DGraphics%20Processing%20Unit%20(GPU)~NVIDIA%20GeForce%20RTX%203090&sc="
            "Global&st=categoryid%24abcat0507002&type=page&usc=All%20Categories"
            )
    # Assign URL's html code to a variable using page_source attribute
    html = driver.page_source
    # Using BS4 parse the source html using lxml and assign this to a variable
    soup = BeautifulSoup(html, 'lxml')
    # Use the find_all method to create a list of all occurrences of the specified tag (tag_name, {dictionary})
    graphic_cards = soup.find_all('div', {"class": "price-block"})

    # Function returns list
    return graphic_cards


def generate_urls():
    # Initialize empty list
    urls = []
    t0 = time.time()

    # Loop through items in list (using function call that returns a list)
    for card in generate_page():
        # The hyperlink we need is in the sibling prior to each of the elements in the html source code
        # so we initialize a variable with this value.
        information_block = card.previous_sibling
        # We need to find the specific html element in each element in the list that holds
        # the status of the product (ADD_TO_CART vs SOLD_OUT)
        availability = card.find("button", {"data-button-state": "SOLD_OUT"})

        # If the status is ADD_TO_CART the product is now in stock
        if availability is not None and availability["data-button-state"] == "SOLD_OUT":
            # We add the hyperlink of the product since it is in stock to a list named urls
            urls.append(fqdn + information_block.find("a")["href"])
    t1 = time.time()
    print(f"Url list took {t1 - t0} seconds.")
    # We return the list of urls
    return urls


generate_urls()

while True:
    event, values = window.read()

    if event == "-UPDATE-":
        window["-URL LIST-"].update(generate_urls())

    if event == "-URL LIST-":
        current_item = window["-URL LIST-"].get()
        open_browser(*current_item)

    if event == "-REFRESH-":
        window["-URL LIST-"].update([])
        generate_page()

    if event == Sg.WIN_CLOSED:
        break

window.close()





