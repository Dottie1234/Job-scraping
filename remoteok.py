## Importign libraries
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd


## website request and text extraction
def extract_remoteok_jobs(keyword):
    url = f"https://remoteok.com/remote-{keyword}-jobs"

    #kimchi agent
    request = requests.get(url, headers={"User-Agent": "Kimchi"})
    results = []

    ## extract text when status code is 200
    if request.status_code == 200:
        
        # get html
        soup = BeautifulSoup(request.text, "html.parser")
        jobs = soup.find_all("tr", class_="job")

        #get texts
        for job in jobs:
            link_tag = job.find("a", class_="preventLink")
            link = f"https://remoteok.com/{link_tag['href']}" if link_tag and link_tag.has_attr('href') else None
        
            #extract job information
            company = job.find("h3", itemprop="name")
            job_title = job.find("h2", itemprop="title")
            location = job.find("div", class_="location")
        
            # extract salary
            salary_div = job.find('div', class_='location tooltip')
            salary = salary_div.text.strip() if salary_div else None
        
            # extract posted time
            time_tag = job.find('time')
            datetime_value = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
            time_posted = time_tag.text.strip() if time_tag else None
        
            #extract tags
            tag_divs = job.find_all('div', class_='tag tag- action-add-tag')
            searchkeys = [div.h3.text.strip() for div in tag_divs if div.h3] if tag_divs else None
        
            #  extract text values
            company = company.string.strip() if company and company.string else None
            job_title = job_title.string.strip() if job_title and job_title.string else None
            location = location.string.strip() if location and location.string else None

            # each item in a dictionary
            job = {
                  'link': link,
                  'company': company,
                  'Job title': job_title,
                  'location': location,
                  'salary': salary,
                  'datetime_posted': datetime_value,
                  'time posted': time_posted,
                  'searchkeys': searchkeys
              }
            results.append(job)
        ## else statement
        else:
            print("Can't get jobs.")
    return results

## converting to dataframe
data = pd.DataFrame(columns=["link", "company", "position", "location", 'salary', 'datetime_posted', 'time posted', 'searchkeys'])

# keywords to look out for to extract text
keyword = ['Mongo', 'Python', 'Vue', 'Jira', 'SEO', 'Apache', 'Data Science', 'React Native', 'Machine learning', 'Social Media', 'Payroll', 'Wordpress', 'Director', 'Shopify', 'architecture', 'Objective C', 'Web', 'Scala']

## going through the keywords for texts related to them
for item in keyword:
    print(f'going through {item}')
    time.sleep(20)
    info = extract_remoteok_jobs(item)
    print(f'extracted item from {item}')
    df = pd.DataFrame(info)
    data = pd.concat([data, df], ignore_index = True)

# Save data to csv
data.to_csv('remoteok.csv', index=False)