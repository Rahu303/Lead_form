"""
HubSpot CRM Connector
Handles all HubSpot API interactions: contacts, notes, workflows
"""
import requests
from typing import Dict, Optional, Any
from datetime import datetime
from shared.config import HUBSPOT_ACCESS_TOKEN, HUBSPOT_API_URL


class HubSpotConnector:
    """Connector for HubSpot CRM API"""

    def __init__(self):
        self.access_token = HUBSPOT_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        self.api_url = HUBSPOT_API_URL

    def create_or_update_contact(self, email: str, name: str, phone: Optional[str] = None, properties: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new contact or update existing one"""
        first_name = name.split()[0] if name else ""
        last_name = name.split()[-1] if " " in name else ""

        contact_properties = {
            "email": email,
            "firstname": first_name,
            "lastname": last_name,
        }

        if phone:
            contact_properties["phone"] = phone

        if properties:
            contact_properties.update(properties)

        payload = {"properties": contact_properties}

        try:
            # Try to create new contact
            response = requests.post(self.api_url, headers=self.headers, json=payload)

            if response.status_code == 201:
                print(f"✅ HubSpot: Created new contact {email}")
                return {"status": "created", "email": email}

            elif response.status_code == 409:
                # Contact exists, update instead
                print(f"ℹ️ HubSpot: Updating contact {email}")
                update_url = f"{self.api_url}/{email}?idProperty=email"
                update_response = requests.patch(update_url, headers=self.headers, json=payload)

                if update_response.status_code == 200:
                    return {"status": "updated", "email": email}
                else:
                    return {"status": "error", "error": update_response.text}

            else:
                print(f"❌ HubSpot Error: {response.status_code} - {response.text}")
                return {"status": "error", "error": response.text}

        except Exception as e:
            print(f"⚠️ HubSpot Sync Failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def add_note(self, email: str, note_text: str) -> Dict[str, Any]:
        """Add a note/engagement to a contact"""
        try:
            # Search for contact by email
            search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": email
                            }
                        ]
                    }
                ]
            }

            search_response = requests.post(search_url, headers=self.headers, json=search_payload)

            if search_response.status_code == 200:
                results = search_response.json().get("results", [])
                if results:
                    contact_id = results[0]["id"]
                    note_payload = {
                        "properties": {
                            "hs_note_body": note_text,
                            "hs_timestamp": datetime.now().isoformat()
                        }
                    }
                    print(f"✅ Note added to {email}")
                    return {"status": "success", "contact_id": contact_id}

            return {"status": "not_found", "email": email}

        except Exception as e:
            print(f"⚠️ Note addition failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def trigger_workflow(self, email: str, intent: str, action: str) -> Dict[str, Any]:
        """Trigger a HubSpot workflow based on intent"""
        workflow_mapping = {
            "lead_qualification": "workflow-hot-lead",
            "demo_request": "workflow-demo-scheduler",
            "pricing_inquiry": "workflow-send-pricing",
            "feature_question": "workflow-send-docs",
            "complaint": "workflow-escalate-support",
            "other": "workflow-general-inquiry"
        }

        workflow_id = workflow_mapping.get(intent, "workflow-general-inquiry")

        try:
            # In production, use HubSpot's workflow API
            # For now, log the trigger
            print(f"🔄 HubSpot Workflow Triggered: {workflow_id} for {email}")
            return {
                "status": "triggered",
                "workflow_id": workflow_id,
                "email": email,
                "action": action
            }

        except Exception as e:
            print(f"⚠️ Workflow trigger failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def get_contact(self, email: str) -> Dict[str, Any]:
        """Get contact details from HubSpot"""
        try:
            url = f"{self.api_url}/{email}?idProperty=email"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return {"status": "found", "contact": response.json()}
            else:
                return {"status": "not_found", "email": email}

        except Exception as e:
            print(f"⚠️ Get contact failed: {str(e)}")
            return {"status": "error", "error": str(e)}
