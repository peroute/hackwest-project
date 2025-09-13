import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

# Define categories with their URLs
categories = {
    "Mental Health ": [
        "https://www.depts.ttu.edu/scc/self-help-resources/mindspa/",
        "https://www.depts.ttu.edu/studenthealth/",
        "https://www.depts.ttu.edu/studentengagement/mentortech/MentorTech.php",
        "https://www.depts.ttu.edu/studenthealth/includes/MyTeamCare/",
        "https://www.depts.ttu.edu/rise/smhc.php",
        "https://www.depts.ttu.edu/scc/treatment-services/brief-individual-counseling/index.php ",
        "https://www.depts.ttu.edu/scc/treatment-services/group-therapy/",
        "https://www.depts.ttu.edu/hs/mft/",
        "https://www.depts.ttu.edu/scc/tao/index.php"
        ],
    "Physical Health ": [
        "https://www.depts.ttu.edu/studenthealth/",
        "https://www.texastechphysicians.com/",
        "https://www.depts.ttu.edu/recreation/"
        # add more URLs
    ],
    "Education and Academic Help ": [
        "http://depts.ttu.edu/provost/aiss/learning-center/",
        "https://www.depts.ttu.edu/provost/aiss/supplemental-instruction/",
        "https://www.depts.ttu.edu/provost/uwc/",
        "https://www.depts.ttu.edu/careercenter/",
        "https://www.depts.ttu.edu/library/",
        "https://www.depts.ttu.edu/library/coursereserve/",
        "https://www.depts.ttu.edu/library/oer/index.php"      
                                     
        ],
    "Wellness" : [
        "https://www.depts.ttu.edu/sds/",
        "https://www.depts.ttu.edu/rise/",
        "https://www.depts.ttu.edu/hs/csa/",
        "https://www.depts.ttu.edu/rise/RaiderRestart.php",
        "https://www.depts.ttu.edu/dos/",
        "https://www.depts.ttu.edu/access-engagement/",
        "https://www.depts.ttu.edu/scc/treatment-services/manage-your-mood/index.php",
    ],
    "Emergencies" : [
        "https://www.depts.ttu.edu/ttpd/",
        "https://www.depts.ttu.edu/scc/crisis-intervention-services/",
        "https://www.depts.ttu.edu/titleix/",
        "https://www.depts.ttu.edu/studentconduct/",
        "https://www.depts.ttu.edu/raiderrelief/"
    ],
    "Travel" : [
        "https://www.depts.ttu.edu/parking/InformationFor/MobilitySolutions/RaiderRide.php"
    ],
    "Food" : [
        "https://www.depts.ttu.edu/raiderrelief/foodpantry.php",
        "https://www.depts.ttu.edu/hospitality/dining_hours.php",
        "https://www.depts.ttu.edu/hospitality/Transact.php"
    ],
    "Legal": ["https://www.depts.ttu.edu/sls/"],
    "Financial" : [
        "https://www.depts.ttu.edu/r2b/",
        "https://www.depts.ttu.edu/studentbusinessservices/"
        ],
    "Fitness":[
        "https://www.depts.ttu.edu/recreation/UREC_DEPT_LANDING_PAGES/OPC_LANDING.php",
        "https://www.depts.ttu.edu/recreation/intramurals/imregistration.php",
        "https://www.depts.ttu.edu/recreation/UREC_DEPT_LANDING_PAGES/SPORT_SPC_LANDING.php",
        "https://www.depts.ttu.edu/recreation/UREC_DEPT_LANDING_PAGES/FITWELL_LANDING.php",
        "https://www.depts.ttu.edu/recreation/UREC_DEPT_LANDING_PAGES/AQ_LANDING.php",
        "https://www.depts.ttu.edu/recreation/UREC_DEPT_LANDING_PAGES/SYP_Landing.php"
    ],
    "Technology" : [ 
        "https://www.depts.ttu.edu/library/make/index.php",
        "https://www.depts.ttu.edu/library/access-services/anatomy-models.php",
        "https://www.depts.ttu.edu/library/podcast-studio/index.php",
        "https://www.depts.ttu.edu/library/crossroadsrecordingstudio/index.php",
        "https://www.depts.ttu.edu/research/research-park/"
    ],
    "Entertainment" : [
        "https://www.depts.ttu.edu/sub/Activities/movies/index.php",
        "https://www.flickr.com/photos/ttustudents/albums/72177720320222445/",
        "https://texastech.com/feature/gameday-2025",
        "https://texastech.com/sports/mens-basketball",
    ],
    "Organization" : [
        "https://ttu.campuslabs.com/engage/",
        "https://ttu.campuslabs.com/engage/organizations",
        "https://ttu.campuslabs.com/engage/events"
    ],
    "Volunteering": [
        "https://www.depts.ttu.edu/hospitality/catering.php ",
        "https://www.depts.ttu.edu/pphc/programs/Volunteering.php"
    ],
    "Jobs" : [
        "https://www.depts.ttu.edu/hr/workattexastech/",
        "https://www.depts.ttu.edu/hospitality/jobs.php",
        "https://www.depts.ttu.edu/housing/workforhousing.php",
        "https://www.depts.ttu.edu/sub/jobs.php "
        "https://www.depts.ttu.edu/recreation/facilities/employment.php",
        "https://www.depts.ttu.edu/research/strategicresearch/hiring/"
    ]
}

resources = {}

def crawl(url):
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        return None  # skip if the page can't be reached

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        title = soup.title.string if soup.title else "No Title"
        return {
            "title": title,
            "text": text,
            "url": url
        }
    return None

# Crawl each category
for category_name, urls in categories.items():
    resources[category_name] = []
    for url in urls:
        page_data = crawl(url)
        if page_data:
            resources[category_name].append(page_data)

# Save JSON
with open("crawl/ttu_resources.json", "w") as f:
    json.dump(resources, f, indent=2)

print("Crawled pages organized by category and saved to ttu_resources.json")
