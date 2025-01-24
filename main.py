from playwright.sync_api import sync_playwright, Playwright, TimeoutError
from login.login import get_login_details
import json


# TODO: add retry for login fails


def run(playwright: Playwright, config: dict[str, str | int]) -> None:
    firefox = playwright.firefox
    browser = firefox.launch(headless=False)

    if not get_login_details(browser=browser, config=config):
        return Exception("There was an error logging in")

    context = browser.new_context(storage_state=config["login_details_path"])
    page = context.new_page()

    page.goto(config["login_url"])
    page_no = 1

    urls_to_visit = []

    try:
        # get all the opportunities available
        while True:
            page.wait_for_selector("#tdr_content")
            all_listings = page.query_selector_all("div.opportunity-card")

            # stop when there are no more listings
            if not all_listings:
                break

            for listing in all_listings:
                listing_url = listing.query_selector("a[href]").get_attribute("href")
                urls_to_visit.append(listing_url)

            page_no += 1
            page.goto(f"{config['login_url']}/?page={page_no}")

        for url in urls_to_visit:
            page.goto(f"https://urp.my.ucla.edu{url}")
            page.wait_for_selector("#tdr_content_content")

            content = page.query_selector("body").inner_text()
            print(content)

    except TimeoutError:
        page.screenshot(path="timeout_error.png", full_page=True)
        print("Scraper timed out!")


if __name__ == "__main__":
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

        with sync_playwright() as playwright:
            run(playwright=playwright, config=config)
