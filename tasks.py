from robocorp.tasks import task
from robocorp import browser, vault
from RPA.HTTP import HTTP
from RPA.Tables import Tables


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    slowmo=300
    orders = get_orders()

    open_robot_order_website()
    for order in orders:

        # Suljetaan evästeikkuna
        close_annoying_modal()

        # täytetään lomake
        fill_the_form(order)

        # tarkistetaan ja lähetetään tilaus
        preview_and_submit_order()


#######################################################################################        

def open_robot_order_website():

    # avataan tilaussivu
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():

    # Ladataan csv tiedosto 
    HTTP().download(
        url = "https://robotsparebinindustries.com/orders.csv",
        target_file="orders.csv",
        overwrite = True
        )
    
    # Palautetaan tiedot taulukkona hakemalla juuri ladattu orders.csv
    return Tables().read_table_from_csv("orders.csv")

def close_annoying_modal():
    page = browser.page()
    page.click("text=I guess so...")

def fill_the_form(order):
    page = browser.page()

    page.select_option('#head', order['Head']) # pää   
    page.locator(f'#id-body-{order['Body']}').check() # body
    page.fill('[placeholder="Enter the part number for the legs"]', order['Legs']) # jalat
    page.fill('#address', order['Address']) # osoite

def preview_and_submit_order():
    page = browser.page()

    page.click('#preview') # näytä robotin preview
    page.locator('#robot-preview').screenshot(path='output/robot_preview.png') # kuvakaappaus robotista
    page.click('#order') # lähetä tilaus

    page.wait_for_timeout(2000) # odota ennen error tarkistusta

    # tarkistetaan tuleeko erroreita. Käytetään whileä siltä varatlta että erroreita tulisi peräkkäin
    while page.locator(".alert.alert-danger").is_visible(): # loopataan niin kauan kun alert on näkyvissä
        page.click("#order")
        page.wait_for_timeout(2000)

    page.click('#order-another') 

