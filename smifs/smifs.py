import requests
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from .smifsbot import get_reports
import logging
logger = logging.getLogger(__name__)
from stockutils import print_table
fetchfile=True
def fetch_smifs_reports(
    lastdate: datetime,
    key: str
) -> Tuple[List[Dict[str, str]], Optional[datetime]]:
    global fetchfile
    base_url = (
        "https://smifs.com/api/{key}"
        "?pagination%5Bpage%5D={page}"
        "&pagination%5BpageSize%5D=30"
        "&sort=publish_date%3Adesc&populate=*"
    )
    print("With key",key)
    results = []
    page = 1
    first_published_at = None

    while True:
        url = base_url.format(key=key, page=page)
        print("From fetch_smifs_reports",url)
        reports = get_reports(url,fetchfile)
        if not reports:
            break
        # Save publishedAt of very first row only
        if first_published_at is None:
            first_row = reports[0]
            first_pub = first_row.get("publishedAt")
            logger.info("Lastest report in this page %s",first_pub)
            if first_pub:
                first_published_at = datetime.fromisoformat(
                    first_pub.replace("Z", "+00:00")
                ).date()
        stop_fetching = False

        for report in reports:
            published_at = report.get("publishedAt")
            
            if not published_at:
                continue

            published_dt = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            ).date()
            c=(published_dt- lastdate).days
            if c <=0 :
                stop_fetching = True
                break
            tres={
                "Company": report.get("Title").split('-')[0].strip(),
                "report-date": published_dt,
                "broker":"SMIFS",
                "link":"https://smifs.com"+report.get("upload_file").get("url"),
                "site":"smifs"
              }
            if key=="icrs":
                tres["recommendation"]="initiating"
            if key=="sector-reports":
                tres['company']=tres['Company'] #sector key is company 
            results.append(tres)

        if stop_fetching:
            break

        last_report = reports[-1]
        last_published = last_report.get("publishedAt")

        if last_published:
            last_dt = datetime.fromisoformat(
                last_published.replace("Z", "+00:00")
            ).date()

            if last_dt <= lastdate:
                break
        print(results)
        page += 1

    return results, first_published_at


def fetch_multiple_smifs_reports(
    lastdate: datetime,
    keys: List[str]


) -> Tuple[
     List[Dict[str, str]],
    Optional[datetime]
]:
    all_results =[] 
    most_recent_published_at = lastdate

    for key in keys:
        try:
            reports, first_published_at = fetch_smifs_reports(
                lastdate,
                key
            )
        except Exception:
            reports = []
            first_published_at = None
        logger.info("New set of reports for key %s",key)
        print_table(reports,logger)
        all_results.extend(reports)

        if first_published_at is None:
            continue

        if (
            most_recent_published_at is None
            or first_published_at > most_recent_published_at
        ):
            most_recent_published_at = first_published_at

    return all_results, most_recent_published_at



def smifs_main(lastdate):
 keys=['result-updates','icrs']
# keys=['result-updates']
 reports,ldate=fetch_multiple_smifs_reports(lastdate,keys)
 sector,lsdate=fetch_multiple_smifs_reports(lastdate,['sector-reports'])
 print(sector)
 print(ldate,lsdate)
 if ldate < lsdate:
     ldate=lsdate
 return reports,sector,ldate
