import sys
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()
    page.goto("http://localhost:5173")
    page.locator("//input[@type='text']").fill(" ".join(sys.argv[1:]))
    page.locator("//input[@type='text']").press('Enter')
    browser.close()
