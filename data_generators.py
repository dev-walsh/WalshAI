"""Add missing methods to the UKDataGenerator class and correct the connection issues."""
"""
Data Generation Utilities for Profile Creation
Centralized data generation with UK-specific formatting
"""

import random
import string
from typing import Dict, List
from datetime import datetime, timedelta

class UKDataGenerator:
    """UK-specific data generation utilities"""

    # UK Data Constants
    UK_POSTCODES = [
        "SW1A 1AA", "M1 1AA", "B33 8TH", "W1A 0AX", "EC1A 1BB", "N1 9GU",
        "E14 5HP", "SE1 9BA", "NW1 6XE", "E1 6AN", "SW7 2AZ", "WC2H 7LT",
        "LS1 1UR", "M3 4EN", "B1 1HH", "G1 1AA", "EH1 1YZ", "CF10 3AT",
        "BT1 5GS", "AB10 1XG", "PL1 2AA", "EX1 1AA", "TR1 2HE", "TQ1 2AA"
    ]

    UK_NAMES = {
        'male_first': [
            "James", "Robert", "John", "Michael", "David", "William", "Richard", 
            "Joseph", "Christopher", "Andrew", "Daniel", "Matthew", "Anthony", 
            "Mark", "Paul", "Steven", "Kenneth", "Joshua", "Kevin", "Brian"
        ],
        'female_first': [
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", 
            "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", 
            "Helen", "Sandra", "Donna", "Carol", "Ruth", "Sharon", "Michelle"
        ],
        'last': [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", 
            "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor", 
            "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", 
            "White", "Lopez", "Lee", "Gonzalez", "Harris", "Clark", "Lewis", 
            "Robinson", "Walker", "Perez", "Hall"
        ]
    }

    UK_CITIES = [
        "London", "Manchester", "Birmingham", "Leeds", "Liverpool", "Sheffield", 
        "Bristol", "Newcastle", "Nottingham", "Leicester", "Coventry", "Bradford",
        "Cardiff", "Belfast", "Edinburgh", "Glasgow", "Plymouth", "Southampton"
    ]

    UK_COUNTIES = [
        "Greater London", "Greater Manchester", "West Midlands", "West Yorkshire", 
        "Merseyside", "South Yorkshire", "Avon", "Tyne and Wear", "Nottinghamshire", 
        "Leicestershire", "Warwickshire", "Hampshire", "Devon", "Surrey"
    ]

    STREET_NAMES = [
        "High Street", "Church Lane", "Victoria Road", "Mill Lane", "School Road", 
        "The Green", "Main Street", "Kings Road", "Queens Avenue", "Park Lane",
        "Oak Avenue", "Rose Street", "Garden Close", "Meadow View", "Hill Top"
    ]

    AREA_CODES = [
        '020', '0121', '0131', '0141', '0151', '0161', '0191', '01273', 
        '01484', '01632', '01234', '01234', '01392', '01752', '023'
    ]

    EMAIL_DOMAINS = [
        'gmail.com', 'outlook.com', 'yahoo.co.uk', 'hotmail.co.uk', 
        'btinternet.com', 'sky.com', 'virginmedia.com'
    ]

    @classmethod
    def generate_complete_profile(cls) -> Dict[str, str]:
        """Generate a complete UK profile"""
        gender = random.choice(['Male', 'Female'])
        first_name = random.choice(
            cls.UK_NAMES['male_first'] if gender == 'Male' 
            else cls.UK_NAMES['female_first']
        )
        last_name = random.choice(cls.UK_NAMES['last'])

        # Generate age between 18-65
        birth_year = random.randint(1959, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)

        address = cls.generate_address()

        return {
            'name': f"{first_name} {last_name}",
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender,
            'dob': f"{birth_day:02d}/{birth_month:02d}/{birth_year}",
            'age': datetime.now().year - birth_year,
            'address': address['full'],
            'city': address['city'],
            'postcode': address['postcode'],
            'ni_number': cls.generate_ni_number(),
            'passport': cls.generate_passport_number(),
            'license': cls.generate_driving_license(),
            'nhs_number': cls.generate_nhs_number(),
            'utr_number': cls.generate_utr_number(),
            'phone': cls.generate_phone_number(),
            'email': cls.generate_email(first_name, last_name),
            'generated_at': datetime.now().isoformat()
        }

    @classmethod
    def generate_address(cls) -> Dict[str, str]:
        """Generate realistic UK address"""
        house_number = random.randint(1, 999)
        street = random.choice(cls.STREET_NAMES)
        city = random.choice(cls.UK_CITIES)
        county = random.choice(cls.UK_COUNTIES)
        postcode = random.choice(cls.UK_POSTCODES)

        return {
            'house': str(house_number),
            'street': street,
            'city': city,
            'county': county,
            'postcode': postcode,
            'full': f"{house_number} {street}\n{city}\n{county}\n{postcode}"
        }

    @classmethod
    def generate_ni_number(cls) -> str:
        """Generate National Insurance number with correct format"""
        # NI format: 2 letters + 6 digits + 1 letter
        letters = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=2))
        numbers = ''.join(random.choices('0123456789', k=6))
        suffix = random.choice(['A', 'B', 'C', 'D'])
        return f"{letters} {numbers[:2]} {numbers[2:4]} {numbers[4:6]} {suffix}"

    @classmethod
    def generate_passport_number(cls) -> str:
        """Generate UK passport number (9 digits)"""
        return f"{random.randint(100000000, 999999999)}"

    @classmethod
    def generate_driving_license(cls) -> str:
        """Generate UK driving license number"""
        # UK license format: 5 letters + 6 digits + 2 letters + 2 digits
        surname_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
        digits = ''.join(random.choices('0123456789', k=6))
        initials = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        final_digits = ''.join(random.choices('0123456789', k=2))
        return f"{surname_part}{digits}{initials}{final_digits}"

    @classmethod
    def generate_nhs_number(cls) -> str:
        """Generate NHS number format"""
        return f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"

    @classmethod
    def generate_utr_number(cls) -> str:
        """Generate UTR (Unique Taxpayer Reference) number"""
        return f"{random.randint(1000000000, 9999999999)}"

    @classmethod
    def generate_phone_number(cls) -> str:
        """Generate realistic UK phone number"""
        area_code = random.choice(cls.AREA_CODES)

        if area_code == '020':  # London
            return f"{area_code} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        elif len(area_code) == 5:  # 5-digit area codes
            return f"{area_code} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        else:  # 4-digit area codes
            return f"{area_code} {random.randint(100, 999)} {random.randint(1000, 9999)}"

    @classmethod
    def generate_email(cls, first_name: str, last_name: str) -> str:
        """Generate realistic email address"""
        domain = random.choice(cls.EMAIL_DOMAINS)

        # Various email formats
        formats = [
            f"{first_name.lower()}.{last_name.lower()}",
            f"{first_name.lower()}{last_name.lower()}",
            f"{first_name[0].lower()}{last_name.lower()}",
            f"{first_name.lower()}.{last_name[0].lower()}",
            f"{first_name.lower()}{random.randint(1, 999)}"
        ]

        username = random.choice(formats)
        return f"{username}@{domain}"

    @classmethod
    def generate_document_set(cls) -> Dict[str, str]:
        """Generate complete set of UK documents"""
        return {
            'ni_number': cls.generate_ni_number(),
            'passport': cls.generate_passport_number(),
            'driving_license': cls.generate_driving_license(),
            'nhs_number': cls.generate_nhs_number(),
            'utr_number': cls.generate_utr_number()
        }

    @staticmethod
    def generate_contact_details():
        """Generate UK contact details"""
        area_codes = ['020', '0121', '0131', '0141', '0113', '0114', '0115', '0116', '0117', '0118']
        mobile_prefixes = ['07700', '07701', '07702', '07703', '07704', '07705']

        first_name = random.choice(UKDataGenerator.UK_NAMES['male_first']).lower()
        last_name = random.choice(UKDataGenerator.UK_NAMES['last']).lower()

        return {
            'phone': f"{random.choice(area_codes)} {random.randint(100, 999)} {random.randint(1000, 9999)}",
            'mobile': f"{random.choice(mobile_prefixes)} {random.randint(100000, 999999)}",
            'email': f"{first_name}.{last_name}@{random.choice(['gmail.com', 'outlook.com', 'yahoo.co.uk', 'btinternet.com'])}",
            'alt_email': f"{first_name}{random.randint(1, 99)}@{random.choice(['hotmail.co.uk', 'live.co.uk', 'icloud.com'])}"
        }

    @staticmethod
    def generate_business_profile():
        """Generate a complete UK business profile"""
        company_types = [
            "Limited Company", "LLP", "PLC", "Community Interest Company",
            "Partnership", "Sole Trader", "Social Enterprise"
        ]

        industries = [
            "Technology", "Finance", "Property Development", "Consulting",
            "Manufacturing", "Retail", "Healthcare", "Education",
            "Construction", "Media", "Legal Services", "Accounting"
        ]

        first_name = random.choice(UKDataGenerator.UK_NAMES['male_first'])
        last_name = random.choice(UKDataGenerator.UK_NAMES['last'])

        return {
            'company_name': f"{last_name} {random.choice(['Holdings', 'Group', 'Enterprises', 'Solutions', 'Partners', 'Associates'])} Ltd",
            'company_number': f"{random.randint(10000000, 99999999):08d}",
            'vat_number': f"GB{random.randint(100000000, 999999999)}",
            'business_type': random.choice(company_types),
            'industry': random.choice(industries),
            'registered_address': UKDataGenerator.generate_address()['full'],
            'directors': f"{first_name} {last_name}",
            'incorporation_date': UKDataGenerator.generate_random_date(1990, 2023)
        }

    @staticmethod
    def generate_random_date(start_year: int, end_year: int) -> str:
        """Generate a random date between start_year and end_year"""
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Use 28 to avoid month-specific day issues
        return f"{day:02d}/{month:02d}/{year}"

class ScamDatabase:
    """Comprehensive scam detection database"""

    SCAM_TYPES = {
        'romance_scams': {
            'description': 'Emotional manipulation for financial gain',
            'warning_signs': [
                'Too good to be true profile',
                'Immediate love declarations',
                'Refuses video calls',
                'Always traveling/military',
                'Financial emergencies',
                'Poor grammar/language',
                'Stolen profile photos'
            ],
            'common_stories': [
                'Military deployment',
                'Business trip abroad',
                'Medical emergency',
                'Inheritance issues',
                'Travel expenses',
                'Custom fees',
                'Family crisis'
            ],
            'protection': [
                'Video call before meeting',
                'Never send money',
                'Reverse image search photos',
                'Meet in public places',
                'Verify identity independently'
            ]
        },
        'investment_scams': {
            'description': 'Fake investment opportunities promising high returns',
            'warning_signs': [
                'Guaranteed high returns',
                'Pressure to invest quickly',
                'Unregistered investments',
                'Complex strategies',
                'Celebrity endorsements',
                'Limited time offers'
            ],
            'common_types': [
                'Ponzi schemes',
                'Pyramid schemes',
                'Fake cryptocurrency',
                'Forex scams',
                'Binary options',
                'Advance fee fraud'
            ],
            'protection': [
                'Check regulatory registration',
                'Get independent advice',
                'Be skeptical of guarantees',
                'Research thoroughly',
                'Start with small amounts'
            ]
        },
        'phishing_scams': {
            'description': 'Attempts to steal personal information through fake communications',
            'warning_signs': [
                'Urgent action required',
                'Generic greetings',
                'Suspicious links',
                'Grammar errors',
                'Unexpected attachments',
                'Requests for passwords'
            ],
            'common_themes': [
                'Bank security alerts',
                'Package delivery',
                'Tax refunds',
                'Account suspensions',
                'Prize winnings',
                'Security breaches'
            ],
            'protection': [
                'Verify sender independently',
                'Check sender independently',
                'Check URLs carefully',
                'Never click suspicious links',
                'Use two-factor authentication',
                'Keep software updated'
            ]
        },
        'crypto_scams': {
            'description': 'Cryptocurrency-related fraudulent schemes',
            'warning_signs': [
                'Guaranteed profits',
                'Celebrity endorsements',
                'Pump and dump schemes',
                'Fake exchanges',
                'Giveaway scams',
                'Cloud mining offers'
            ],
            'common_types': [
                'Fake ICOs',
                'Mining scams',
                'Wallet theft',
                'Exchange fraud',
                'Rug pulls',
                'Fake trading bots'
            ],
            'protection': [
                'Use reputable exchanges',
                'Store coins securely',
                'Research thoroughly',
                'Be wary of social media promotions',
                'Never share private keys'
            ]
        }
    }

    @classmethod
    def get_scam_info(cls, scam_type: str) -> Dict:
        """Get information about specific scam type"""
        return cls.SCAM_TYPES.get(scam_type, {})

    @classmethod
    def analyze_text_for_scams(cls, text: str) -> List[str]:
        """Analyze text for scam indicators"""
        text_lower = text.lower()
        detected_scams = []

        for scam_type, info in cls.SCAM_TYPES.items():
            for warning_sign in info.get('warning_signs', []):
                if warning_sign.lower() in text_lower:
                    detected_scams.append(scam_type)
                    break

        return list(set(detected_scams))  # Remove duplicates