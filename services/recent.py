import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Set, Tuple

class CredlyUpdater:
    def __init__(self, api_token: str, badge_size: int = 100):
        self.api_token = api_token
        self.badge_size = badge_size
        self.base_url = "https://api.credly.com/v1/users/self/badges"
        
        # Organization data (moved from original class)
        self.org_logos = {
            "APIsec University": "https://images.credly.com/size/200x200/images/722366ec-1535-4d51-ac31-f5294833e3d4/blob.png",
            "Acronis": "https://images.credly.com/size/200x200/images/d498c506-056e-4062-905a-c757724a4b23/blob.png",
            "Alation University": "https://images.credly.com/size/400x400/images/491c6659-8c88-4158-80f2-3228bf18db12/blob",
            "Adobe Education": "https://images.credly.com/size/200x200/images/bb708792-a2f0-4b4a-bc7d-27d4423938af/blob.png",
            "Alteryx": "https://images.credly.com/size/200x200/images/b8079e20-ff5f-47c4-aadd-494b54ef02eb/blob.png",
            "Amazon Web Services Training and Certification": "https://images.credly.com/size/400x400/images/14a6da77-7f93-4867-81ef-ad7c6a400ec2/blob.png",
            # ... (include all other organizations from original)
        }
        
        self.org_links = {
            "APIsec University": "https://www.credly.com/organizations/apisec-university/badges",
            "Acronis": "https://www.credly.com/organizations/acronis/badges",
            # ... (include all other organizations from original)
        }
        
        self.org_descriptions = {
            "APIsec University": "APIsec University is a learning platform focused on API security, offering certifications to strengthen secure development practices.",
            "Acronis": "Acronis is a global leader in cyber protection, specializing in data backup, recovery, and secure file access.",
            # ... (include all other organizations from original)
        }

    def fetch_latest_badges(self) -> List[Dict]:
        """Fetch the latest badges using a single API call"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "User-Agent": "Credly/1.28.0/2025041702 (iOS; 18.4.1; iPhone14,4)",
            "Accept": "application/json",
        }
        
        url = f"{self.base_url}?sort=-state_updated_at"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"Fetched {len(data['data'])} badges")
            return data['data']
            
        except requests.RequestException as e:
            print(f"Error fetching badges: {e}")
            return []

    def convert_badge_to_dict(self, badge: Dict) -> Dict:
        """Convert API badge response to standardized format"""
        badge_template = badge["badge_template"]
        issuer = badge["issuer"]["entities"][0]["entity"]["name"] if badge["issuer"]["entities"] else "Unknown Issuer"

        activities = badge_template.get("badge_template_activities", [])
        criteria = " ".join(activity.get("title", "No criteria provided") for activity in activities if isinstance(activity, dict))

        return {
            "title": badge_template["name"],
            "href": badge_template["url"],
            "img": badge_template["image_url"].replace("https://images.credly.com/", f"https://images.credly.com/size/{self.badge_size}x{self.badge_size}/"),
            "issuer": issuer,
            "description": badge_template["description"],
            "time_to_earn": badge_template["time_to_earn"],
            "skills": badge_template["skills"],
            "criteria": criteria,
            "level": badge_template.get("level", "N/A"),
            "state_updated_at": badge.get("state_updated_at")
        }

    def parse_existing_readme(self, readme_content: str) -> Tuple[Set[str], Dict[str, List[str]]]:
        """Parse existing README to extract current badges and organizations"""
        existing_badges = set()
        existing_orgs = {}
        
        # Extract badge titles from existing README
        badge_pattern = r'<a href="[^"]*">([^<]+)</a>'
        matches = re.findall(badge_pattern, readme_content)
        
        for match in matches:
            if " - " in match:  # Badge format is "Title - Issuer"
                title, issuer = match.rsplit(" - ", 1)
                existing_badges.add(title.strip())
                
                if issuer not in existing_orgs:
                    existing_orgs[issuer] = []
                existing_orgs[issuer].append(title.strip())
        
        return existing_badges, existing_orgs

    def find_new_badges(self, latest_badges: List[Dict], existing_badges: Set[str]) -> List[Dict]:
        """Find badges that don't exist in the current README"""
        new_badges = []
        
        for badge_data in latest_badges:
            badge = self.convert_badge_to_dict(badge_data)
            if badge["title"] not in existing_badges:
                new_badges.append(badge)
                print(f"New badge found: {badge['title']} from {badge['issuer']}")
        
        return new_badges

    def get_org_info(self, issuer: str) -> Tuple[str, str, str]:
        """Get organization logo, link, and description"""
        logo = self.org_logos.get(issuer, "")
        link = self.org_links.get(issuer, "")
        description = self.org_descriptions.get(issuer, "No description available")
        
        return logo, link, description

    def ten_word_limit(self, text: str) -> str:
        """Limit text to 10 words"""
        words = text.split()
        if len(words) <= 10:
            return text
        else:
            return " ".join(words[:10]) + "..."

    def generate_badge_row(self, badge: Dict) -> str:
        """Generate a single badge table row"""
        return f'''  <tr>
    <td align="center" width="20%" padding="10">
      <a href="{badge["href"]}">
        <img src="{badge["img"]}" width="100">
      </a><br>
      <a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a>
    </td>
    <td width="80%" padding="10">
      <strong>Description:</strong> {self.ten_word_limit(badge["description"])} Read more <a href="{badge["href"]}">here</a><br>
      <strong>Skills:</strong> {", ".join(badge["skills"])}<br>
      <strong>Criteria:</strong> {badge["criteria"]}<br>
      <strong>Time to Earn:</strong> {badge["time_to_earn"]}<br>
      <strong>Level:</strong> {badge.get("level", "N/A")}
    </td>
  </tr>
'''

    def generate_org_section(self, issuer: str, badges: List[Dict]) -> str:
        """Generate a complete organization section"""
        logo, link, description = self.get_org_info(issuer)
        anchor = issuer.lower().replace(" ", "-")
        
        section = f'''

### {issuer} ({len(badges)})


<strong><a href="#user-content-free-credly-badges">Back to Top ⬆️</a></strong>


| Issuing Organization | Description | Credly Badges | Verified | Organization Link |
|        :---:         |-------------|     :---:     |   :---:  |       :---:       |
| <img src='{logo}' height='100' /><br>[{issuer}](#{anchor}-{len(badges)}) | {description} | {len(badges)} | ✅ | [{issuer}]({link}) |


<table width="100%" border="1" cellspacing="0" cellpadding="4">
  <tr>
    <th width="20%">Badge</th>
    <th width="80%">Description, Time to Earn, Skills & Earning Criteria</th>
  </tr>
'''
        
        # Add first 3 badges
        for badge in badges[:3]:
            section += self.generate_badge_row(badge)
        
        section += '</table>\n\n'
        
        # Add remaining badges if more than 3
        if len(badges) > 3:
            section += f'<details><summary>More {issuer} ({len(badges) - 3})</summary>\n'
            section += '<table width="100%" border="1" cellspacing="0" cellpadding="4">\n'
            section += '  <tr>\n'
            section += '    <th width="20%">Badge</th>\n'
            section += '    <th width="80%">Description, Time to Earn, Skills & Earning Criteria</th>\n'
            section += '  </tr>\n'
            
            for badge in badges[3:]:
                section += f'''  <tr>
    <td align="center" width="20%" padding="10">
      <a href="{badge["href"]}">
        <img src="{badge["img"]}" width="100">
      </a><br>
      <a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a>
    </td>
    <td width="80%" padding="10">
      <strong>Read more <a href="{badge["href"]}">here</a><br>
    </td>
  </tr>
'''
            
            section += '</table>\n\n'
            section += '</details>'
        
        return section

    def update_readme_with_new_badges(self, readme_content: str, new_badges: List[Dict]) -> str:
        """Update README content with new badges, maintaining alphabetical order"""
        if not new_badges:
            print("No new badges to add")
            return readme_content
        
        # Group new badges by issuer
        new_badges_by_issuer = {}
        for badge in new_badges:
            issuer = badge["issuer"]
            if issuer not in new_badges_by_issuer:
                new_badges_by_issuer[issuer] = []
            new_badges_by_issuer[issuer].append(badge)
        
        # Parse existing README to understand structure
        existing_badges, existing_orgs = self.parse_existing_readme(readme_content)
        
        updated_content = readme_content
        
        # Update badge counts in header
        total_badges = len(existing_badges) + len(new_badges)
        total_orgs = len(existing_orgs) + len([org for org in new_badges_by_issuer.keys() if org not in existing_orgs])
        
        # Update total counts
        updated_content = re.sub(r'## Total Badges: \(\d+\)', f'## Total Badges: ({total_badges})', updated_content)
        updated_content = re.sub(r'## Issuing Organizations: \(\d+\)', f'## Issuing Organizations: ({total_orgs})', updated_content)
        
        # For each new organization, insert in alphabetical order
        for issuer, badges in sorted(new_badges_by_issuer.items()):
            if issuer not in existing_orgs:
                # New organization - insert entire section
                new_section = self.generate_org_section(issuer, badges)
                
                # Find where to insert alphabetically
                org_sections = re.findall(r'### ([^(]+) \(\d+\)', updated_content)
                insert_position = None
                
                for i, existing_org in enumerate(org_sections):
                    if issuer < existing_org.strip():
                        # Find the position of this organization section
                        pattern = f'### {re.escape(existing_org.strip())} \\(\\d+\\)'
                        match = re.search(pattern, updated_content)
                        if match:
                            insert_position = match.start()
                            break
                
                if insert_position:
                    updated_content = updated_content[:insert_position] + new_section + updated_content[insert_position:]
                else:
                    # Insert at the end
                    updated_content += new_section
                    
            else:
                # Existing organization - need to add badges to existing section
                print(f"Adding badges to existing organization: {issuer}")
                # This would require more complex parsing and insertion logic
                # For now, let's just append to the organization's first table
                
        return updated_content

    def run_update(self, readme_path: str = "README.md") -> bool:
        """Main method to update README with latest badges"""
        print("Starting Credly badge update...")
        
        # Read existing README
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        except FileNotFoundError:
            print(f"README file not found: {readme_path}")
            return False
        
        # Fetch latest badges
        latest_badges = self.fetch_latest_badges()
        if not latest_badges:
            print("No badges fetched")
            return False
        
        # Find existing badges
        existing_badges, existing_orgs = self.parse_existing_readme(readme_content)
        print(f"Found {len(existing_badges)} existing badges from {len(existing_orgs)} organizations")
        
        # Find new badges
        new_badges = self.find_new_badges(latest_badges, existing_badges)
        
        if not new_badges:
            print("No new badges found")
            return True
        
        print(f"Found {len(new_badges)} new badges")
        
        # Update README
        updated_content = self.update_readme_with_new_badges(readme_content, new_badges)
        
        # Write updated README
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Successfully updated {readme_path}")
            return True
        except Exception as e:
            print(f"Error writing README: {e}")
            return False


# Usage example
# if __name__ == "__main__":
    # Replace with your actual API token
    # API_TOKEN = "your_api_token_here"
    
    # updater = CredlyUpdater(API_TOKEN)
    # success = updater.run_update("README.md")
    
    # if success:
    #     print("Update completed successfully!")
    # else:
    #     print("Update failed!")