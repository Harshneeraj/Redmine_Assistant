import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from langchain_core.tools import tool
from global_driver import driver


#  List project tools: list Redmine projects
@tool
def list_projects(state: dict) -> dict:
    """
    Lists available Redmine projects.

    **Arguments**:
    - `state (dict)`: The current agent state. No specific keys required.

    **Behavior**:
    - Retrieval of Redmine project names.
    - Prints the list of projects`.

    **Returns**:
    - `list`: Returns the list of projects.
    """
    print("📋 Listing projects in Redmine...")
    mock_projects = ["test-ortut", "empower-roadmap", "otkap"]
    print("✅ Projects retrieved:", mock_projects)
    return mock_projects

# Redmine tools: login to Redmine
@tool
def login_to_redmine(state:dict) -> dict:
    """
    Logs into Redmine using Selenium WebDriver.

    **Arguments**:
    - `state (dict)`: A dictionary representing the current agent state. No specific keys required.

    **Behavior**:
    - Launches a Chrome browser using Selenium.
    - Navigates to the Redmine login page.
    - Fills in hardcoded credentials for the user.
    - Clicks the login button and waits for the login to complete.
    - Updates the state with:
        - `'logged_in': True`
        - `'driver'`: Selenium WebDriver instance

    **Returns**:
    - `dict`: Updated state with driver and login status.
    """
    driver.get("http://svn.aps1aws.lumiq.int")  

    driver.find_element(By.ID, "username").send_keys("harsh.kumar")
    driver.find_element(By.ID, "password").send_keys("tdaik@57024")
    driver.find_element(By.NAME, "login").click()
    time.sleep(2) 
    
    state['logged_in'] = True
    return state

# Redmine tools: create an issue
@tool
def create_issue(state, project_id, subject, description, start_date, due_date='', estimated_hours='', priority='HIGH', assignee='me' , done_ratio=0) -> dict:
    """
    Automates Redmine issue creation using Selenium.

    **Arguments**:
    - `state (dict)`: Must contain `'driver'`, a logged-in Selenium WebDriver instance.
    - `project_id (str)`: The ID or slug of the Redmine project.
    - `subject (str)`: Short title or summary of the issue.
    - `description (str)`: Full description of the issue.
    - `start_date (str)`: Start date in 'YYYY-MM-DD' format.
    - `due_date (str, optional)`: Due date in 'YYYY-MM-DD' format.
    - `estimated_hours (str, optional)`: Estimated time to resolve the issue.
    - `priority (str, optional)`: Priority level (e.g., 'HIGH').
    - `assignee (str, optional)`: Assignee name or 'me' to assign to self.
    - `done_ratio (int, optional)`: Percentage completion (e.g., 0, 50, 100).

    **Behavior**:
    - Navigates to the new issue form.
    - Fills out all form fields using the provided values.
    - Selects appropriate values from dropdowns.
    - Clicks "Assign to me" if assignee is 'me'.
    - Submits the form.

    **Returns**:
    - `dict`: Unchanged state if issue creation is successful.

    **Requires**:
    - The user must be logged in (`state['driver']` must be available).
    """

    driver.get(f"http://svn.aps1aws.lumiq.int/projects/{project_id}/issues/new")
    
    issue_data = {
    "tracker": "Bug",
    "subject": f"{subject}",
    "description": F"{description}",
    "status": "New",
    "priority": f"{priority}",
    "assignee": f"{assignee}",  
    "category": "",  
    "parent_id": "", 
    "start_date": f"{start_date}",
    "due_date": f"{due_date}",  
    "estimated_hours": f"{estimated_hours}",
    "done_ratio": f"{done_ratio}"
    }

    Select(driver.find_element(By.ID, "issue_tracker_id")).select_by_visible_text(issue_data["tracker"])
    driver.find_element(By.ID, "issue_subject").send_keys(issue_data["subject"])
    driver.find_element(By.ID, "issue_description").send_keys(issue_data["description"])
    Select(driver.find_element(By.ID, "issue_status_id")).select_by_visible_text(issue_data["status"])
    Select(driver.find_element(By.ID, "issue_priority_id")).select_by_visible_text(issue_data["priority"])
    assign_to_me_btn = driver.find_element(By.LINK_TEXT, "Assign to me")
    assign_to_me_btn.click()
    if issue_data["category"]:
        Select(driver.find_element(By.ID, "issue_category_id")).select_by_visible_text(issue_data["category"])
    if issue_data["parent_id"]:
        driver.find_element(By.ID, "issue_parent_issue_id").send_keys(issue_data["parent_id"])
    driver.find_element(By.ID, "issue_start_date").clear()
    driver.find_element(By.ID, "issue_start_date").send_keys(issue_data["start_date"])
    if issue_data["due_date"]:
        driver.find_element(By.ID, "issue_due_date").send_keys(issue_data["due_date"])
    driver.find_element(By.ID, "issue_estimated_hours").send_keys(issue_data["estimated_hours"])
    Select(driver.find_element(By.ID, "issue_done_ratio")).select_by_visible_text(issue_data["done_ratio"] + " %")
    driver.find_element(By.NAME, "commit").click()
    time.sleep(2)
    return state

# Redmine tools: list issues
@tool
def list_issues(state) -> dict:
    """
    List all Redmine issues assigned to the logged-in user in a given project.

    **Arguments**:
    - `state (dict)`: Current state which must include a Selenium WebDriver under the key `'driver'`.
    - `project_id (str)`: The unique identifier of the Redmine project from which issues are to be listed.

    **Behavior**:
    - Navigates to the Redmine issue listing page for the specified project.
    - Filters issues assigned to the current user.
    - Parses issue data (ID and subject) from the page.
    - Presents the list of issues to the user with indexed options.`.

    **Returns**:
    - `list`: Returns list of issues.

    **Requires**:
    - User must be logged in and `driver` must be initialized and project must be selected.
    """
    
    project = state["project"]
    if not project:
        raise Exception("Project not selected. Please select a project first.")

    driver.get(f"http://svn.aps1aws.lumiq.int/projects/{project}/issues?utf8=%E2%9C%93&set_filter=1&sort=id%3Adesc&f%5B%5D=assigned_to_id&op%5Bassigned_to_id%5D=%3D&v%5Bassigned_to_id%5D%5B%5D=me&f%5B%5D=&c%5B%5D=tracker&c%5B%5D=status&c%5B%5D=priority&c%5B%5D=subject&c%5B%5D=assigned_to&c%5B%5D=updated_on&c%5B%5D=agile_sprint&c%5B%5D=total_estimated_hours&c%5B%5D=total_spent_hours&group_by=&t%5B%5D=estimated_hours&t%5B%5D=spent_hours&t%5B%5D=")
    time.sleep(2)

    issues = driver.find_elements(By.CSS_SELECTOR, "table.issues tbody tr")
    issue_map = {}

    print("Available issues:")
    for i, row in enumerate(issues, start=1):
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) >= 2:
            issue_id = columns[1].text.strip("#")
            subject = columns[5].text
            issue_map[issue_id] = f"{issue_id} - {subject}"
            print(f"{i}. [{issue_id}] {subject}")
    return issues

# Redmine tools: log time to selected issue
@tool
def log_time_to_selected_issue(state:dict) -> dict:
    """
    Logs time against the issue previously selected by the user in Redmine.

    **Arguments**:
    - `state (dict)`: Should contain:
        - `'driver'`: A Selenium WebDriver instance that is already authenticated.
        - `'selected_issue'`: The ID of the Redmine issue to which time should be logged.

    **Behavior**:
    - Navigates to the time logging form for the selected issue.
    - Fills in the time entry form with:
        - `Activity`: "Development"
        - `Hours`: 2.5 (hardcoded)
        - `Comments`: "Worked on bug fix and testing"
    - Submits the form.
    - Waits for the form submission to complete.
    - Updates the `state` with the key `'time_logged'` set to `True`.

    **Returns**:
    - `dict`: Updated state with `'time_logged': True` upon successful submission.

    **Requires**:
    - The user must be logged in.
    - A valid `selected_issue` must be present in the state.
    """
    selected_issue = state.get("selected_issue")
    if not selected_issue:
        raise Exception("No issue selected.")
    driver.get(f"http://svn.aps1aws.lumiq.int/issues/{selected_issue}/time_entries/new")
    time.sleep(2)
    time_entry_data = {
        "activity": "Development",
        "hours": "2.5",
        "comments": "Worked on bug fix and testing"
    }
    driver.find_element(By.ID, "time_entry_hours").send_keys(time_entry_data["hours"])
    driver.find_element(By.ID, "time_entry_comments").send_keys(time_entry_data["comments"])
    driver.find_element(By.NAME, "commit").click()  # Submit the form
    time.sleep(2)
    state["time_logged"] = True
    return state


tool_list = [log_time_to_selected_issue, list_issues,create_issue,login_to_redmine,list_projects]
