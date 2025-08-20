#!/usr/bin/env python3
"""Simple platform status check"""

import asyncio
import httpx

async def check_platform_status():
    print("OMNIFUNNEL PLATFORM STATUS CHECK")
    print("=" * 40)
    
    services = [
        ("Tracker", 8001),
        ("Generator", 8002), 
        ("Analytics", 8003),
        ("Score", 8004),
        ("Deployer", 8005),
        ("GEO", 8006)
    ]
    
    async with httpx.AsyncClient() as client:
        for name, port in services:
            try:
                response = await client.get(f"http://localhost:{port}/health", timeout=3.0)
                if response.status_code == 200:
                    print(f"OK   {name:12} - Port {port}")
                else:
                    print(f"ERR  {name:12} - HTTP {response.status_code}")
            except:
                print(f"DOWN {name:12} - Port {port}")
    
    print()
    print("TESTING REAL AI INTEGRATION")
    print("-" * 25)
    
    # Test site creation
    try:
        site_response = await client.post(
            "http://localhost:8001/v1/sites",
            json={"domain": "status-test.com", "cms_type": "wordpress", "tenant_id": 1}
        )
        
        if site_response.status_code == 200:
            site = site_response.json()
            print(f"Site creation: WORKING (ID: {site['site_id']})")
            
            # Test cluster creation
            cluster_response = await client.post(
                f"http://localhost:8001/v1/sites/{site['site_id']}/clusters",
                json={
                    "name": "Status Test",
                    "seed_prompt": "AI SEO platform testing",
                    "keywords": ["test"]
                }
            )
            
            if cluster_response.status_code == 200:
                cluster = cluster_response.json()
                print(f"Cluster creation: WORKING (ID: {cluster['cluster_id']})")
                
                # Test real AI call
                track_response = await client.post(
                    f"http://localhost:8001/v1/clusters/{cluster['cluster_id']}/run",
                    json={"engine": "chatgpt", "variant_sample": 1}
                )
                
                if track_response.status_code == 200:
                    print("ChatGPT tracking: WORKING")
                    
                    # Check for real response
                    await asyncio.sleep(3)
                    answers_response = await client.get(
                        f"http://localhost:8001/v1/clusters/{cluster['cluster_id']}/answers"
                    )
                    
                    if answers_response.status_code == 200:
                        answers = answers_response.json()
                        if answers:
                            print(f"AI Response: {len(answers[0]['raw_text'])} chars")
                            print(f"Citations: {len(answers[0]['citations'])}")
                        else:
                            print("AI Response: No data yet")
                else:
                    print("ChatGPT tracking: FAILED")
            else:
                print("Cluster creation: FAILED")
        else:
            print("Site creation: FAILED")
    except Exception as e:
        print(f"Workflow test error: {str(e)}")
    
    print()
    print("FRONTEND URLS:")
    print("Main:        http://localhost:3000")
    print("Tracking:    http://localhost:3000/tracking")
    print("Master:      http://localhost:3000/master-dashboard")

if __name__ == "__main__":
    asyncio.run(check_platform_status())