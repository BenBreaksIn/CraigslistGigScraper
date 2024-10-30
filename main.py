import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import re
from collections import defaultdict
import os
from typing import Dict, List, Optional
import logging


class CraigslistGigFinder:
    def __init__(self):
        # Set up logging
        self.setup_logging()

        # Define keyword groups with context
        self.keyword_groups = {
            'web_dev': [
                r'\bweb\s+(?:developer|development|designer?|design)\b',
                r'\bwordpress\b',
                r'\bshopify\b',
                r'\bwix\b',
                r'\bsquarespace\b',
                r'\bwebsite\s+(?:developer?|development|designer?|design)\b',
                r'\bfront[\s-]*end\b',
                r'\bback[\s-]*end\b',
                r'\bfull[\s-]*stack\b',
                r'\bweb\s+programmer\b',
                r'\bui\s*/?\s*ux\b',
                r'\bhtml\b',
                r'\bcss\b',
                r'\bbootstrap\b',
                r'\btailwind\b',
            ],
            'software_dev': [
                r'\bsoftware\s+(?:developer|development|engineer)\b',
                r'\b(?:senior|jr|junior)\s+developer\b',
                r'\bpython\b',
                r'\bjava\b',
                r'\bjavascript\b',
                r'\breact\b',
                r'\bangular\b',
                r'\bvue\.?js\b',
                r'\bnode\.?js\b',
                r'\bprogrammer\b',
                r'\bcoding\b',
                r'\bapi\b',
                r'\bruby\b',
                r'\bphp\b',
                r'\blaravel\b',
                r'\bdjango\b',
                r'\bspring\b',
                r'\bdocker\b',
            ],
            'mobile_dev': [
                r'\bmobile\s+(?:developer|development|app)\b',
                r'\bios\s+(?:developer|development)\b',
                r'\bandroid\s+(?:developer|development)\b',
                r'\bapp\s+(?:developer|development)\b',
                r'\bswift\b',
                r'\bkotlin\b',
                r'\breact\s+native\b',
                r'\bflutter\b',
                r'\bxcode\b',
                r'\bandroid\s+studio\b',
            ],
            'tech_misc': [
                r'\bdevops\b',
                r'\bcloud\b',
                r'\baws\b',
                r'\bazure\b',
                r'\bgcp\b',
                r'\bdatabase\b',
                r'\bsql\b',
                r'\bmongo\b',
                r'\bpostgres\b',
                r'\bdata\s+(?:scientist|science)\b',
                r'\bml\b',
                r'\bai\b',
                r'\bartificial\s+intelligence\b',
                r'\bmachine\s+learning\b',
                r'\bdeep\s+learning\b',
                r'\bgit\b',
                r'\blinux\b',
                r'\bci/cd\b',
                r'\bkubernetes\b',
                r'\bk8s\b',
            ]
        }

        # Load the cities list (continuing from previous list)
        self.craigslist_sites = {
            # WEST COAST
            ## California
            'SF Bay Area': 'sfbay',
            'Los Angeles': 'losangeles',
            'San Diego': 'sandiego',
            'Sacramento': 'sacramento',
            'Inland Empire': 'inlandempire',
            'Orange County': 'orangecounty',
            'Fresno': 'fresno',
            'Ventura County': 'ventura',
            'Bakersfield': 'bakersfield',
            'Long Beach': 'longbeach',
            'Palm Springs': 'palmsprings',
            'Monterey Bay': 'monterey',
            'Santa Barbara': 'santabarbara',
            'Stockton': 'stockton',
            'Modesto': 'modesto',
            'San Luis Obispo': 'slo',
            'Santa Maria': 'santamaria',
            'Redding': 'redding',
            'Chico': 'chico',
            'Humboldt County': 'humboldt',
            'Merced': 'merced',
            'Susanville': 'susanville',
            'Visalia-Tulare': 'visalia',
            'Yuba-Sutter': 'yubasutter',
            'Mendocino': 'mendocino',

            ## Oregon
            'Portland': 'portland',
            'Eugene': 'eugene',
            'Salem': 'salem',
            'Medford': 'medford',
            'Bend': 'bend',
            'Corvallis': 'corvallis',
            'Roseburg': 'roseburg',
            'Klamath Falls': 'klamath',
            'Coos Bay': 'coosbay',

            ## Washington
            'Seattle': 'seattle',
            'Tacoma': 'tacoma',
            'Spokane': 'spokane',
            'Olympia': 'olympia',
            'Bellingham': 'bellingham',
            'Kennewick': 'kpr',
            'Yakima': 'yakima',
            'Wenatchee': 'wenatchee',
            'Everett': 'everett',
            'Port Angeles': 'portangeles',

            # SOUTHWEST
            ## Arizona
            'Phoenix': 'phoenix',
            'Tucson': 'tucson',
            'Flagstaff': 'flagstaff',
            'Yuma': 'yuma',
            'Sierra Vista': 'sierravista',
            'Prescott': 'prescott',
            'Mohave County': 'mohave',

            ## Nevada
            'Las Vegas': 'lasvegas',
            'Reno': 'reno',
            'Elko': 'elko',

            ## New Mexico
            'Albuquerque': 'albuquerque',
            'Santa Fe': 'santafe',
            'Las Cruces': 'lascruces',
            'Roswell': 'roswell',
            'Farmington': 'farmington',

            # MOUNTAIN STATES
            ## Colorado
            'Denver': 'denver',
            'Colorado Springs': 'cosprings',
            'Boulder': 'boulder',
            'Fort Collins': 'fortcollins',
            'Pueblo': 'pueblo',
            'Western Slope': 'westslope',
            'High Rockies': 'rockies',
            'Eastern CO': 'eastco',

            ## Utah
            'Salt Lake City': 'saltlakecity',
            'Provo': 'provo',
            'Ogden': 'ogden',
            'St George': 'stgeorge',
            'Logan': 'logan',

            ## Idaho
            'Boise': 'boise',
            'Idaho Falls': 'eastidaho',
            'Twin Falls': 'twinfalls',
            'Lewiston': 'lewiston',
            'Pocatello': 'pocatello',

            ## Montana
            'Billings': 'billings',
            'Missoula': 'missoula',
            'Great Falls': 'greatfalls',
            'Bozeman': 'bozeman',
            'Helena': 'helena',
            'Butte': 'butte',
            'Kalispell': 'kalispell',

            ## Wyoming
            'Wyoming': 'wyoming',

            # MIDWEST - NORTH
            ## Minnesota
            'Minneapolis/St Paul': 'minneapolis',
            'Duluth': 'duluth',
            'Rochester': 'rmn',
            'St Cloud': 'stcloud',
            'Mankato': 'mankato',
            'Bemidji': 'bemidji',

            ## Wisconsin
            'Milwaukee': 'milwaukee',
            'Madison': 'madison',
            'Green Bay': 'greenbay',
            'Appleton': 'appleton',
            'Eau Claire': 'eauclaire',
            'La Crosse': 'lacrosse',
            'Sheboygan': 'sheboygan',
            'Wausau': 'wausau',

            ## Michigan
            'Detroit': 'detroit',
            'Grand Rapids': 'grandrapids',
            'Ann Arbor': 'annarbor',
            'Lansing': 'lansing',
            'Flint': 'flint',
            'Kalamazoo': 'kalamazoo',
            'Saginaw': 'saginaw',
            'Upper Peninsula': 'up',
            'Battle Creek': 'battlecreek',
            'Monroe': 'monroemi',
            'Muskegon': 'muskegon',
            'Northern MI': 'nmi',
            'Port Huron': 'porthuron',

            # MIDWEST - CENTRAL
            ## Illinois
            'Chicago': 'chicago',
            'Springfield': 'springfieldil',
            'Champaign': 'chambana',
            'Peoria': 'peoria',
            'Rockford': 'rockford',
            'Bloomington': 'bloomington',
            'Carbondale': 'carbondale',
            'Quad Cities': 'quadcities',
            'Decatur': 'decatur',

            ## Indiana
            'Indianapolis': 'indianapolis',
            'Fort Wayne': 'fortwayne',
            'South Bend': 'southbend',
            'Evansville': 'evansville',
            'Bloomington': 'bloomington',
            'Lafayette': 'tippecanoe',
            'Terre Haute': 'terrehaute',
            'Muncie': 'muncie',

            ## Ohio
            'Cleveland': 'cleveland',
            'Columbus': 'columbus',
            'Cincinnati': 'cincinnati',
            'Dayton': 'dayton',
            'Toledo': 'toledo',
            'Akron/Canton': 'akroncanton',
            'Youngstown': 'youngstown',
            'Lima': 'limaohio',
            'Mansfield': 'mansfield',
            'Sandusky': 'sandusky',
            'Zanesville': 'zanesville',

            # MIDWEST - SOUTH
            ## Missouri
            'St Louis': 'stlouis',
            'Kansas City': 'kansascity',
            'Springfield MO': 'springfield',
            'Columbia': 'columbiamo',
            'Jefferson City': 'jeffersoncity',
            'St Joseph': 'stjoseph',
            'Joplin': 'joplin',

            ## Kansas
            'Wichita': 'wichita',
            'Topeka': 'topeka',
            'Lawrence': 'lawrence',
            'Manhattan': 'ksu',
            'Salina': 'salina',

            ## Iowa
            'Des Moines': 'desmoines',
            'Cedar Rapids': 'cedarrapids',
            'Iowa City': 'iowacity',
            'Waterloo': 'waterloo',
            'Sioux City': 'siouxcity',
            'Quad Cities': 'quadcities',
            'Ames': 'ames',
            'Dubuque': 'dubuque',

            ## Nebraska
            'Omaha': 'omaha',
            'Lincoln': 'lincoln',
            'Grand Island': 'grandisland',
            'North Platte': 'northplatte',
            'Scottsbluff': 'scottsbluff',

            # SOUTH CENTRAL
            ## Texas
            'Austin': 'austin',
            'Dallas': 'dallas',
            'Houston': 'houston',
            'San Antonio': 'sanantonio',
            'Fort Worth': 'fortworth',
            'El Paso': 'elpaso',
            'Corpus Christi': 'corpuschristi',
            'McAllen': 'mcallen',
            'Lubbock': 'lubbock',
            'Amarillo': 'amarillo',
            'Waco': 'waco',
            'Beaumont': 'beaumont',
            'Brownsville': 'brownsville',
            'College Station': 'collegestation',
            'Del Rio': 'delrio',
            'Galveston': 'galveston',
            'Killeen': 'killeen',
            'Laredo': 'laredo',
            'Midland': 'midland',
            'Odessa': 'odessa',
            'San Marcos': 'sanmarcos',
            'Tyler': 'tyler',
            'Victoria': 'victoria',
            'Wichita Falls': 'wichitafalls',

            ## Oklahoma
            'Oklahoma City': 'oklahomacity',
            'Tulsa': 'tulsa',
            'Lawton': 'lawton',
            'Stillwater': 'stillwater',

            ## Arkansas
            'Little Rock': 'littlerock',
            'Fayetteville': 'fayar',
            'Fort Smith': 'fortsmith',
            'Jonesboro': 'jonesboro',
            'Texarkana': 'texarkana',

            # SOUTHEAST
            ## Florida
            'Miami': 'miami',
            'Tampa': 'tampa',
            'Orlando': 'orlando',
            'Jacksonville': 'jacksonville',
            'Fort Lauderdale': 'fortlauderdale',
            'West Palm Beach': 'westpalm',
            'Tallahassee': 'tallahassee',
            'Gainesville': 'gainesville',
            'Pensacola': 'pensacola',
            'Daytona': 'daytona',
            'Fort Myers': 'fortmyers',
            'Sarasota': 'sarasota',
            'Space Coast': 'spacecoast',
            'Lakeland': 'lakeland',
            'Ocala': 'ocala',
            'Panama City': 'panamacity',
            'St Augustine': 'staugustine',
            'Treasure Coast': 'treasure',
            'Keys': 'keys',

            ## Georgia
            'Atlanta': 'atlanta',
            'Augusta': 'augusta',
            'Savannah': 'savannah',
            'Macon': 'macon',
            'Athens': 'athens',
            'Columbus': 'columbusga',
            'Albany': 'albanyga',
            'Brunswick': 'brunswick',
            'Valdosta': 'valdosta',

            ## North Carolina
            'Charlotte': 'charlotte',
            'Raleigh-Durham': 'raleigh',
            'Greensboro': 'greensboro',
            'Winston-Salem': 'winstonsalem',
            'Asheville': 'asheville',
            'Wilmington': 'wilmington',
            'Fayetteville': 'fayetteville',
            'Boone': 'boone',
            'Greenville NC': 'greenville',
            'Hickory': 'hickory',
            'Jacksonville NC': 'onslow',
            'Outer Banks': 'outerbanks',

            ## South Carolina
            'Charleston SC': 'charleston',
            'Columbia': 'columbia',
            'Greenville SC': 'greenville',
            'Myrtle Beach': 'myrtlebeach',
            'Hilton Head': 'hiltonhead',
            'Florence SC': 'florencesc',
            'Aiken': 'aiken',

            ## Tennessee
            'Nashville': 'nashville',
            'Memphis': 'memphis',
            'Knoxville': 'knoxville',
            'Chattanooga': 'chattanooga',
            'Tri-Cities': 'tricities',
            'Clarksville': 'clarksville',
            'Jackson TN': 'jacksontn',
            'Cookeville': 'cookeville',

            ## Alabama
            'Birmingham': 'birmingham',
            'Huntsville': 'huntsville',
            'Mobile': 'mobile',
            'Montgomery': 'montgomery',
            'Auburn': 'auburn',
            'Dothan': 'dothan',
            'Florence': 'shoals',
            'Gadsden': 'gadsden',
            'Tuscaloosa': 'tuscaloosa',

            ## Mississippi
            'Jackson MS': 'jackson',
            'Hattiesburg': 'hattiesburg',
            'Biloxi': 'gulfport',
            'Meridian': 'meridian',
            'North MS': 'northmiss',
            'Southwest MS': 'natchez',

            ## Louisiana
            'New Orleans': 'neworleans',
            'Baton Rouge': 'batonrouge',
            'Shreveport': 'shreveport',
            'Lafayette': 'lafayette',
            'Lake Charles': 'lakecharles',
            'Monroe': 'monroe',
            'Alexandria': 'cenla',
            'Houma': 'houma',

            ## Kentucky
            'Louisville': 'louisville',
            'Lexington': 'lexington',
            'Bowling Green': 'bgky',
            'Owensboro': 'owensboro',
            'Western KY': 'westky',
            'Eastern KY': 'eastky',

            # NORTHEAST
            ## New York
            'New York City': 'newyork',
            'Long Island': 'longisland',
            'Buffalo': 'buffalo',
            'Rochester NY': 'rochester',
            'Syracuse': 'syracuse',
            'Albany': 'albany',
            'Hudson Valley': 'hudsonvalley',
            'Binghamton': 'binghamton',
            'Elmira': 'elmira',
            'Finger Lakes': 'fingerlakes',
            'Glens Falls': 'glensfalls',
            'Ithaca': 'ithaca',
            'Oneonta': 'oneonta',
            'Plattsburgh': 'plattsburgh',
            'Potsdam': 'potsdam',
            'Utica': 'utica',
            'Watertown': 'watertown',

            ## New Jersey
            'North Jersey': 'newjersey',
            'South Jersey': 'southjersey',
            'Central Jersey': 'jerseyshore',

            ## Pennsylvania
            'Philadelphia': 'philadelphia',
            'Pittsburgh': 'pittsburgh',
            'Allentown': 'allentown',
            'Erie': 'erie',
            'Harrisburg': 'harrisburg',
            'Scranton': 'scranton',
            'State College': 'pennstate',
            'Lancaster': 'lancaster',
            'Altoona': 'altoona',
            'Chambersburg': 'chambersburg',
            'Meadville': 'meadville',
            'Reading': 'reading',
            'Williamsport': 'williamsport',
            'York': 'york',

            ## Massachusetts
            'Boston': 'boston',
            'Worcester': 'worcester',
            'Springfield MA': 'westernmass',
            'South Coast': 'southcoast',
            'Cape Cod': 'capecod',

            ## Connecticut
            'Hartford': 'hartford',
            'New Haven': 'newhaven',
            'Eastern CT': 'newlondon',
            'Northwest CT': 'nwct',

            ## Maine
            'Portland ME': 'maine',
            'Bangor': 'bangor',
            'Augusta': 'augusta',

            ## New Hampshire
            'New Hampshire': 'nh',

            ## Rhode Island
            'Rhode Island': 'providence',

            ## Vermont
            'Vermont': 'vermont',
            'Burlington': 'burlington',

            # MID-ATLANTIC
            ## Virginia
            'Northern VA': 'nova',
            'Richmond': 'richmond',
            'Norfolk': 'norfolk',
            'Roanoke': 'roanoke',
            'Charlottesville': 'charlottesville',
            'Danville': 'danville',
            'Fredericksburg': 'fredericksburg',
            'Harrisonburg': 'harrisonburg',
            'Lynchburg': 'lynchburg',
            'Winchester': 'winchester',

            ## Maryland
            'Baltimore': 'baltimore',
            'Western Maryland': 'westmd',
            'Eastern Shore': 'easternshore',
            'Frederick': 'frederick',
            'Southern Maryland': 'smd',

            ## DC
            'Washington DC': 'washingtondc',

            ## Delaware
            'Delaware': 'delaware',

            ## West Virginia
            'Charleston WV': 'charlestonwv',
            'Huntington': 'huntington',
            'Morgantown': 'morgantown',
            'Northern Panhandle': 'wheeling',
            'Parkersburg': 'parkersburg',
            'Southern WV': 'swv',

            # ALASKA & HAWAII
            ## Alaska
            'Anchorage': 'anchorage',
            'Fairbanks': 'fairbanks',
            'Juneau': 'juneau',
            'Kenai Peninsula': 'kenai',

            ## Hawaii
            'Honolulu': 'honolulu',
            'Big Island': 'bigisland',
            'Maui': 'maui',
            'Kauai': 'kauai',

            # CANADA
            'Vancouver BC': 'vancouver',
            'Victoria BC': 'victoria',
            'Montreal': 'montreal',
            'Toronto': 'toronto',
            'Calgary': 'calgary',
            'Edmonton': 'edmonton',
            'Ottawa': 'ottawa',
            'Winnipeg': 'winnipeg',
            'Halifax': 'halifax',
            'Saskatoon': 'saskatoon',

            # U.S. TERRITORIES
            'Puerto Rico': 'puertorico',
            'U.S. Virgin Islands': 'virgin',
            'Guam': 'guam'
        }

        # Initialize tracking sets and counters
        self.seen_titles = set()
        self.seen_links = set()
        self.duplicate_count = 0

        # Create results directory
        self.results_dir = 'gig_finder_results'
        os.makedirs(self.results_dir, exist_ok=True)

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gig_finder.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalize title for comparison by removing spaces, punctuation, and converting to lowercase."""
        return re.sub(r'[^\w]', '', title.lower())

    def is_duplicate(self, title: str, link: str) -> bool:
        """Check if this is a duplicate posting."""
        normalized_title = self.normalize_title(title)

        # Check both title and link
        is_dupe = normalized_title in self.seen_titles or link in self.seen_links

        if not is_dupe:
            self.seen_titles.add(normalized_title)
            self.seen_links.add(link)
            return False

        self.duplicate_count += 1
        return True

    def matches_tech_keywords(self, text: str) -> List[str]:
        """Check if text matches any of our technical keywords."""
        text = text.lower()
        matches = []
        for group, patterns in self.keyword_groups.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(group)
                    break
        return matches

    def should_exclude(self, title: str) -> bool:
        """Check if the posting should be excluded based on common false positives."""
        exclude_patterns = [
            r'\bapply\s+(?:now|today)\b',
            r'\begg\s+donor\b',
            r'\bresearch\s+study\b',
            r'\bsurvey\b',
            r'\bfocus\s+group\b',
            r'\bmodels?\b',
            r'\bactors?\b',
            r'\bcastings?\b',
            r'\bphoto\s*shoot\b',
            r'hiring\s+immediately',
            r'start\s+tomorrow',
            r'\bclean(?:er|ing)\b',
            r'\broom\s+attendant\b',
            r'\bwarehouse\b',
            r'\bdriver\b',
            r'\bmoving\b',
            r'\bcaregiver\b',
            r'\btest\s+(?:study|survey)\b',
            r'\bonline\s+survey\b',
            r'\bbeta\s+test',
            r'\bfocus\s+group\b',
            r'\bpaid\s+study\b',
            r'\bresearch\s+participant\b'
        ]

        return any(re.search(pattern, title, re.IGNORECASE) for pattern in exclude_patterns)

    def get_posting_date(self, url: str) -> Optional[Dict[str, str]]:
        """Fetch the full posting page and extract the precise date."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for the specific date element
            date_p = soup.find('p', class_='postinginfo reveal')
            if date_p and 'Posted' in date_p.text:
                time_elem = date_p.find('time', class_='date timeago')
                if time_elem and time_elem.get('datetime'):
                    return {
                        'datetime': time_elem['datetime'],
                        'title': time_elem.get('title', ''),
                        'relative': time_elem.text.strip()
                    }
        except Exception as e:
            self.logger.error(f"Error fetching date from posting {url}: {str(e)}")

        return None

    def search_site(self, site_name: str, site_code: str) -> List[Dict]:
        """Search a single Craigslist site."""
        results = []
        sections = ['cpg', 'crg', 'ggg']  # computer gigs, creative gigs, general gigs

        for section in sections:
            url = f"https://{site_code}.craigslist.org/search/{section}"
            self.logger.info(f"Searching {site_name} - {section}")

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.get(url, headers=headers, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')

                listings = soup.select('.cl-static-search-result')

                for listing in listings:
                    title_elem = listing.select_one('.title')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Skip if title matches exclusion patterns
                    if self.should_exclude(title):
                        continue

                    link_elem = listing.select_one('a')
                    link = link_elem.get('href', '') if link_elem else ''

                    # Skip if it's a duplicate
                    if self.is_duplicate(title, link):
                        continue

                    # Check for keyword matches
                    matches = self.matches_tech_keywords(title)
                    if matches:
                        location_elem = listing.select_one('.location')
                        price_elem = listing.select_one('.price')

                        # Get detailed date from the full posting
                        date_info = self.get_posting_date(link) if link else None

                        result = {
                            'site': site_name,
                            'title': title,
                            'link': link,
                            'location': location_elem.get_text(strip=True) if location_elem else '',
                            'price': price_elem.get_text(strip=True) if price_elem else 'Not specified',
                            'categories': matches,
                            'section': section,
                            'date': {
                                'datetime': date_info['datetime'] if date_info else None,
                                'formatted': date_info['title'] if date_info else None,
                                'relative': date_info['relative'] if date_info else None
                            },
                            'date_found': datetime.now().isoformat(),
                        }

                        results.append(result)
                        self.logger.info(f"Found matching gig: {title} (Posted: {result['date']['datetime']})")

                time.sleep(2)  # Respect rate limits

            except Exception as e:
                self.logger.error(f"Error searching {site_name} - {section}: {str(e)}")

        return results

    def get_region(self, site_code: str) -> str:
        """Determine the region for a given site code."""
        west_coast = ['sfbay', 'losangeles', 'sandiego', 'seattle', 'portland', 'sacramento', 'lasvegas', 'phoenix']
        mountain = ['denver', 'boulder', 'saltlakecity', 'albuquerque', 'boise']
        central = ['austin', 'dallas', 'houston', 'chicago', 'minneapolis', 'kansascity']

        if site_code in west_coast:
            return 'West Coast'
        elif site_code in mountain:
            return 'Mountain'
        elif site_code in central:
            return 'Central'
        else:
            return 'East Coast'

    def run_search(self) -> Dict:
        """Run the search across all sites."""
        self.logger.info("Starting search across Craigslist sites...")
        start_time = time.time()
        all_results = []

        # Group results by region for better organization
        region_results = defaultdict(list)

        for site_name, site_code in self.craigslist_sites.items():
            results = self.search_site(site_name, site_code)
            region = self.get_region(site_code)
            region_results[region].extend(results)
            all_results.extend(results)

        # Sort results by categories (more category matches = more relevant)
        all_results.sort(key=lambda x: len(x['categories']), reverse=True)

        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(self.results_dir, f'tech_gigs_{timestamp}.json')

        final_results = {
            'timestamp': datetime.now().isoformat(),
            'total_results': len(all_results),
            'total_duplicates_skipped': self.duplicate_count,
            'search_duration': time.time() - start_time,
            'results_by_region': {region: results for region, results in region_results.items()},
            'all_results': all_results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2)

        # Print summary
        self.logger.info("\nSearch Summary:")
        self.logger.info(f"Total unique gigs found: {len(all_results)}")
        self.logger.info(f"Duplicate listings skipped: {self.duplicate_count}")
        self.logger.info(f"Search duration: {time.time() - start_time:.2f} seconds")
        self.logger.info(f"Results saved to: {filename}")

        # Print results by region
        for region, results in region_results.items():
            self.logger.info(f"\n{region} - {len(results)} gigs found")
            category_counts = defaultdict(int)
            for result in results:
                for category in result['categories']:
                    category_counts[category] += 1
            for category, count in category_counts.items():
                self.logger.info(f"  {category}: {count} gigs")

        # Print top results
        self.logger.info("\nTop matching gigs:")
        for result in all_results[:5]:
            self.logger.info("\n" + "=" * 50)
            self.logger.info(f"Site: {result['site']} ({result['section']})")
            self.logger.info(f"Title: {result['title']}")
            self.logger.info(f"Categories: {', '.join(result['categories'])}")
            self.logger.info(f"Location: {result['location']}")
            self.logger.info(f"Posted: {result['date']['datetime']} ({result['date']['relative']})")
            self.logger.info(f"Link: {result['link']}")

        return final_results


def main():
    finder = CraigslistGigFinder()
    try:
        results = finder.run_search()
        print(f"\nSearch completed successfully. Found {results['total_results']} gigs.")
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        logging.exception("Unexpected error in main execution")


if __name__ == "__main__":
    main()
