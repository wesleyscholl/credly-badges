from bs4 import BeautifulSoup
import lxml, requests
import time
import random

from settings import (
    CREDLY_SORT,
    CREDLY_USER,
    CREDLY_BASE_URL,
    BADGE_SIZE,
    NUMBER_LAST_BADGES,
    CREDLY_API_TOKEN,
)
from services.org_info import org_logos, org_links, org_descriptions

class Credly:
    def __init__(self, f=None):
        self.FILE = f
        self.BASE_URL = CREDLY_BASE_URL
        self.USER = CREDLY_USER
        self.SORT = CREDLY_SORT
        self.API_TOKEN = CREDLY_API_TOKEN
        print(self.BASE_URL, self.USER, self.SORT)

    def fetch_badges(self):
        all_badges = []
        page = 1

        headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "User-Agent": "Credly/1.28.0/2025041702 (iOS; 18.4.1; iPhone14,4)",
            "Accept": "application/json",
        }

        while True:
            url = f"{self.BASE_URL}?page={page}&state=accepted,pending"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                print(response.text)
                break

            print(f"Page {page} - Status Code: {response.status_code}")
            data = response.json()
            all_badges.extend(data["data"])

            # Check if there is a next page
            if not data["metadata"]["next_page_url"]:
                break

            page += 1
            delay = random.uniform(2, 6)
            print(f"Delaying next request by {delay:.2f} seconds...")
            time.sleep(delay)  # Avoid hitting rate limits

        return all_badges

    def convert_to_dict(self, badge):
        badge_template = badge["badge_template"]
        issuer = badge["issuer"]["entities"][0]["entity"]["name"] if badge["issuer"]["entities"] else "Unknown Issuer"

        activities = badge_template.get("badge_template_activities", [])
        criteria = " ".join(activity.get("title", "No criteria provided") for activity in activities if isinstance(activity, dict))

        return {
            "title": badge_template["name"],
            "href": badge_template["url"],
            "img": badge_template["image_url"].replace("https://images.credly.com/", f"https://images.credly.com/size/{BADGE_SIZE}x{BADGE_SIZE}/"),
            "issuer": issuer,
            "description": badge_template["description"],
            "time_to_earn": badge_template["time_to_earn"],
            "skills": badge_template["skills"],
            "criteria": criteria,
            "level": badge_template["level"],
        }

    def return_badges_html(self):
        badges = self.fetch_badges()
        return [self.convert_to_dict(badge) for badge in badges]

    def twenty_word_limit(self, text):
        """Helper function to limit text to less than or equal to 20 words, otherwise returns just the first 20 words"""
        words = text.split()
        if len(words) <= 20:
            return text, None
        else:
            limited_text = " ".join(words[:20]) + "..."
            return limited_text

    def generate_badge_rows(self, badges):
        """Helper function to generate table rows for a list of badges."""
        rows = ""
        for badge in badges:
            rows += '  <tr>\n'
            rows += f'    <td align="center" width="20%" padding="10">\n'
            rows += f'      <a href="{badge["href"]}">\n'
            rows += f'        <img src="{badge["img"]}" width="100">\n'
            rows += f'      </a><br>\n'
            rows += f'      <a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a>\n'
            rows += f'    </td>\n'
            rows += f'    <td width="80%" padding="10">\n'
            rows += f'      <strong>Description:</strong> {self.twenty_word_limit(badge["description"])} <a href="{badge["href"]}">Read more here</a><br>\n'
            # Only render up to 5 skills
            if badge["skills"]:
                if len(badge["skills"]) > 5:
                    badge["skills"] = badge["skills"][:5]
            rows += f'      <strong>Skills:</strong> {", ".join(badge["skills"])}<br>\n'
            rows += f'      <strong>Criteria:</strong> {self.twenty_word_limit(badge["criteria"])} <a href="{badge["href"]}">Read more here</a><br>\n'
            rows += f'      <strong>Time to Earn:</strong> {badge.get("time_to_earn", "N/A")}<br>\n'
            rows += f'      <strong>Level:</strong> {badge.get("level", "N/A")}\n'
            rows += f'    </td>\n'
            rows += '  </tr>\n'
        return rows

    def generate_hidden_badge_rows(self, badges):
        """Helper function to generate hidden table rows for a list of badges, filtering out paid training badges."""
        rows = ""
        for badge in badges:
            # Filter out paid training badges by title and issuer
            if (
                (badge["title"].strip() == "LFS256: DevOps and Workflow Management with Argo" and badge["issuer"].strip() == "The Linux Foundation") or
                (badge["title"].strip() == "CAPA: Certified Argo Project Associate" and badge["issuer"].strip() == "The Linux Foundation")
            ):
                continue
            rows += '  <tr>\n'
            rows += f'    <td align="center" width="20%" padding="10">\n'
            rows += f'      <a href="{badge["href"]}">\n'
            rows += f'        <img src="{badge["img"]}" width="100">\n'
            rows += f'      </a><br>\n'
            rows += f'      <a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a>\n'
            rows += f'    </td>\n'
            rows += f'    <td width="80%" padding="10">\n'
            rows += f'      <strong>Read more <a href="{badge["href"]}">here</a><br>\n'
            rows += f'    </td>\n'
            rows += '  </tr>\n'
        return rows

    def generate_md_format(self, badges):
        if not badges:
            return None

        sorted_badges = sorted(badges, key=lambda x: x["issuer"].lower())
        grouped_badges = {}
        for badge in sorted_badges:
            issuer = badge["issuer"]
            if issuer not in grouped_badges:
                grouped_badges[issuer] = []
            grouped_badges[issuer].append(badge)

        markdown = f"## Total Badges: ({len(badges)})\n\n"
        markdown += f"## Issuing Organizations: ({len(grouped_badges)})\n\n"
        unique_issuers = list(grouped_badges.keys())
        unique_issuers.sort(key=lambda x: x.lower())  # Sort issuers alphabetically
        markdown += "<table width='100%' border='1' cellspacing='0' cellpadding='4'>\n"
        cell_count = 0
        for idx, issuer in enumerate(unique_issuers):
            if cell_count == 0:
                markdown += "<tr>\n"
            logo = org_logos(issuer)
            link = org_links(issuer)
            anchor = issuer.lower().replace(" ", "-").replace(".", "")
            badge_count = len(grouped_badges[issuer])
            if logo and link:
                markdown += f'  <td align="center" width="20%" padding="10">\n'
                markdown += f'    <a href="{link}">\n'
                markdown += f'      <img src="{logo}" width="100">\n'
                markdown += f'    </a><br>\n'
                markdown += f'    <a href="#{anchor}-{badge_count}">{issuer}</a>\n'
                markdown += f'  </td>\n'
                cell_count += 1
            if cell_count == 5:
                markdown += "</tr>\n"
                cell_count = 0
        if cell_count > 0:
            for _ in range(5 - cell_count):
                markdown += '  <td></td>\n'
            markdown += "</tr>\n"
        markdown += "</table>\n"
        markdown += f'\n\n'
        for issuer in unique_issuers:
            markdown += f"[{issuer}](#{issuer.lower().replace(' ', '-').replace('.', '')}-{len(grouped_badges.get(issuer, []))}), "
        markdown = markdown.rstrip(", ")  # Remove trailing comma
        markdown += f'\n\n'

        for issuer, badges in grouped_badges.items():
            anchor = issuer.lower().replace(" ", "-").replace(".", "")
            markdown += f'\n\n'
            markdown += f"### {issuer} ({len(badges)})\n"
            markdown += f'\n\n'
            markdown += f'<strong><a href="#user-content-free-credly-badges">Back to Top ⬆️</a></strong>\n\n'
            markdown += f'\n\n'
            markdown += "| Issuing Organization | Description | Credly Badges | Verified | Organization Link |\n"
            markdown += "|        :---:         |-------------|     :---:     |   :---:  |       :---:       |\n"
            markdown += f"| <img src='{org_logos(issuer)}' height='100' /><br>[{issuer}](#{anchor}-{len(grouped_badges.get(issuer, []))}) | {org_descriptions(issuer)} | {len(grouped_badges.get(issuer, []))} | ✅ | [{issuer}]({org_links(issuer)}) |\n"
            markdown += f'\n\n'
            markdown += '<table width="100%" border="1" cellspacing="0" cellpadding="4">\n'
            markdown += '  <tr>\n'
            markdown += '    <th width="20%">Badge</th>\n'
            markdown += '    <th width="80%">Description</th>\n'
            markdown += '  </tr>\n'

            # Generate rows for the first 3 badges
            markdown += self.generate_badge_rows(badges[:3])
            markdown += '</table>\n\n'

            # If there are more than 3 badges, create a "more" dropdown
            if len(badges) > 3:
                markdown += f'<details><summary>More {issuer} ({len(badges) - 3})</summary>\n'
                markdown += '<table width="100%" border="1" cellspacing="0" cellpadding="4">\n'
                markdown += '  <tr>\n'
                markdown += '    <th width="20%">Badge</th>\n'
                markdown += '    <th width="80%">Description</th>\n'
                markdown += '  </tr>\n'

                # Generate rows for the remaining badges
                markdown += self.generate_hidden_badge_rows(badges[3:])
                markdown += '</table>\n\n'
                markdown += '</details>'
        
        # Print tail of the markdown
        print(markdown.split("\n")[-100:])
        return markdown

    def get_markdown(self):
        badges = self.return_badges_html()
        return self.generate_md_format(badges)
