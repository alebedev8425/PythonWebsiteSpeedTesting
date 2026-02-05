import time
import requests as req
import gspread as gc
from gspread.exceptions import APIError

#PageSpeedAPI key
API_KEY = ""

endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

query_params = {
    'url': 'https://speed.bluebeardecks.com', # the page to audit REPLACE LATER
    'key': API_KEY,           # generated API Key
    'strategy': 'mobile',                 # can be 'mobile' or 'desktop'
    'category': ['performance', 'seo']    # you can request multiple categories
}


# this function establishes if there is a connection to the google sheet and returns it if so
def handshake():
    try:
        acc = gc.service_account(filename='creds.json')
        # CHANGE THIS STRING BELOW TO NAME OF YOUR GOOGLE SHEET
        sh = acc.open('Current GHL Shinnova Home Speed metrics') 
        print("Connection Successful")
        return sh
    
    except APIError as e:  
        print(f"Google API Error: {e}")
        # here you could wait 60 seconds and try again
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def extract_speed_data(endpoint, query_params):
    # call the PageSpeed Insights API with passed url
    response = req.get(endpoint, params=query_params)

    # check the status code (200 means success)
    if response.status_code == 200:
        # parse JSON content into a Python dictionary
        data = response.json()
        report = data['lighthouseResult']

        # extract desired metrics
        score = report['categories']['performance']['score'] * 100
        lcp = report['audits']['largest-contentful-paint']['displayValue']
        cls = report['audits']['cumulative-layout-shift']['displayValue']
        tbt = report['audits']['total-blocking-time']['displayValue']
        #success message
        print("Data extraction successful")

        # return the extracted metrics
        return score, lcp, cls, tbt
    else:
        print(f"Failed for {query_params['url']} ({query_params['strategy']}): {response.status_code}")
        return None, None, None, None

# loop through all urls provided in a text file and insert data into google sheet
def loop_urls_insert_into_sheet(url_file, sheet):
    with open(url_file) as file:
        urls = [url.strip() for url in file.readlines()]
    # url loop
    for url in urls:
        print(f"Processing URL: {url}")
        
        # Get all mobile data first, google prioritizes mobile data first, so we use lcp, cls, and tbt for mobile
        query_params['strategy'] = 'mobile'
        query_params['url'] = url
        mobile_score, lcp, cls, tbt = extract_speed_data(endpoint, query_params)

        # get desktop score only
        query_params['strategy'] = 'desktop'
        desktop_score, _, _, _ = extract_speed_data(endpoint, query_params)

        # determine overall optimization status
        optimization_status = 'Good' if mobile_score and mobile_score >= 90 else 'Needs Work'

        #build row to append to sheet
        row = [url, mobile_score, desktop_score, lcp, cls, tbt, optimization_status]
        
        # append to sheet
        sheet.append_row(row)

        # sleep to be polite to the API (GHL pages are heavy)
        print(f"Finished {url}. Sleeping for 5 seconds...")
        time.sleep(5)


def main():
    sheet = handshake()
    if sheet:
        worksheet = sheet.sheet1  # Select the first sheet
        loop_urls_insert_into_sheet('pages.txt', worksheet)

if __name__ == "__main__":
    main()