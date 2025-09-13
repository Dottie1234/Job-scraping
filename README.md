# Cloud based Job scraping
## RemoteOK Job Scraping Pipeline
This project **automatically scrapes job listings from [RemoteOK](https://remoteok.com/)** for various tech-related keywords and stores the data in AWS S3. The entire pipeline is **fully automated and serverless** using AWS Lambda, EventBridge, Glue, and S3.

---

## Project Overview
* Scrapes job listings from RemoteOK on a scheduled basis (daily at 7 PM).
* Transforms the data into a structured Parquet file using Pandas.
* Uploads automatically to Amazon S3.
* Data catalogued in AWS Glue for querying with Athena (crawler runs daily at 8 PM).
* Zero manual intervention thanks to EventBridge scheduling.

---

## AWS Architecture

| Service         | Role in the Pipeline                                                             |
| --------------- | -------------------------------------------------------------------------------- |
| **AWS Lambda**  | Runs the Python scraping script, processes the data, and uploads to S3.          |
| **Amazon S3**   | Stores Parquet outputs partitioned by date.                                          |
| **EventBridge** | Automatically triggers Lambda at a scheduled interval (e.g., daily at midnight). |
| **AWS Glue**    | Crawls and catalogs S3 data so it can be queried with Athena.                    |

**Workflow:**
`EventBridge (7 PM) → Lambda (Scraper) → S3 (Parquet Storage) → Glue (8 PM Catalog) → Athena (Query)`

---

## How It Works

1. **Scheduled Trigger with EventBridge**
   * EventBridge runs the Lambda function automatically on a predefined schedule (daily).

2. **Lambda Scraper Function**
   * Scrapes job postings from RemoteOK using `requests` + `BeautifulSoup`.
   * Extracts company, title, location, salary, tags, and posting date.
   * Uses Pandas (via Lambda Layer) to create a clean Parquet file.

3. **Automatic Upload to S3**
   * Parquet is stored in S3 with a date-based key:
     ```
     s3://jobscraping/jobs/remoteok/YYYY-MM-DD.parquet
     ```

4. **AWS Glue Crawler**
* Automatically runs every day at 8 PM to detect new Parquet files.

* Updates the Glue Data Catalog for Athena queries.

---

## Lambda Function

* **Key Features:**

  * Scrapes multiple keywords at once.
  * Handles missing fields gracefully.
  * Outputs clean Parquet format.
  * Uploads automatically to S3.

* **Dependencies:**

  * `boto3`
  * `requests`
  * `beautifulsoup4`
  * `pandas` (provided as a Lambda Layer)

---

## Setup & Deployment

### 1. AWS Lambda

* Create a Lambda function and upload `lambda_function.py`.
* Add a **Lambda Layer** containing Pandas and other Python dependencies.
* Installed and zipped the dependencies that are not available in lambda

### 2. EventBridge Schedule

* Create an EventBridge rule with a CRON expression to trigger Lambda at 7 PM daily.

### 3. AWS Glue

* Point Glue Crawler to `s3://jobscraping/jobs/remoteok/`.
* Configure to run after each upload by 8pm or on a schedule.

---

## Data Schema

| Column           | Description                           |
| ---------------- | ------------------------------------- |
| link             | Direct link to the job posting.       |
| company          | Company name.                         |
| Job title        | Title of the position.                |
| location         | Job location.                         |
| salary           | Salary info (if available).           |
| datetime\_posted | ISO timestamp of when job was posted. |
| time posted      | Human-readable posting time.          |
| searchkeys       | Tags or keywords for the job posting. |

---

## Output file Example

```
s3://jobscraping/jobs/remoteok/2025-09-13.parquet
```

---

## Benefits

* **Fully Automated** — Entire process runs on schedule without manual triggering.
* **Serverless** — Scales automatically with no infrastructure to manage.
* **Cost-Effective** — Pay only for execution and  time
* **Queryable** — Data ready for Athena SQL analytics via Glue.

---

## Future Improvements

* Add CloudWatch logs + SNS notifications for error alerts.
* Add data validation or enrichment steps before upload.
* Add more websites to scrape

---

## Author

**Adelodun Gbanjubola**
* GitHub: [github.com/Dottie1234](https://github.com/Dottie1234)
* LinkedIn: [linkedin.com/in/adelodun-gbanjubola](https://linkedin.com/in/adelodun-gbanjubola)
