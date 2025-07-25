## Importing libraries
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re

# Helper to remove emojis from location
def remove_emojis(text):
    if not text:
        return None
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()

## Website request and text extraction (with all corrections)
def extract_remoteok_jobs(keyword):
    url = f"https://remoteok.com/remote-{keyword}-jobs"
    request = requests.get(url, headers={"User-Agent": "Kimchi"})
    results = []

    if request.status_code == 200:
        soup = BeautifulSoup(request.text, "html.parser")
        jobs = soup.find_all("tr", class_="job")

        for job in jobs:
            link_tag = job.find("a", class_="preventLink")
            link = f"https://remoteok.com/{link_tag['href']}" if link_tag and link_tag.has_attr('href') else None

            company = job.find("h3", itemprop="name")
            job_title = job.find("h2", itemprop="title")
            location = job.find("div", class_="location")
            salary_div = job.find('div', class_='location tooltip')
            time_tag = job.find('time')
            tag_divs = job.find_all('div', class_='tag tag- action-add-tag')

            # Extract text
            company = company.string.strip() if company and company.string else None
            job_title_text = job_title.string.strip() if job_title and job_title.string else None

            # Remove emojis from location
            raw_location = location.string.strip() if location and location.string else None
            location_clean = remove_emojis(raw_location)

            # Clean salary - set to None if no number
            salary_raw = salary_div.text.strip() if salary_div else None
            salary_clean = remove_emojis(salary_raw) if salary_raw else None
            salary = salary_clean if salary_clean and any(char.isdigit() for char in salary_clean) else None


            # Extract date and time separately
            datetime_value = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
            date_posted, time_posted = (None, None)
            if datetime_value:
                try:
                    date_posted, time_posted = datetime_value.split("T")
                    time_posted = time_posted.split("+")[0]
                except:
                    date_posted, time_posted = datetime_value, None

            # Extract search tags
            searchkeys = [div.h3.text.strip() for div in tag_divs if div.h3] if tag_divs else None

            # Store all values including split date and cleaned fields
            job = {
                'link': link,
                'company': company,
                'position': job_title_text,
                'location': location_clean,
                'salary': salary,
                'date_posted': date_posted,
                'time_posted': time_posted,
                'searchkeys': searchkeys,
                'Job title': job_title_text
            }
            results.append(job)
    else:
        print(f"Can't get jobs for {keyword}. Status code: {request.status_code}")
    
    return results

## Initialize empty dataframe with updated column names
data = pd.DataFrame(columns=["link", "company", "position", "location", 'salary', 'date_posted', 'time_posted', 'searchkeys', 'Job title'])

## Keywords to look out for
keyword = [
    'Mongo', 'Python', 'Vue', 'Jira', 'SEO', 'Apache', 'Data Science', 'React Native', 'Machine learning', 'Social Media', 'Payroll', 'Wordpress', 'Director', 'Shopify', 'architecture', 'Objective C', 'Web', 'Scala'
]

## Loop through keywords and collect job data
for item in keyword:
    print(f'Going through {item}')
    time.sleep(3)  # delay to avoid hitting site too quickly
    info = extract_remoteok_jobs(item)
    print(f'Extracted items from {item}')
    df = pd.DataFrame(info)
    data = pd.concat([data, df], ignore_index=True)

## Save to Parquet 
data.to_parquet('remoteok.parquet', index=False)