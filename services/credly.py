from bs4 import BeautifulSoup
import lxml, requests
import time

from settings import (
    CREDLY_SORT,
    CREDLY_USER,
    CREDLY_BASE_URL,
    BADGE_SIZE,
    NUMBER_LAST_BADGES,
    CREDLY_API_TOKEN,
)

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

            data = response.json()
            all_badges.extend(data["data"])

            # Check if there is a next page
            if not data["metadata"]["next_page_url"]:
                break

            page += 1
            time.sleep(3)  # Avoid hitting rate limits

        return all_badges


    def convert_to_dict(self, badge):
        badge_template = badge["badge_template"]
        issuer = badge["issuer"]["entities"][0]["entity"]["name"] if badge["issuer"]["entities"] else "Unknown Issuer"

        return {
            "title": badge_template["name"],
            "href": badge_template["url"],
            "img": badge_template["image_url"].replace("110x110", f"{BADGE_SIZE}x{BADGE_SIZE}"),
            "issuer": issuer,
        }

    def return_badges_html(self):
        badges = self.fetch_badges()
        return [self.convert_to_dict(badge) for badge in badges]

    def generate_md_format(self, badges):
        if not badges:
            return None

        sorted_badges = sorted(badges, key=lambda x: x["issuer"])
        grouped_badges = {}
        for badge in sorted_badges:
            issuer = badge["issuer"]
            if issuer not in grouped_badges:
                grouped_badges[issuer] = []
            grouped_badges[issuer].append(badge)

        markdown = f"## Total Badges: ({len(badges)})\n\n"
        markdown += "## List of Issuing Organizations\n\n"
        markdown += "| Issuing Organization | Description | Credly Badges | Verified |\n"
        markdown += "|-----------------------|----------------|----------------|----------|\n"
        for issuer in grouped_badges.keys():
            anchor = issuer.lower().replace(" ", "-")
            markdown += f"| [{issuer}](#{anchor}-{len(grouped_badges.get(issuer, []))}) | ... | {len(grouped_badges.get(issuer, []))} | ✅ |\n"
        markdown += "\n"

        for issuer, badges in grouped_badges.items():
            anchor = issuer.lower().replace(" ", "-")
            markdown += f"### {issuer} ({len(badges)})\n\n"
            markdown += '<table width="100%">\n'
            first_row = badges[:5]
            markdown += '  <tr>\n'
            for badge in first_row:
                markdown += f'    <td width="20%"><a href="{badge["href"]}"><img src="{badge["img"]}" /></a></td>\n'
            for _ in range(5 - len(first_row)):
                markdown += '    <td width="20%"></td>\n'
            markdown += '  </tr>\n'
            markdown += '  <tr>\n'
            for badge in first_row:
                markdown += f'    <td align="center" width="20%"><a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a></td>\n'
            for _ in range(5 - len(first_row)):
                markdown += '    <td align="center" width="20%"></td>\n'
            markdown += '  </tr>\n'
            markdown += '</table>\n\n'

            # If there are more than 5 badges, create a "more" dropdown
            if len(badges) > 5:
                markdown += '<br>\n'
                markdown += f'<details>\n  <summary>More {issuer} ({len(badges) - 5})</summary>\n\n'
                markdown += '<table width="100%">\n'
                remaining_badges = badges[5:]
                rows = []
                for i in range(0, len(remaining_badges), 5):
                    row = remaining_badges[i:i + 5]
                    rows.append(row)
                for row in rows:
                    markdown += '  <tr>\n'
                    for badge in row:
                        markdown += f'    <td width="20%"><a href="{badge["href"]}"><img src="{badge["img"]}" /></a></td>\n'
                    for _ in range(5 - len(row)):
                        markdown += '    <td width="20%"></td>\n'
                    markdown += '  </tr>\n'
                    markdown += '  <tr>\n'
                    for badge in row:
                        markdown += f'    <td align="center" width="20%"><a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a></td>\n'
                    for _ in range(5 - len(row)):
                        markdown += '    <td align="center" width="20%"></td>\n'
                    markdown += '  </tr>\n'
                markdown += '</table>\n\n'
                markdown += '</details>\n\n'

        return markdown

    def get_markdown(self):
        badges = self.return_badges_html()
        return self.generate_md_format(badges)