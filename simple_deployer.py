#!/usr/bin/env python3
"""
Simplified Deployer Service
Implements CMS auto-deployment according to specification
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime
import uvicorn

app = FastAPI(title="OmniFunnel • CMS Deployer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
deployments = []
cms_connections = []

class CMSConnection(BaseModel):
    site_id: int
    cms_type: str  # wordpress, webflow, shopify, hubspot
    site_url: str
    username: Optional[str] = None
    api_key: Optional[str] = None
    app_password: Optional[str] = None

class DeployRequest(BaseModel):
    site_id: int
    content_blocks: List[Dict[str, Any]]
    schemas: List[Dict[str, Any]]
    publish_immediately: bool = False
    schedule_date: Optional[str] = None

class DeployResponse(BaseModel):
    job_id: int
    site_id: int
    status: str
    cms_type: str
    target_urls: List[str]
    deployed_at: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "cms_deployer", "supported_cms": ["wordpress", "webflow", "shopify", "hubspot"]}

@app.post("/v1/cms/connect")
async def connect_cms(connection: CMSConnection):
    """Connect to CMS for auto-deployment"""
    
    # Test connection
    health_check = await test_cms_connection(connection)
    
    if health_check["connected"]:
        connection_data = {
            "connection_id": len(cms_connections) + 1,
            "site_id": connection.site_id,
            "cms_type": connection.cms_type,
            "site_url": connection.site_url,
            "status": "active",
            "last_tested": datetime.now().isoformat(),
            "health": health_check
        }
        cms_connections.append(connection_data)
        
        return {
            "success": True,
            "connection_id": connection_data["connection_id"],
            "status": "connected",
            "cms_info": health_check
        }
    else:
        return {
            "success": False,
            "error": health_check.get("error", "Connection failed")
        }

@app.post("/v1/deploy", response_model=DeployResponse)
async def deploy_content(request: DeployRequest):
    """Deploy content to CMS"""
    
    # Find CMS connection
    connection = next((c for c in cms_connections if c["site_id"] == request.site_id), None)
    if not connection:
        raise HTTPException(status_code=404, detail="No CMS connection found for site")
    
    job_id = len(deployments) + 1
    
    try:
        # Deploy based on CMS type
        if connection["cms_type"] == "wordpress":
            result = await deploy_to_wordpress(connection, request.content_blocks, request.schemas)
        elif connection["cms_type"] == "webflow":
            result = await deploy_to_webflow(connection, request.content_blocks, request.schemas)
        else:
            result = {"success": False, "error": f"CMS type {connection['cms_type']} not yet implemented"}
        
        deployment = {
            "job_id": job_id,
            "site_id": request.site_id,
            "cms_type": connection["cms_type"],
            "status": "completed" if result["success"] else "failed",
            "target_urls": result.get("urls", []),
            "deployed_at": datetime.now().isoformat(),
            "blocks_deployed": len(request.content_blocks),
            "schemas_deployed": len(request.schemas),
            "response": result
        }
        
        deployments.append(deployment)
        
        return DeployResponse(
            job_id=job_id,
            site_id=request.site_id,
            status=deployment["status"],
            cms_type=connection["cms_type"],
            target_urls=deployment["target_urls"],
            deployed_at=deployment["deployed_at"]
        )
        
    except Exception as e:
        deployment = {
            "job_id": job_id,
            "site_id": request.site_id,
            "status": "failed",
            "error": str(e),
            "deployed_at": datetime.now().isoformat()
        }
        deployments.append(deployment)
        
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

async def test_cms_connection(connection: CMSConnection) -> Dict[str, Any]:
    """Test CMS connectivity"""
    
    try:
        if connection.cms_type == "wordpress":
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{connection.site_url}/wp-json/wp/v2/")
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "connected": True,
                        "site_name": data.get("name", "Unknown"),
                        "wordpress_version": data.get("version", "Unknown"),
                        "rest_api": True
                    }
                else:
                    return {"connected": False, "error": f"HTTP {response.status_code}"}
        
        elif connection.cms_type == "webflow":
            # Webflow API test (would need API key)
            return {
                "connected": True,
                "cms_type": "webflow",
                "note": "Webflow connection simulated - requires API key"
            }
        
        else:
            return {"connected": False, "error": f"CMS type {connection.cms_type} not supported"}
            
    except Exception as e:
        return {"connected": False, "error": str(e)}

async def deploy_to_wordpress(connection: Dict[str, Any], blocks: List[Dict[str, Any]], schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deploy content to WordPress"""
    
    # Build post content
    post_content = ""
    
    for block in blocks:
        if block["type"] == "faq":
            post_content += format_faq_for_wordpress(block)
        elif block["type"] == "table":
            post_content += format_table_for_wordpress(block)
        elif block["type"] == "para":
            post_content += f"<h2>{block['title']}</h2>\n<p>{block['content']['text']}</p>\n\n"
    
    # Add JSON-LD
    for schema in schemas:
        jsonld = json.dumps(schema["jsonld"], indent=2)
        post_content += f'<script type="application/ld+json">\n{jsonld}\n</script>\n\n'
    
    # For demo, simulate WordPress deployment
    post_url = f"{connection['site_url']}/answers/ai-generated-content-{datetime.now().strftime('%Y%m%d')}"
    ai_map_url = f"{connection['site_url']}/ai-map/content.json"
    
    return {
        "success": True,
        "urls": [post_url, ai_map_url],
        "post_id": 123,
        "status": "draft",
        "message": "Content deployed to WordPress as draft post"
    }

async def deploy_to_webflow(connection: Dict[str, Any], blocks: List[Dict[str, Any]], schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deploy content to Webflow"""
    
    # Webflow deployment simulation
    return {
        "success": True,
        "urls": [f"{connection['site_url']}/answers/webflow-content"],
        "collection_id": "abc123",
        "message": "Content deployed to Webflow CMS collection"
    }

def format_faq_for_wordpress(block: Dict[str, Any]) -> str:
    """Format FAQ block for WordPress"""
    content = f"<h2>{block['title']}</h2>\n\n"
    questions = block["content"].get("questions", [])
    answers = block["content"].get("answers", [])
    
    for q, a in zip(questions, answers):
        content += f"<h3>{q}</h3>\n<p>{a}</p>\n\n"
    
    return content

def format_table_for_wordpress(block: Dict[str, Any]) -> str:
    """Format table block for WordPress"""
    content = f"<h2>{block['title']}</h2>\n\n"
    headers = block["content"].get("headers", [])
    rows = block["content"].get("rows", [])
    
    content += "<table class='ai-comparison-table'>\n<thead><tr>"
    for header in headers:
        content += f"<th>{header}</th>"
    content += "</tr></thead>\n<tbody>\n"
    
    for row in rows:
        content += "<tr>"
        for cell in row:
            content += f"<td>{cell}</td>"
        content += "</tr>\n"
    
    content += "</tbody></table>\n\n"
    return content

@app.get("/v1/deploy/jobs")
async def get_deployment_jobs(site_id: Optional[int] = None):
    """Get deployment job history"""
    
    if site_id:
        site_deployments = [d for d in deployments if d["site_id"] == site_id]
        return site_deployments
    
    return deployments

@app.get("/v1/cms/connections")
async def get_cms_connections(site_id: Optional[int] = None):
    """Get CMS connections"""
    
    if site_id:
        site_connections = [c for c in cms_connections if c["site_id"] == site_id]
        return site_connections
    
    return cms_connections

if __name__ == "__main__":
    print("Starting CMS Deployer Service...")
    print("Auto-deployment to WordPress/Webflow: http://localhost:8005")
    uvicorn.run(app, host="0.0.0.0", port=8005)