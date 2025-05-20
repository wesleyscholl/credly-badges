from bs4 import BeautifulSoup
import lxml, requests
import time

# All badges listed on this github page are completely free, no payment required. There are thousands of free training resources available but not all have certificates, badges or proof of completion. 

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

    def replace_broken_images(self, badge):
        """Replace known broken image links with functional ones."""
        broken_images = {
            "https://www.credly.com/org/ibm-skillsbuild/badge/getting-started-with-data": "http://www.credly.com/badges/bcd2b361-ce6d-4bb7-9fc4-4bba25cc6a7f",
            "https://www.credly.com/org/ibm-skillsbuild/badge/getting-started-with-cybersecurity": "http://www.credly.com/badges/ce8f9f38-c187-40f5-aa9c-db72b3c29698",
            "https://www.credly.com/org/ibm-skillsbuild/badge/generative-ai-in-action": "http://www.credly.com/badges/857864af-eead-46d0-9805-8d825642aa6d",
            "https://www.credly.com/org/ibm-skillsbuild/badge/getting-started-with-artificial-intelligence": "http://www.credly.com/badges/e0f49a38-3af6-4eb5-a69d-2e16931972c2",
        }

        # Check if the badge's href matches a known broken link
        if badge["img"] in broken_images:
            badge["img"] = broken_images[badge["img"]]
        return badge

    def convert_to_dict(self, badge):
        badge_template = badge["badge_template"]
        issuer = badge["issuer"]["entities"][0]["entity"]["name"] if badge["issuer"]["entities"] else "Unknown Issuer"

        activities = badge_template.get("badge_template_activities", [])
        criteria = ", ".join(activity.get("title", "No criteria provided") for activity in activities if isinstance(activity, dict))

        badge_dict = {
            "title": badge_template["name"],
            "href": badge_template["url"],
            "img": badge_template["image_url"].replace("110x110", f"{BADGE_SIZE}x{BADGE_SIZE}"),
            "issuer": issuer,
            "description": badge_template["description"],
            "time_to_earn": badge_template["time_to_earn"],
            "skills": badge_template["skills"],
            "criteria": criteria,
        }
        
        if issuer == "IBM SkillsBuild":
            return self.replace_broken_images(badge_dict)
        else
            return badge_dict

    def return_badges_html(self):
        badges = self.fetch_badges()
        return [self.convert_to_dict(badge) for badge in badges]

    def org_descriptions(self, issuer):
        descriptions = {
            "APIsec University": "APIsec University is a learning platform focused on API security, offering certifications to strengthen secure development practices.",
            "Acronis": "Acronis is a global leader in cyber protection, specializing in data backup, recovery, and secure file access.",
            "Alation University": "Alation University provides training and certification programs for data governance, analytics, and data literacy.",
            "Adobe Education": "Adobe's educational initiative that provides creative tools and resources for students and educators.",
            "Alteryx": "Alteryx is a data analytics company known for its user-friendly platform that enables data blending and advanced analytics.",
            "Amazon Web Services Training and Certification": "AWS's official training body offering cloud computing certifications and skill development.",
            "Appcues": "Appcues is a platform that helps product teams build personalized user onboarding and in-app experiences without code.",
            "AttackIQ": "AttackIQ is a cybersecurity company that provides breach and attack simulation tools to test and improve defenses.",
            "Basis Technologies": "Basis Technologies specializes in DevOps and automation tools for SAP systems to accelerate digital transformation.",
            "Broadcom": "Broadcom is a global technology leader that designs, develops, and supplies semiconductor and infrastructure software solutions.",
            "Camunda": "Camunda is a software company that provides open-source process automation solutions for business process management.",
            "Celonis": "Celonis is a process mining software company helping businesses discover and fix inefficiencies in their operations.",
            "Certiprof": "Certiprof is a certification provider offering globally recognized credentials in project management, IT, and business agility.",
            "Chainguard": "Chainguard is a cybersecurity company focused on securing software supply chains and containerized applications.",
            "Cisco": "Cisco is a multinational technology conglomerate known for networking hardware, cybersecurity, and IT certifications.",
            "ClickHouse": "ClickHouse is an open-source columnar database management system optimized for real-time analytical queries.",
            "CompTIA": "CompTIA is a nonprofit trade association providing vendor-neutral IT certifications and professional development.",
            "Datadog": "Datadog is a monitoring and analytics platform for developers, IT operations teams, and business users.",
            "Data Protocol": "Data Protocol is an educational platform offering bite-sized technical training for developers in modern data tools.",
            "data.world": "data.world is a cloud-based data collaboration platform that enables teams to work with data and analytics.",
            "Dremio": "Dremio is a data lakehouse platform that simplifies and accelerates analytics directly on cloud data lakes.",
            "Extreme Networks": "Extreme Networks provides cloud-driven networking solutions and services for enterprise-level connectivity.",
            "Google Cloud": "Google Cloud is Google's cloud computing division, offering infrastructure, machine learning, and development tools.",
            "Hewlett Packard Enterprise": "Hewlett Packard Enterprise specializes in enterprise IT solutions including servers, storage, and cloud services.",
            "IBM": "IBM is a multinational technology company offering AI, cloud computing, and enterprise software solutions.",
            "IBM SkillsBuild": "IBM SkillsBuild is an IBM initiative offering free digital learning and career-readiness programs for job seekers.",
            "ISC2": "ISC2 is a nonprofit organization offering cybersecurity certifications, including the well-known CISSP.",
            "Ikigai Labs": "Ikigai Labs provides AI/ML platforms that enable easy building and deployment of predictive analytics workflows.",
            "Intel": "Intel is a leading semiconductor manufacturer known for CPUs, data center solutions, and AI hardware innovation.",
            "Kong": "Kong is an open-source API management and microservices platform for modern distributed architectures.",
            "Lucid Software": "Lucid Software offers collaborative diagramming and whiteboarding tools like Lucidchart and Lucidspark.",
            "Make": "Make is a no-code automation platform that allows users to connect apps and automate workflows without programming.",
            "MongoDB": "MongoDB is the creator of the popular NoSQL database known for flexibility and scalability in modern application development.",
            "NetApp": "NetApp is a data management and cloud storage company providing solutions for hybrid cloud environments.",
            "NASA Open Science": "NASA Open Science is a program by NASA promoting open access to scientific data, tools, and research collaboration.",
            "Okta": "Okta is a leading identity and access management platform providing secure authentication for users and applications.",
            "OPSWAT": "Opswat is a cybersecurity company specializing in data sanitization and threat detection solutions.",
            "Pendo": "Pendo is a product experience platform that helps software teams improve user onboarding, feedback, and retention.",
            "ProcessMaker": "ProcessMaker is a leading business process management (BPM) and workflow automation platform that enables organizations to design, automate, and optimize business workflows.",
            "Project Management Institute": "PMI is a global organization offering standards and certifications in project management, including the PMP.",
            "SAP": "SAP is a global enterprise software leader in ERP, data analytics, and digital transformation solutions.",
            "SAS": "SAS specializes in advanced analytics, AI, and business intelligence software and services.",
            "Software AG": "Software AG is a global software company providing solutions for integration, API management, and business process management.",
            "The Linux Foundation": "The Linux Foundation is a nonprofit that supports open-source innovation and provides training in Linux and emerging technologies.",
            "Tigera": "Tigera is a cybersecurity company specializing in cloud-native security and observability for Kubernetes environments.",
            "ZEDEDA": "ZEDEDA offers edge computing orchestration solutions for deploying and managing applications at the network edge.",
            "Zendesk": "Zendesk is a customer service and engagement platform that helps businesses manage support and improve customer satisfaction."
        }

        if issuer in descriptions:
            return descriptions[issuer]
        else:
            return "..."

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
        markdown += f"## List of Issuing Organizations ({len(grouped_badges)})\n\n"
        markdown += "| Issuing Organization | Description | Credly Badges | Verified |\n"
        markdown += "|-----------------------|----------------|----------------|----------|\n"
        for issuer in grouped_badges.keys():
            anchor = issuer.lower().replace(" ", "-").replace(".", "-")
            markdown += f"| [{issuer}](#{anchor}-{len(grouped_badges.get(issuer, []))}) | {self.org_descriptions(issuer)} | {len(grouped_badges.get(issuer, []))} | ✅ |\n"
        markdown += "\n"

        for issuer, badges in grouped_badges.items():
            anchor = issuer.lower().replace(" ", "-")
            markdown += f"### {issuer} ({len(badges)})\n\n"
            markdown += '<table width="100%">\n'
            markdown += '  <tr>\n'
            markdown += '    <th width="20%">Badge</th>\n'
            markdown += '    <th width="35%">Description</th>\n'
            markdown += '    <th width="15%">Time to Earn</th>\n'
            markdown += '    <th width="15%">Skills</th>\n'
            markdown += '    <th width="15%">Earning Criteria</th>\n'
            markdown += '  </tr>\n'

            # Display the first 5 badges
            first_row = badges[:5]
            for badge in first_row:
                markdown += '  <tr>\n'
                markdown += f'    <td align="center" width="20%"><a href="{badge["href"]}"><img src="{badge["img"]}" /></a><br><a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a></td>\n'
                markdown += f'    <td width="35%">{badge["description"]}</td>\n'
                markdown += f'    <td align="center" width="15%">{badge["time_to_earn"]}</td>\n'
                markdown += f'    <td width="15%">{", ".join(badge["skills"])}</td>\n'
                markdown += f'    <td width="15%">{badge["criteria"]}</td>\n'

                markdown += '  </tr>\n'
            markdown += '</table>\n\n'

            # If there are more than 5 badges, create a "more" dropdown
            if len(badges) > 5:
                markdown += '<br>\n'
                markdown += f'<details>\n  <summary>More {issuer} ({len(badges) - 5})</summary>\n\n'
                markdown += '<table width="100%">\n'
                markdown += '  <tr>\n'
                markdown += '    <th width="20%">Badge</th>\n'
                markdown += '    <th width="35%">Description</th>\n'
                markdown += '    <th width="15%">Time to Earn</th>\n'
                markdown += '    <th width="15%">Skills</th>\n'
                markdown += '    <th width="15%">Earning Criteria</th>\n'
                markdown += '  </tr>\n'

                remaining_badges = badges[5:]
                for badge in remaining_badges:
                    markdown += '  <tr>\n'
                    markdown += f'    <td align="center" width="20%"><a href="{badge["href"]}"><img src="{badge["img"]}" /></a><br><a href="{badge["href"]}">{badge["title"]} - {badge["issuer"]}</a></td>\n'
                    markdown += f'    <td width="35%">{badge["description"]}</td>\n'
                    markdown += f'    <td align="center" width="15%">{badge["time_to_earn"]}</td>\n'
                    markdown += f'    <td width="15%">{", ".join(badge["skills"])}</td>\n'
                    markdown += f'    <td width="15%">{badge["criteria"]}</td>\n'
                    markdown += '  </tr>\n'
                markdown += '</table>\n\n'
                markdown += '</details>\n\n'

        return markdown

    def get_markdown(self):
        badges = self.return_badges_html()
        return self.generate_md_format(badges)