import os
import json
import requests
from flask import make_response

"""Return dialog fields for Slack from Jama API

Purpose of this file is to format data in a JSON object that
Slack can handle. Each of the fucntion queries a different REST endpoint
on the Jama instance.

Attributes:
    None
"""

def create_fields(project_id):
    """Returns dialog box
    
    Args: 
        project_id (int): ID of the project that users will get
            from Jama instance
        
    Returns:
        dict

    Raies:
        AssertionException:
            If the GET requests sent to Jama return anything but a
            status of 200, then assertion error will be thrown. 
    """
    # Passes this object back to slack dialog
    return {
        "title": "JamaConnect - Create",
        "submit_label": "Submit",
        "callback_id": "jamaconnect_create_dialog",
        "elements": _fields_array(project_id)
        
    }

# Private helper functions to interface w/ Jama API
def _fields_array(project_id):
    """Creates an array from API data.

    FUNCTION IS PRIVATE

    Returns:
        Array: this array is an object of dicts

    Raises:
        None
    """

    prj_data = _get_jama_project_items(project_id)
    item_types = _get_jama_item_types()
    jama_users = _get_jama_users()
    
    return [
        {
            "label": "Project Item",
            "type": "select",
            "name": "projectId",
            "option_groups": [
                prj_data
            ]
                  
        },
        {
            "label": "Item Type",
            "type": "select",
            "name": "itemType",
            "options": item_types
        },
        {
            "label": "New Item Name",
            "type": "text",
            "name": "newItemName",
        },
        {
            "label": "asignee",
            "type": "select",
            "name": "asignee",
            "options": jama_users
        },
        {
            "label": "Description",
            "type": "textarea",
            "name": "description"
        }

    ]


def _get_jama_project(project_id):
    """GETs project

    Args:
        project_id: id of the project the user wants to access
    """
    url = (os.environ['JAMA_URL'] + "/rest/latest/projects/{id}").format(id=project_id)
    resp = requests.get(url, auth=(os.environ["JAMA_USER"], os.environ["JAMA_PASS"]))

    # handled in create_req 
    assert(200 == resp.status_code)
    resp_json = json.loads(resp.text)

    return resp_json


def _get_jama_project_items(project_id):
    """GETs root items of a project

    Args:
        project_id: id of the project the user wants to access
    """
    # Gets all items
    url = os.environ['JAMA_URL']

    project = _get_jama_project(project_id)
    get_url = "{url}/rest/latest/items?project={id}&rootOnly=true".format(
            url=url, id=project["data"]["id"]
        )

    items_resp = requests.get(get_url, auth=(os.environ["JAMA_USER"], os.environ["JAMA_PASS"]))
    
    assert(200 == items_resp.status_code)
    project_items = json.loads(items_resp.text)

    return {
    "label": project["data"]["fields"]["name"],
    "options": [{
            "label": item["fields"]["name"],
            # value is "child.parent", similar to jwt
            "value": "{item_id}.{project_id}".format(
                item_id=item["id"], project_id=item["project"]
                ) 
            }
            for item in project_items["data"]
        ]
    }

def _get_jama_item_types():
    """GETs item types defined in a Jama instance

    Args:
        None

    Returns: 
        Array: objects of users data in the Jama instance
    """
    url = os.environ['JAMA_URL'] + "/rest/latest/itemtypes"
    resp = requests.get(url, auth=(os.environ["JAMA_USER"], os.environ["JAMA_PASS"]))
    
    assert(200 == resp.status_code)
    resp_json = json.loads(resp.text)
    
    # Returns an array of objects
    return [{
            "label": item["display"], 
            "value": item["id"] 
        } 
        for item in resp_json["data"] 
    ]


def _get_jama_users():
    """GETs
    Args:
        none

    Returns: 
        Array: Object with data of current users in the Jama instance
    """
    url = os.environ['JAMA_URL'] + "/rest/latest/users"
    resp = requests.get(url, auth=(os.environ["JAMA_USER"], os.environ["JAMA_PASS"]))
    
    assert(200 == resp.status_code)
    resp_json = json.loads(resp.text)

    return [{
            "label": item["username"],
            "value": item["id"]
        } for item in resp_json["data"]
    ]