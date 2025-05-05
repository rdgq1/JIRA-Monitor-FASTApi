# main.py
import uvicorn
from api import jira_endpoints

if __name__ == "__main__":
    uvicorn.run(jira_endpoints.app, host="0.0.0.0", port=8000, reload=True)
