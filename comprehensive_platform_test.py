#!/usr/bin/env python3
"""
Comprehensive OmniFunnel Platform Testing Script
Tests all services and demonstrates complete specification compliance
"""

import asyncio
import httpx
import json
from typing import Dict, Any

async def comprehensive_platform_test():
    """Test the complete OmniFunnel AI Visibility Platform"""
    
    print("COMPREHENSIVE OMNIFUNNEL PLATFORM TEST")
    print("=" * 60)
    print("Testing complete specification compliance...")
    print()
    
    results = {
        "services_tested": 0,
        "features_working": 0,
        "api_calls_successful": 0,
        "real_ai_responses": 0,
        "errors": []
    }
    
    # Test all service health
    print("TESTING SERVICE HEALTH")
    print("-" * 30)
    
    services = [
        ("Tracker", 8001, "/health"),
        ("Generator", 8002, "/health"), 
        ("Analytics", 8003, "/health"),
        ("Score", 8004, "/health"),
        ("Deployer", 8005, "/health"),
        ("GEO", 8006, "/health")
    ]
    
    async with httpx.AsyncClient() as client:
        for name, port, path in services:
            try:
                response = await client.get(f"http://localhost:{port}{path}", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {name:12} - {data.get('status', 'ok'):10} - Port {port}")
                    results["services_tested"] += 1
                else:
                    print(f"❌ {name:12} - HTTP {response.status_code:3} - Port {port}")
                    results["errors"].append(f"{name} service error: {response.status_code}")
            except Exception as e:
                print(f"❌ {name:12} - ERROR: {str(e)[:30]}...")
                results["errors"].append(f"{name} service unreachable: {str(e)}")
    
    print()
    
    # Test complete workflow
    print("🔄 TESTING COMPLETE WORKFLOW")
    print("-" * 30)
    
    try:
        # 1. Create Site
        print("1. Creating test site...")
        site_response = await client.post(
            "http://localhost:8001/v1/sites",
            json={
                "domain": "comprehensive-test.com",
                "cms_type": "wordpress",
                "tenant_id": 1
            }
        )
        
        if site_response.status_code == 200:
            site = site_response.json()
            print(f"   ✅ Site created: {site['domain']} (ID: {site['site_id']})")
            results["api_calls_successful"] += 1
            
            # 2. Create Cluster
            print("2. Creating test cluster...")
            cluster_response = await client.post(
                f"http://localhost:8001/v1/sites/{site['site_id']}/clusters",
                json={
                    "name": "Comprehensive Test Cluster",
                    "description": "Testing all platform features",
                    "seed_prompt": "comprehensive AI SEO platform with real-time tracking",
                    "keywords": ["ai", "seo", "platform", "tracking"]
                }
            )
            
            if cluster_response.status_code == 200:
                cluster = cluster_response.json()
                print(f"   ✅ Cluster created: {cluster['name']} (ID: {cluster['cluster_id']})")
                results["api_calls_successful"] += 1
                
                # 3. Test Real AI Tracking (all 3 engines)
                print("3. Testing REAL AI engine integrations...")
                
                for engine in ["chatgpt", "claude", "gemini"]:
                    print(f"   Testing {engine.upper()}...")
                    
                    track_response = await client.post(
                        f"http://localhost:8001/v1/clusters/{cluster['cluster_id']}/run",
                        json={
                            "engine": engine,
                            "variant_sample": 1
                        }
                    )
                    
                    if track_response.status_code == 200:
                        run_data = track_response.json()
                        print(f"   ✅ {engine.upper()} tracking initiated (Run ID: {run_data['run_id']})")
                        results["api_calls_successful"] += 1
                        
                        # Wait for processing
                        await asyncio.sleep(2)
                        
                        # Check answers
                        answers_response = await client.get(
                            f"http://localhost:8001/v1/clusters/{cluster['cluster_id']}/answers?engine={engine}"
                        )
                        
                        if answers_response.status_code == 200:
                            answers = answers_response.json()
                            if answers:
                                answer = answers[0]
                                print(f"   📝 Response length: {len(answer['raw_text'])} chars")
                                print(f"   🔗 Citations found: {len(answer['citations'])}")
                                print(f"   📊 Confidence: {answer.get('confidence', 0):.2f}")
                                results["real_ai_responses"] += 1
                                
                                if answer['citations']:
                                    print(f"   🎯 Sample citation: {answer['citations'][0][:50]}...")
                    else:
                        print(f"   ❌ {engine.upper()} tracking failed: {track_response.status_code}")
                
                # 4. Test Content Generation
                print("4. Testing content generation...")
                
                content_response = await client.post(
                    "http://localhost:8002/v1/content/generate",
                    json={
                        "topic": "AI-powered SEO automation platform",
                        "site_id": site['site_id'],
                        "formats": ["faq", "table", "para", "jsonld"]
                    }
                )
                
                if content_response.status_code == 200:
                    content = content_response.json()
                    print(f"   ✅ Content generated: {len(content['blocks'])} blocks, {len(content['schemas'])} schemas")
                    print(f"   📝 Total words: {content['total_word_count']}")
                    print(f"   🏆 Evaluator score: {content.get('evaluator_score', 0):.1f}")
                    results["features_working"] += 1
                else:
                    print(f"   ❌ Content generation failed: {content_response.status_code}")
                
                # 5. Test AI Visibility Score
                print("5. Testing AI Visibility Score™...")
                
                score_response = await client.post(
                    "http://localhost:8004/v1/calculate-score",
                    json={
                        "site_id": site['site_id'],
                        "cluster_id": cluster['cluster_id'],
                        "date_range_days": 30
                    }
                )
                
                if score_response.status_code == 200:
                    score = score_response.json()
                    print(f"   🏆 AI Visibility Score: {score['total']:.1f}/100")
                    print(f"   📊 Components: {len(score['subscores'])} metrics")
                    print(f"   💡 Recommendations: {len(score['recommendations'])}")
                    print(f"   🎯 Top component: {max(score['subscores'].items(), key=lambda x: x[1])}")
                    results["features_working"] += 1
                else:
                    print(f"   ❌ Score calculation failed: {score_response.status_code}")
                
                # 6. Test Competitive Analysis
                print("6. Testing competitive intelligence...")
                
                competitive_response = await client.post(
                    "http://localhost:8003/v1/competitive/analyze",
                    json={
                        "site_id": site['site_id'],
                        "cluster_id": cluster['cluster_id'],
                        "competitors": ["semrush.com", "ahrefs.com", "brightedge.com"],
                        "time_range_days": 30
                    }
                )
                
                if competitive_response.status_code == 200:
                    competitive = competitive_response.json()
                    print(f"   🧠 Competitive analysis complete: {len(competitive['competitors'])} competitors")
                    print(f"   🎯 Top competitor: {max(competitive['competitors'].items(), key=lambda x: x[1]['presence_score'])}")
                    print(f"   💡 Recommendations: {len(competitive['recommendation'])}")
                    results["features_working"] += 1
                else:
                    print(f"   ❌ Competitive analysis failed: {competitive_response.status_code}")
                
                # 7. Test CMS Deployment
                print("7. Testing CMS deployment...")
                
                deploy_response = await client.post(
                    "http://localhost:8005/v1/deploy",
                    json={
                        "site_id": site['site_id'],
                        "content_blocks": content['blocks'] if 'content' in locals() else [],
                        "schemas": content['schemas'] if 'content' in locals() else [],
                        "publish_immediately": False
                    }
                )
                
                if deploy_response.status_code == 200:
                    deployment = deploy_response.json()
                    print(f"   🚀 Deployment successful: Job ID {deployment['job_id']}")
                    print(f"   🌐 Target URLs: {len(deployment['target_urls'])}")
                    print(f"   📄 Status: {deployment['status']}")
                    results["features_working"] += 1
                else:
                    print(f"   ❌ Deployment failed: {deploy_response.status_code}")
                
            else:
                print(f"❌ Cluster creation failed: {cluster_response.status_code}")
        else:
            print(f"❌ Site creation failed: {site_response.status_code}")
    
    except Exception as e:
        print(f"❌ Workflow test error: {str(e)}")
        results["errors"].append(f"Workflow error: {str(e)}")
    
    # Final Results
    print()
    print("📋 COMPREHENSIVE TEST RESULTS")
    print("=" * 40)
    print(f"Services tested:        {results['services_tested']}/6")
    print(f"Features working:       {results['features_working']}")
    print(f"API calls successful:   {results['api_calls_successful']}")
    print(f"Real AI responses:      {results['real_ai_responses']}")
    print(f"Errors encountered:     {len(results['errors'])}")
    
    if results["errors"]:
        print("\n🚨 ERRORS:")
        for error in results["errors"]:
            print(f"   • {error}")
    
    # Calculate completion percentage
    total_possible = 20  # Estimated total features to test
    completion = (results["services_tested"] + results["features_working"] + results["real_ai_responses"]) / total_possible * 100
    
    print()
    print(f"🎯 PLATFORM COMPLETION: {completion:.1f}%")
    
    if completion >= 80:
        print("🎉 PLATFORM IS HIGHLY FUNCTIONAL!")
    elif completion >= 60:
        print("✅ PLATFORM CORE IS WORKING - NEEDS POLISH")
    else:
        print("⚠️ PLATFORM NEEDS SIGNIFICANT WORK")
    
    print()
    print("🌐 FRONTEND ACCESS:")
    print("   Main Dashboard: http://localhost:3000")
    print("   Master Control: http://localhost:3000/master-dashboard")
    print("   LEO Content:    http://localhost:3000/optimization")
    print("   Intelligence:   http://localhost:3000/intelligence")
    print("   AI Score™:      http://localhost:3000/scores")

if __name__ == "__main__":
    asyncio.run(comprehensive_platform_test())