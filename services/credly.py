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
            "img": badge["image_url"] if badge["image_url"] else badge_template["image_url"],
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

    def org_logos(self, issuer):
        logos = {
            "APIsec University": "https://images.credly.com/size/200x200/images/722366ec-1535-4d51-ac31-f5294833e3d4/blob.png",
            "Acronis": "https://images.credly.com/size/200x200/images/d498c506-056e-4062-905a-c757724a4b23/blob.png",
            "Alation University": "https://images.credly.com/size/400x400/images/491c6659-8c88-4158-80f2-3228bf18db12/blob",
            "Adobe Education": "https://images.credly.com/size/200x200/images/bb708792-a2f0-4b4a-bc7d-27d4423938af/blob.png",
            "Alteryx": "https://images.credly.com/size/200x200/images/b8079e20-ff5f-47c4-aadd-494b54ef02eb/blob.png",
            "Amazon Web Services Training and Certification": "https://images.credly.com/size/400x400/images/14a6da77-7f93-4867-81ef-ad7c6a400ec2/blob.png",
            "Appcues": "https://images.credly.com/size/200x200/images/98f63591-3d90-46a9-bc4f-25ca3044459e/blob.png",
            "AttackIQ": "https://images.credly.com/size/200x200/images/26bc3c78-d2d2-4fda-9464-c28609f305eb/blob.png",
            "Basis Technologies": "https://images.credly.com/size/200x200/images/93556319-5a06-4a08-a363-6390d8d8cf3e/blob.png",
            "Broadcom": "https://images.credly.com/size/200x200/images/e0b1d3bf-8d7f-4bc8-b0ff-4b6515b72561/blob.png",
            "Camunda": "https://images.credly.com/size/200x200/images/deb111b4-fd83-428d-b0b8-b8a450b21e03/blob.png",
            "Celonis": "https://images.credly.com/size/200x200/images/f38665cc-b74f-4149-b784-c7302afc6461/blob.png",
            "Certiprof": "https://images.credly.com/size/200x200/images/1598437d-f59f-4f0f-a138-7e00c69acbce/blob",
            "Chainguard": "https://images.credly.com/size/200x200/images/467f64a1-5da5-4e25-8b11-35a93fc11ec6/blob",
            "Cisco": "https://images.credly.com/size/200x200/images/81324abf-aff1-44e3-b36b-130a7b8361a0/blob.png",
            "ClickHouse": "https://images.credly.com/size/200x200/images/2471a383-fb15-4cb8-84f0-1b14f3a926be/blob.png",
            "CompTIA": "https://images.credly.com/size/200x200/images/1d9d2038-abf7-49b4-a8db-c6fb884dfdb5/blob.png",
            "Datadog": "https://images.credly.com/size/200x200/images/cd7dca42-ab31-41a9-9d2d-d90f37dced30/blob.png",
            "Data Protocol": "https://images.credly.com/size/200x200/images/96cd563f-98e3-4f18-9ab8-240bc7aead90/blob.png",
            "data.world": "https://images.credly.com/size/400x400/images/a878e5a2-7045-4d4f-a6fe-48c61eeede6e/blob",
            "Dremio": "https://images.credly.com/size/200x200/images/3627d9c5-d7db-4d16-8a70-18a0587a4775/organization-600x600.png",
            "Extreme Networks": "https://images.credly.com/size/200x200/images/f4a679e4-a683-4475-8f1e-3e36d05d2a38/blob.png",
            "Google Cloud": "https://images.credly.com/size/200x200/images/ca55a8cf-9e9c-47e3-9378-d225d63dd1e5/blob.png",
            "Hewlett Packard Enterprise": "https://images.credly.com/size/200x200/images/e18e9c8e-9303-4c7d-9fd6-cbb222bc64c2/HPE_logo.png",
            "IBM": "https://images.credly.com/size/200x200/images/854d76bf-4f74-4d51-98a0-d969214bfba7/IBM%2BLogo%2Bfor%2BAcclaim%2BProfile.png",
            "IBM SkillsBuild": "https://images.credly.com/size/200x200/images/adc55fbb-55a1-425c-b133-6ed5b83f5d38/blob.png",
            "ISC2": "https://images.credly.com/size/200x200/images/0e8d9cd4-ce53-4afd-be2e-d8b30021b61b/blob.png",
            "Ikigai Labs": "https://images.credly.com/size/200x200/images/65eec552-fee8-4948-bb86-5849368d57eb/blob.png",
            "Intel": "https://images.credly.com/size/200x200/images/51b8845c-9404-4d49-be09-8decec250beb/blob.png",
            "Kong": "https://images.credly.com/size/200x200/images/85dcf844-10cc-4587-8534-cc68b6595f8e/blob.png",
            "Lucid Software": "https://images.credly.com/size/400x400/images/a0c7f3d8-9517-4b95-8a95-6ba75a03f360/blob.png",
            "Make": "https://images.credly.com/size/200x200/images/7b59869c-3ce2-4c2a-85a5-e160dc33081b/blob.png",
            "MongoDB": "https://images.credly.com/size/200x200/images/ef0ef46d-47a5-4025-a1bc-9d46732310da/blob.png",
            "NetApp": "https://images.credly.com/size/200x200/images/92e705f4-b027-4d05-94fa-6d55048f2d92/NetApp_Logo.png",
            "NASA Open Science": "https://images.credly.com/size/200x200/images/d2cf3383-8989-4acd-8cb8-4ca9024643fc/blob.png",
            "Okta": "https://images.credly.com/size/200x200/images/b83732ea-b75e-4335-8fd7-7749615387d2/blob",
            "OPSWAT": "https://images.credly.com/size/200x200/images/a5a39dfa-c315-422c-90d2-4b954b66ed28/blob.png",
            "Pendo": "https://images.credly.com/size/200x200/images/648b5cb8-8fc1-44df-9a2e-6a4f3e86f49e/blob.png",
            "ProcessMaker": "https://images.credly.com/size/200x200/images/7b79da44-2fa1-4bbf-b638-11f7e3284908/blob",
            "Project Management Institute": "https://images.credly.com/size/200x200/images/31da017a-a50c-48a8-8012-c4811063581f/blob.png",
            "SAP": "https://images.credly.com/size/200x200/images/cc566727-d258-4291-8bb5-cfffb53ebb9a/SAP_org.png",
            "SAS": "https://images.credly.com/size/200x200/images/b108f83f-fedf-4479-8515-48a48a9df862/blob.png",
            "Software AG": "https://images.credly.com/size/200x200/images/cb804039-a63a-4e8e-82c8-058b6fcff38a/blob.png",
            "The Linux Foundation": "https://images.credly.com/size/200x200/images/e6066b96-c59d-49b6-87cc-d8873022e84f/blob.png",
            "Tigera": "https://images.credly.com/size/200x200/images/44031b8f-9364-42fb-9ba7-37858c650511/blob.png",
            "ZEDEDA": "https://images.credly.com/size/200x200/images/32b1c161-6993-4b70-a104-ef9301b3b456/blob.png",
            "Zendesk": "https://images.credly.com/size/200x200/images/a648362b-1174-4b27-93f1-a3e12fe6d49a/blob.png"
        }
        return logos.get(issuer, None)

    def org_links(self, issuer):
        org_urls = {
            "APIsec University": "https://www.credly.com/organizations/apisec-university/badges",
            "Acronis": "https://www.credly.com/organizations/acronis/badges",
            "Alation University": "https://www.credly.com/organizations/alation/badges",
            "Adobe Education": "https://www.credly.com/organizations/adobe-education/badges",
            "Alteryx": "https://www.credly.com/organizations/alteryx/badges",
            "Amazon Web Services Training and Certification": "https://www.credly.com/organizations/amazon-web-services/badges",
            "Appcues": "https://www.credly.com/organizations/appcues/badges",
            "AttackIQ": "https://www.credly.com/organizations/attackiq/badges",
            "Basis Technologies": "https://www.credly.com/organizations/basis-technologies/badges",
            "Broadcom": "https://www.credly.com/organizations/broadcom/badges",
            "Camunda": "https://www.credly.com/organizations/camunda/badges",
            "Celonis": "https://www.credly.com/organizations/celonis/badges",
            "Certiprof": "https://www.credly.com/organizations/certiprof/badges",
            "Chainguard": "https://www.credly.com/organizations/chainguard/badges",
            "Cisco": "https://www.credly.com/organizations/cisco/badges",
            "ClickHouse": "https://www.credly.com/organizations/clickhouse/badges",
            "CompTIA": "https://www.credly.com/organizations/comptia/badges",
            "Datadog": "https://www.credly.com/organizations/datadog/badges",
            "Data Protocol": "https://www.credly.com/organizations/data-protocol/badges",
            "data.world": "https://www.credly.com/organizations/data-world/badges",
            "Dremio": "https://www.credly.com/organizations/dremio/badges",
            "Extreme Networks": "https://www.credly.com/organizations/extreme-networks/badges",
            "Google Cloud": "https://www.credly.com/organizations/google-cloud/badges",
            "Hewlett Packard Enterprise": "https://www.credly.com/organizations/hewlett-packard-enterprise/badges",
            "IBM": "https://www.credly.com/organizations/ibm/badges",
            "IBM SkillsBuild": "https://www.credly.com/organizations/ibm-skillsbuild/badges",
            "ISC2": "https://www.credly.com/organizations/isc2/badges",
            "Ikigai Labs": "https://www.credly.com/organizations/ikigai-labs/badges",
            "Intel": "https://www.credly.com/organizations/intel/badges",
            "Kong": "https://www.credly.com/organizations/kong/badges",
            "Lucid Software": "https://www.credly.com/organizations/lucidsoftware/badges",
            "Make": "https://www.credly.com/organizations/make/badges",
            "MongoDB": "https://www.credly.com/organizations/mongodb/badges",
            "NetApp": "https://www.credly.com/organizations/netapp/badges",
            "NASA Open Science": "https://www.credly.com/organizations/nasa-open-science/badges",
            "Okta": "https://www.credly.com/organizations/okta/badges",
            "OPSWAT": "https://www.credly.com/organizations/opswat/badges",
            "Pendo": "https://www.credly.com/organizations/pendo/badges",
            "ProcessMaker": "https://www.credly.com/organizations/processmaker/badges",
            "Project Management Institute": "https://www.credly.com/organizations/project-management-institute/badges",
            "SAP": "https://www.credly.com/organizations/sap/badges",
            "SAS": "https://www.credly.com/organizations/sas/badges",
            "Software AG": "https://www.credly.com/organizations/software-ag/badges",
            "The Linux Foundation": "https://www.credly.com/organizations/the-linux-foundation/badges",
            "Tigera": "https://www.credly.com/organizations/tigera/badges",
            "ZEDEDA": "https://www.credly.com/organizations/zededa/badges",
            "Zendesk": "https://www.credly.com/organizations/zendesk/badges"
        }
        return org_urls.get(issuer, None)
    
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

    def twenty_word_limit(self, text):
        """Helper function to limit text to 20 words. Returns the text if it is less than or equal to 20 words, otherwise returns the first 20 words followed by '...' and the remaining words as a separate string variable."""
        words = text.split()
        if len(words) <= 20:
            return text, None
        else:
            limited_text = " ".join(words[:20]) + "..."
            remaining_text = " ".join(words[20:])
            return limited_text, remaining_text

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
            description, remaining_description = self.twenty_word_limit(badge["description"])
            rows += f'      <strong>Description:</strong> {description}<br>\n'
            if remaining_description:
                rows += f'      <details>\n'
                rows += f'        <summary>Show more</summary>\n'
                rows += f'        {remaining_description}\n'
                rows += f'      </details>\n'
            rows += f'      <strong>Skills:</strong> {", ".join(badge["skills"])}<br>\n'
            rows += f'      <strong>Criteria:</strong> {badge["criteria"]}<br>\n'
            rows += f'      <strong>Time to Earn:</strong> {badge["time_to_earn"]}<br>\n'
            rows += f'      <strong>Level:</strong> {badge.get("level", "N/A")}\n'
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
        markdown += f"## List of Issuing Organizations: ({len(grouped_badges)})\n\n"
        markdown += "| Issuing Organization | Description | Credly Badges | Verified | Organization Link |\n"
        markdown += "|        :---:         |-------------|     :---:     |   :---:  |       :---:       |\n"
        for issuer in grouped_badges.keys():
            anchor = issuer.lower().replace(" ", "-").replace(".", "-")
            markdown += f"| <img src='{self.org_logos(issuer)}' height='100' /><br>[{issuer}](#{anchor}-{len(grouped_badges.get(issuer, []))}) | {self.org_descriptions(issuer)} | {len(grouped_badges.get(issuer, []))} | ✅ | [{issuer}]({self.org_links(issuer)}) |\n"
        markdown += "\n\n"

        for issuer, badges in grouped_badges.items():
            anchor = issuer.lower().replace(" ", "-")
            markdown += '<br>\n'
            markdown += f"### {issuer} ({len(badges)})\n"
            markdown += f'<br><br>\n\n'
            markdown += f'<strong><a href="#user-content-free-credly-badges">Back to Top ⬆️</a></strong>\n\n'
            markdown += '<table width="100%" border="1" cellspacing="0" cellpadding="4">\n'
            markdown += '  <tr>\n'
            markdown += '    <th width="20%">Badge</th>\n'
            markdown += '    <th width="80%">Description, Time to Earn, Skills & Earning Criteria</th>\n'
            markdown += '  </tr>\n'

            # Generate rows for the first 5 badges
            markdown += self.generate_badge_rows(badges[:5])
            markdown += '</table>\n\n'

            # If there are more than 5 badges, create a "more" dropdown
            if len(badges) > 5:
                markdown += '<br>\n'
                markdown += f'<details>\n  <summary>More {issuer} ({len(badges) - 5}</summary>\n\n'
                markdown += f'<br><br>\n\n'
                markdown += f'<strong><a href="#user-content-free-credly-badges">Back to Top ⬆️</a></strong>\n\n'
                markdown += '<table width="100%" border="1" cellspacing="0" cellpadding="4">\n'
                markdown += '  <tr>\n'
                markdown += '    <th width="20%">Badge</th>\n'
                markdown += '    <th width="80%">Description, Time to Earn, Skills & Earning Criteria</th>\n'
                markdown += '  </tr>\n'

                # Generate rows for the remaining badges
                markdown += self.generate_badge_rows(badges[5:])
                markdown += '</table>\n\n'
                markdown += '</details>\n\n'
        
        # Print tail of the markdown
        print(markdown.split("\n")[-100:])
        return markdown

    def get_markdown(self):
        badges = self.return_badges_html()
        broken_images = {
            "Getting Started with Data": "http://www.credly.com/badges/bcd2b361-ce6d-4bb7-9fc4-4bba25cc6a7f",
            "Getting Started with Cybersecurity": "http://www.credly.com/badges/ce8f9f38-c187-40f5-aa9c-db72b3c29698",
            "Generative AI in Action": "http://www.credly.com/badges/857864af-eead-46d0-9805-8d825642aa6d",
            "Getting Started with Artificial Intelligence": "http://www.credly.com/badges/e0f49a38-3af6-4eb5-a69d-2e16931972c2",
        }

        # Find and replace broken image URLs
        for badge in badges:
            if badge["title"] in broken_images:
                badge["img"] = broken_images[badge["title"]]
                print(f"Replacing broken image URL for {badge['title']}")
                print(f"New image URL: {badge['img']}")
        return self.generate_md_format(badges)