"""
generate_openapi.py
HemaGrid AI - OpenAPI Spec Generator

Extracts the JSON OpenAPI schema definitions from the FastAPI application instance
and writes them directly to openapi.json.
"""

import json
import os
import sys

# Append root directory to sys path to resolve local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from api.main import app

def generate_spec():
    # Extract schema
    schema = app.openapi()
    
    # Save output to docs directory
    out_path = os.path.join(current_dir, "openapi.json")
    with open(out_path, "w") as f:
        json.dump(schema, f, indent=2)
        
    print(f"Successfully generated OpenAPI specification at: {out_path}")

if __name__ == "__main__":
    generate_spec()
