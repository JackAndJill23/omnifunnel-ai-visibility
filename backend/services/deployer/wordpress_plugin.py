"""
WordPress CMS Plugin Integration
Based on technical specification section 10 - Plugins & Auto-Deployment
"""

import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from base64 import b64encode

class WordPressCMSIntegration:
    """WordPress CMS integration for auto-deployment"""
    
    def __init__(self, site_url: str, username: str, app_password: str):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Setup authentication
        credentials = f"{username}:{app_password}"
        encoded_credentials = b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    async def create_answer_hub_post(self, content_blocks: List[Dict[str, Any]], schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create Answer Hub post with content blocks and JSON-LD"""
        
        # Build post content from blocks
        post_content = self._build_post_content(content_blocks)
        
        # Add JSON-LD to post
        jsonld_script = self._build_jsonld_script(schemas)
        post_content += f"\n\n{jsonld_script}"
        
        # Create WordPress post
        post_data = {
            "title": content_blocks[0]["title"] if content_blocks else "AI Optimized Content",
            "content": post_content,
            "status": "draft",  # Start as draft for review
            "categories": [self._get_or_create_category("AI Answers")],
            "meta": {
                "ai_optimized": True,
                "schema_count": len(schemas),
                "block_count": len(content_blocks),
                "generated_at": datetime.now().isoformat()
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.site_url}/wp-json/wp/v2/posts",
                headers=self.headers,
                json=post_data
            )
            
            if response.status_code == 201:
                post = response.json()
                
                # Create AI map endpoint
                await self._create_ai_map_endpoint(post["id"], schemas)
                
                return {
                    "success": True,
                    "post_id": post["id"],
                    "post_url": post["link"],
                    "ai_map_url": f"{self.site_url}/ai-map/{post['slug']}.json",
                    "status": "draft"
                }
            else:
                return {"success": False, "error": f"WordPress API error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    async def publish_post(self, post_id: int) -> Dict[str, Any]:
        """Publish a draft post"""
        
        try:
            response = await self.client.post(
                f"{self.site_url}/wp-json/wp/v2/posts/{post_id}",
                headers=self.headers,
                json={"status": "publish"}
            )
            
            if response.status_code == 200:
                return {"success": True, "status": "published"}
            else:
                return {"success": False, "error": f"Publish failed: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_ai_map_endpoint(self, post_id: int, schemas: List[Dict[str, Any]]) -> bool:
        """Create /ai-map/{slug}.json endpoint"""
        
        # This would typically be done via a custom WordPress plugin
        # For now, we'll store the mapping in post meta
        
        ai_map_data = {
            "post_id": post_id,
            "schemas": schemas,
            "generated_at": datetime.now().isoformat()
        }
        
        try:
            await self.client.post(
                f"{self.site_url}/wp-json/wp/v2/posts/{post_id}/meta",
                headers=self.headers,
                json={
                    "key": "ai_map_data",
                    "value": json.dumps(ai_map_data)
                }
            )
            return True
        except:
            return False
    
    def _build_post_content(self, blocks: List[Dict[str, Any]]) -> str:
        """Build WordPress post content from content blocks"""
        
        content_parts = []
        
        for block in blocks:
            if block["type"] == "faq":
                content_parts.append(self._format_faq_block(block))
            elif block["type"] == "table":
                content_parts.append(self._format_table_block(block))
            elif block["type"] == "para":
                content_parts.append(self._format_paragraph_block(block))
            elif block["type"] == "list":
                content_parts.append(self._format_list_block(block))
        
        return "\n\n".join(content_parts)
    
    def _format_faq_block(self, block: Dict[str, Any]) -> str:
        """Format FAQ block for WordPress"""
        
        content = f"<h2>{block['title']}</h2>\n\n"
        questions = block["content"].get("questions", [])
        answers = block["content"].get("answers", [])
        
        for q, a in zip(questions, answers):
            content += f"<h3>{q}</h3>\n<p>{a}</p>\n\n"
        
        return content
    
    def _format_table_block(self, block: Dict[str, Any]) -> str:
        """Format table block for WordPress"""
        
        content = f"<h2>{block['title']}</h2>\n\n"
        headers = block["content"].get("headers", [])
        rows = block["content"].get("rows", [])
        
        content += "<table class='ai-comparison-table'>\n"
        content += "<thead><tr>"
        for header in headers:
            content += f"<th>{header}</th>"
        content += "</tr></thead>\n<tbody>\n"
        
        for row in rows:
            content += "<tr>"
            for cell in row:
                content += f"<td>{cell}</td>"
            content += "</tr>\n"
        
        content += "</tbody></table>\n"
        return content
    
    def _format_paragraph_block(self, block: Dict[str, Any]) -> str:
        """Format paragraph block for WordPress"""
        return f"<h2>{block['title']}</h2>\n<p>{block['content']['text']}</p>"
    
    def _format_list_block(self, block: Dict[str, Any]) -> str:
        """Format list block for WordPress"""
        
        content = f"<h2>{block['title']}</h2>\n<ul>\n"
        for item in block["content"].get("items", []):
            content += f"<li>{item}</li>\n"
        content += "</ul>"
        return content
    
    def _build_jsonld_script(self, schemas: List[Dict[str, Any]]) -> str:
        """Build JSON-LD script tags"""
        
        scripts = []
        for schema in schemas:
            jsonld = json.dumps(schema["jsonld"], indent=2)
            scripts.append(f'<script type="application/ld+json">\n{jsonld}\n</script>')
        
        return "\n\n".join(scripts)
    
    async def _get_or_create_category(self, category_name: str) -> int:
        """Get or create WordPress category"""
        
        try:
            # Check if category exists
            response = await self.client.get(
                f"{self.site_url}/wp-json/wp/v2/categories",
                headers=self.headers,
                params={"search": category_name}
            )
            
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    return categories[0]["id"]
            
            # Create category if not found
            create_response = await self.client.post(
                f"{self.site_url}/wp-json/wp/v2/categories",
                headers=self.headers,
                json={"name": category_name}
            )
            
            if create_response.status_code == 201:
                return create_response.json()["id"]
                
        except Exception as e:
            print(f"Category creation error: {e}")
        
        return 1  # Default uncategorized

    async def get_site_health(self) -> Dict[str, Any]:
        """Check WordPress site health and connectivity"""
        
        try:
            # Test basic connectivity
            response = await self.client.get(f"{self.site_url}/wp-json/wp/v2/")
            
            if response.status_code == 200:
                site_info = response.json()
                
                # Test authentication
                auth_test = await self.client.get(
                    f"{self.site_url}/wp-json/wp/v2/users/me",
                    headers=self.headers
                )
                
                return {
                    "connected": True,
                    "site_name": site_info.get("name", "Unknown"),
                    "wordpress_version": site_info.get("version", "Unknown"),
                    "authenticated": auth_test.status_code == 200,
                    "rest_api": True,
                    "last_checked": datetime.now().isoformat()
                }
            else:
                return {
                    "connected": False,
                    "error": f"HTTP {response.status_code}",
                    "last_checked": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }

    async def list_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent posts for monitoring"""
        
        try:
            response = await self.client.get(
                f"{self.site_url}/wp-json/wp/v2/posts",
                headers=self.headers,
                params={
                    "per_page": limit,
                    "orderby": "date",
                    "order": "desc"
                }
            )
            
            if response.status_code == 200:
                posts = response.json()
                return [
                    {
                        "id": post["id"],
                        "title": post["title"]["rendered"],
                        "status": post["status"],
                        "date": post["date"],
                        "link": post["link"]
                    }
                    for post in posts
                ]
            else:
                return []
                
        except Exception:
            return []