# the boto file for the lambda 
import boto3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time

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
            salary = salary_div.text.strip() if salary_div else None

            time_tag = job.find('time')
            datetime_value = time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else None
            time_posted = time_tag.text.strip() if time_tag else None

            tag_divs = job.find_all('div', class_='tag tag- action-add-tag')
            searchkeys = [div.h3.text.strip() for div in tag_divs if div.h3] if tag_divs else None

            company = company.string.strip() if company and company.string else None
            job_title = job_title.string.strip() if job_title and job_title.string else None
            location = location.string.strip() if location and location.string else None

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
    return results



def lambda_handler(event, context):
    try:
        keywords = ['Mongo', 'Python', 'Vue', 'Jira', 'SEO', 'Apache', 'Data Science', 'React Native',
                    'Machine learning', 'Social Media', 'Payroll', 'Wordpress', 'Director', 'Shopify',
                    'architecture', 'Objective C', 'Web', 'Scala']

        data = pd.DataFrame(columns=["link", "company", "Job title", "location", 'salary', 'datetime_posted', 'time posted', 'searchkeys'])

        for item in keywords:
            info = extract_remoteok_jobs(item)
            df = pd.DataFrame(info)
            data = pd.concat([data, df], ignore_index=True)

        # Save CSV to /tmp (only writable dir in Lambda)
        file_path = "/tmp/remoteok.csv"
        data.to_csv(file_path, index=False)

        time.sleep(3)

        # Upload to S3
        s3 = boto3.client('s3')
        bucket_name = "jobscraping" 
        today = datetime.today().strftime('%Y-%m-%d')
        s3_key = f"jobs/remoteok/{today}.csv"
        s3.upload_file(file_path, bucket_name, s3_key)

        return {
            "statusCode": 200,
            "body": f"✅ Uploaded to s3://{bucket_name}/{s3_key}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }
