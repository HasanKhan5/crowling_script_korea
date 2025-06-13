|| Korea Tender Scraper ||

This Python project automates the extraction of tender data from a Korean government website (like bonghwa.go.kr) using Selenium, with special handling for pages that load content inside iframes.

Features
* GUI calendar to select scraping start date

* Crawls tender listings and navigates through iframe-based pages

* Extracts fields: title, notice number, organization, value, deadline, etc.

* Inserts data into a MySQL database (l2l_tenders_tbl, asia_tenders_tbl)

* Uploads tender documents to AWS S3

* Handles duplication checks, errors, and expired tenders

Iframe Handling
The scraper detects and switches to the iframe where the tender details are embedded before extracting content. Example iframe handling in Selenium:

# Code for Iframe Handling
iframe = driver.find_element(By.XPATH, '//iframe[@id="targetFrame"]')

driver.switch_to.frame(iframe)

- Now scrape inside the iframe
This ensures the script can reliably extract data even when content is not in the main DOM.

How to Run
python MainCalender.py

Notes

^ Ensure chromedriver is installed and in your PATH

^ DB and S3 credentials must be properly configured

^ The script is optimized for Korean tender sources (e.g., bonghwa.go.kr)
