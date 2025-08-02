
import requests
import logging
from typing import Dict, Optional, List
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class CompaniesHouseAPI:
    """Real Companies House API integration for fetching company data"""
    
    def __init__(self):
        self.api_key = os.getenv('COMPANIES_HOUSE_API_KEY', '')
        self.base_url = "https://api.company-information.service.gov.uk"
        self.session = requests.Session()
        
        if self.api_key:
            # Use API key for authentication
            self.session.auth = (self.api_key, '')
        else:
            logger.warning("Companies House API key not found. Using public endpoints only.")
    
    def search_companies(self, company_name: str, limit: int = 5) -> List[Dict]:
        """Search for companies by name"""
        try:
            url = f"{self.base_url}/search/companies"
            params = {
                'q': company_name,
                'items_per_page': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.error(f"Companies House search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return []
    
    def get_company_profile(self, company_number: str) -> Optional[Dict]:
        """Get detailed company profile by company number"""
        try:
            url = f"{self.base_url}/company/{company_number}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get company profile: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting company profile: {e}")
            return None
    
    def get_company_officers(self, company_number: str) -> List[Dict]:
        """Get company officers/directors"""
        try:
            url = f"{self.base_url}/company/{company_number}/officers"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.error(f"Failed to get company officers: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting company officers: {e}")
            return []
    
    def get_company_filing_history(self, company_number: str, limit: int = 10) -> List[Dict]:
        """Get company filing history"""
        try:
            url = f"{self.base_url}/company/{company_number}/filing-history"
            params = {'items_per_page': limit}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.error(f"Failed to get filing history: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting filing history: {e}")
            return []
    
    def lookup_company_comprehensive(self, company_name: str) -> Dict:
        """Comprehensive company lookup with real data"""
        try:
            # First, search for the company
            search_results = self.search_companies(company_name)
            
            if not search_results:
                return {
                    'success': False,
                    'error': f'No companies found matching "{company_name}"',
                    'company_name': company_name
                }
            
            # Get the best match (first result)
            best_match = search_results[0]
            company_number = best_match.get('company_number', '')
            
            if not company_number:
                return {
                    'success': False,
                    'error': 'Company number not found in search results',
                    'company_name': company_name
                }
            
            # Get detailed company profile
            profile = self.get_company_profile(company_number)
            officers = self.get_company_officers(company_number)
            
            if not profile:
                return {
                    'success': False,
                    'error': 'Failed to retrieve company profile',
                    'company_name': company_name
                }
            
            # Format the response with real data
            registered_address = profile.get('registered_office_address', {})
            address_parts = []
            
            if registered_address.get('address_line_1'):
                address_parts.append(registered_address['address_line_1'])
            if registered_address.get('address_line_2'):
                address_parts.append(registered_address['address_line_2'])
            if registered_address.get('locality'):
                address_parts.append(registered_address['locality'])
            if registered_address.get('region'):
                address_parts.append(registered_address['region'])
            if registered_address.get('postal_code'):
                address_parts.append(registered_address['postal_code'])
            if registered_address.get('country'):
                address_parts.append(registered_address['country'])
            
            formatted_address = ', '.join(address_parts) if address_parts else 'Address not available'
            
            # Format directors
            director_names = []
            for officer in officers[:5]:  # Limit to 5 directors
                name = officer.get('name', '')
                if name:
                    director_names.append(name)
            
            directors_text = '; '.join(director_names) if director_names else 'Directors information not available'
            
            # Get SIC codes for industry classification
            sic_codes = profile.get('sic_codes', [])
            industry = 'Unknown'
            if sic_codes:
                industry = f"SIC: {', '.join(sic_codes[:2])}"  # Show first 2 SIC codes
            
            return {
                'success': True,
                'company_name': profile.get('company_name', company_name),
                'company_number': company_number,
                'company_status': profile.get('company_status', 'Unknown'),
                'company_type': profile.get('type', 'Unknown'),
                'incorporation_date': profile.get('date_of_creation', 'Unknown'),
                'registered_address': formatted_address,
                'directors': directors_text,
                'industry': industry,
                'jurisdiction': profile.get('jurisdiction', 'England & Wales'),
                'accounts_next_due': profile.get('accounts', {}).get('next_due', 'Unknown'),
                'confirmation_statement_next_due': profile.get('confirmation_statement', {}).get('next_due', 'Unknown'),
                'data_source': 'Companies House Official API',
                'retrieved_at': datetime.now().isoformat(),
                'links': {
                    'self': profile.get('links', {}).get('self', ''),
                    'officers': f"/company/{company_number}/officers",
                    'filing_history': f"/company/{company_number}/filing-history"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive company lookup: {e}")
            return {
                'success': False,
                'error': f'System error: {str(e)}',
                'company_name': company_name
            }
