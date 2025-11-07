import os
import sys
import json

# garante path correto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from service.client_insights_service import generate_client_insights

if __name__ == "__main__":
    period = sys.argv[1] if len(sys.argv) > 1 else "30d"
    result = generate_client_insights(period)
    print(json.dumps(result, ensure_ascii=False, indent=2))
