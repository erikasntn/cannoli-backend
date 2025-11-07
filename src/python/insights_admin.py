import json
from service.admin_insights_service import generate_admin_dashboard

if __name__ == "__main__":
    result = generate_admin_dashboard("30d")
    print(json.dumps(result, ensure_ascii=False, indent=2))
