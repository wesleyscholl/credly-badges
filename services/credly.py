from bs4 import BeautifulSoup
import lxml, requests
import time

from settings import (
    CREDLY_SORT,
    CREDLY_USER,
    CREDLY_BASE_URL,
    BADGE_SIZE,
    NUMBER_LAST_BADGES,
)


class Credly:
    def __init__(self, f=None):
        self.FILE = f
        self.BASE_URL = CREDLY_BASE_URL
        self.USER = CREDLY_USER
        self.SORT = CREDLY_SORT

        print(self.BASE_URL, self.USER, self.SORT)

    def data_from_html(self):
        if self.FILE:
            with open(self.FILE, "r") as f:
                return f.read()
        
        all_data = ""
        page = 1
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

        while True:
            url = f"{self.BASE_URL}/users/{self.USER}/badges?page={page}&sort={self.sort_by()}"
            response = requests.get(url, headers=headers)
            data = response.text
            print(data)

            soup = BeautifulSoup(data, "lxml")
            badges = soup.findAll("a", {"class": "cr-public-earned-badge-grid-item"})
            if not badges:
                break

            relevant_data = ''.join(str(badge) for badge in badges)
            all_data += relevant_data

            next_page = soup.find("a", {"rel": "next"})
            if not next_page:
                break

            page += 1
            time.sleep(5)

        return all_data

    def sort_by(self):
        return "most_popular" if self.SORT == "POPULAR" else "-state_updated_at"

    def convert_to_dict(self, htmlBadge):
        soupBadge = BeautifulSoup(str(htmlBadge), "lxml")
        img = soupBadge.findAll(
            "img", {"class": "cr-standard-grid-item-content__image"}
        )[0]
        issuer = soupBadge.find(
            "div", {"class": "cr-standard-grid-item-content__subtitle"}
        ).text.strip()
        return {
            "title": str(htmlBadge["title"]).replace('"', '\\"'),
            "href": self.BASE_URL + htmlBadge["href"],
            "img": img["src"].replace("110x110", f"{BADGE_SIZE}x{BADGE_SIZE}"),
            "issuer": issuer,
        }

    def return_badges_html(self):
        data = self.data_from_html()
        # print(data)
        soup = BeautifulSoup(data, "lxml")
        return soup.findAll("a", {"class": "cr-public-earned-badge-grid-item"})

    def generate_md_format(self, badges):
        if not badges:
            return None
        sorted_badges = sorted(badges, key=lambda x: x['issuer'])
        grouped_badges = {}
        for badge in sorted_badges:
            issuer = badge['issuer']
            if issuer not in grouped_badges:
                grouped_badges[issuer] = []
            grouped_badges[issuer].append(badge)

        # Count and add the number of badges to the markdown
        markdown = f"## Total Badges: ({len(badges)})\n\n"

        # Generate the list of issuing organizations with anchor links
        markdown += "## List of Issuing Organizations\n\n"
        markdown += "| Issuing Organization | Description | Credly Badges | Verified |\n"
        markdown += "|-----------------------|----------------|----------------|----------|\n"
        for issuer in grouped_badges.keys():
            # Create an anchor link for each organization
            anchor = issuer.lower().replace(" ", "-")
            # Get the total number of badges for the organization
            # Add total badges to anchored link
            markdown += f"| [{issuer}](#{anchor}-{len(grouped_badges.get(issuer, []))}) | ... | {len(grouped_badges.get(issuer, []))} | ✅ |\n"
        markdown += "\n"

        # Generate the badge tables for each organization
        for issuer, badges in grouped_badges.items():
            # Add an anchor for the organization section
            anchor = issuer.lower().replace(" ", "-")
            markdown += f"### {issuer} ({len(badges)})\n\n"
            # Main table for the first 5 badges
            markdown += '<table width="100%">\n'
            first_row = badges[:5]  # Get the first 5 badges
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
                # Add the number of badges hidden in the dropdown title
                markdown += f'<details>\n  <summary>More {issuer} ({len(badges) - 5})</summary>\n\n'
                markdown += '<table width="100%">\n'
                
                # Process remaining badges in groups of 5
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

        # print(markdown)
        return markdown

    def get_markdown(self):
        badges_html = self.return_badges_html()
        return self.generate_md_format(
            [self.convert_to_dict(badge) for badge in badges_html]
        )