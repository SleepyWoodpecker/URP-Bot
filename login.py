from playwright.sync_api import BrowserContext, Browser
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())


def get_login_details(browser: Browser, config: dict[str, str | int]) -> bool:
    """
    Runs the main screenshotting script

    Parameters:
        playwright - the playwright object, preferably passed in by context
    """
    if not os.path.exists(config["login_details_path"]):
        login_context = browser.new_context()

        if not _login(context=login_context, config=config):
            return False

        login_context.close()

    return True


def _login(context: BrowserContext, config: dict[str, str | int]) -> bool:
    """
    Interacts with the UCLA logon page, there is currently no way to bypass the 2FA, unfortunately

    @param context: a new browser context to perform the login on
    """
    page = context.new_page()
    page.goto(config["login_url"])
    page.wait_for_selector("form")

    # input username and password
    username_box = page.query_selector("#logon")
    if not username_box:
        return False

    password_box = page.query_selector("#pass")
    if not password_box:
        return False

    username_box.fill(os.getenv("USERNAME"))
    password_box.fill(os.getenv("PASSWORD"))

    # click login
    page.query_selector("button.primary-button").click()

    # give time to approve DUO request
    page.wait_for_timeout(config["timeout"]["wait_for_2FA"])

    context.storage_state(path=config["login_details_path"])
    page.close()
