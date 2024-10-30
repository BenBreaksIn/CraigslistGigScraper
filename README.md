# Craigslist Gig Finder

Craigslist Gig Finder is a Python script that allows users to automate the search for tech gigs posted on Craigslist. It aims to help freelancers and job seekers find opportunities in web development, software development, mobile development, and other tech-related fields. This script performs keyword-based searches across various Craigslist regions and filters the results to match the user's technical skills.

## Features

- **Keyword-based Search:** Automatically search Craigslist gigs in categories such as web development, software development, mobile development, and more.
- **Multi-region Search:** Search across a wide range of Craigslist regions in the US and Canada.
- **Category-based Filtering:** Filter results based on tech-related keywords to reduce false positives.
- **Duplicate Detection:** Automatically detects and removes duplicate postings.
- **Logging and Results Storage:** Save results to a JSON file for later analysis, with comprehensive logging to track search progress.
- **Exclusion Patterns:** Filters out false positives (e.g., non-tech gigs, spam postings).

## Setup

### Prerequisites

To run the Craigslist Gig Finder, you will need:

- Python 3.6 or higher
- Required Python packages (install using `pip`):
  - `requests`
  - `beautifulsoup4`

### Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/username/craigslist-gig-finder.git
   cd craigslist-gig-finder
   ```

2. **Install Dependencies**

   Install the required dependencies using `pip`:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

To run the script, simply execute the following command:

```sh
python craigslist_gig_finder.py
```

The script will start searching for tech gigs across the defined Craigslist regions. Results will be saved in a JSON file under the `gig_finder_results` directory.

### Running the Search

- The script will automatically search for gigs across multiple Craigslist sites based on the predefined list.
- It will search for gigs in three categories: **computer gigs**, **creative gigs**, and **general gigs**.
- Matching results are saved to a JSON file for later analysis.

### Search Parameters

- **Keyword Groups:** The script uses keyword patterns to match specific categories of gigs, such as:
  - **Web Development:** Keywords like "web developer," "HTML," "CSS," etc.
  - **Software Development:** Keywords like "software developer," "Python," "Java," etc.
  - **Mobile Development:** Keywords like "iOS developer," "Android development," etc.
  - **Tech Miscellaneous:** Keywords like "DevOps," "AWS," "cloud," etc.

- **Exclusion Patterns:** The script filters out posts that commonly appear as false positives, such as research studies, focus groups, surveys, etc.

## Logging

The script provides comprehensive logging of the search process:

- Logs are saved to `gig_finder.log` for reference.
- Logs include information about the gigs found, duplicate gigs skipped, and any errors encountered.

## Results

- **Storage:** Results are saved in a JSON file in the `gig_finder_results` directory, with filenames indicating the timestamp of the search.
- **Format:** The results JSON file includes details such as the gig title, categories matched, location, link, and posting date.

## Customization

The script can be customized for different regions or keywords by modifying the following:

- **Keyword Groups:** Update the `self.keyword_groups` dictionary in the script to add/remove keywords or categories.
- **Regions List:** Update the `self.craigslist_sites` dictionary to search in additional regions or focus on specific areas.

## Error Handling

- The script handles errors such as connection timeouts and invalid links to ensure the search process is not disrupted.
- It waits between requests to avoid being rate-limited by Craigslist.

## Contributions

Feel free to contribute by submitting issues or pull requests. Any improvements or additional features are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This script is intended for educational purposes and personal use. Craigslist may have terms of use that restrict automated access, so use this script responsibly and consider checking Craigslist's policies before using it extensively.

