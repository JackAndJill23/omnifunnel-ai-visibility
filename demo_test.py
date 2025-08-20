#!/usr/bin/env python3
"""
OmniFunnel AI Visibility Platform - Standalone Demo
This script demonstrates our core functionality without Docker
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Demo imports
from backend.services.tracker.engines import engine_manager, EngineManager
from backend.services.tracker.prompt_variants import generate_prompt_variants
from backend.services.score.main import AIVisibilityScoreCalculator
import asyncio
import json

async def demo_prompt_variants():
    """Demo: Generate prompt variants"""
    print("🎯 DEMO: Prompt Variant Generation")
    print("=" * 50)
    
    seed_prompt = "best AI SEO tools"
    variants = generate_prompt_variants(seed_prompt, count=10)
    
    print(f"Seed prompt: '{seed_prompt}'")
    print(f"Generated {len(variants)} variants:")
    print()
    
    for i, variant in enumerate(variants[:10], 1):
        print(f"{i:2d}. {variant.text}")
        print(f"    Type: {variant.variant_type.value}, Confidence: {variant.confidence:.2f}")
    
    print("\n" + "=" * 50)
    return variants

async def demo_ai_engines():
    """Demo: AI Engine Responses"""
    print("🤖 DEMO: AI Engine Integration")
    print("=" * 50)
    
    # Test with a simple prompt
    test_prompt = "What are the top AI SEO platforms in 2024?"
    
    print(f"Testing prompt: '{test_prompt}'")
    print()
    
    # Test each engine
    for engine_name in engine_manager.list_engines():
        try:
            print(f"Testing {engine_name.upper()}...")
            answer = await engine_manager.query_engine(engine_name, test_prompt)
            
            print(f"✅ {engine_name}: Response length: {len(answer.raw_text)} chars")
            print(f"   Citations found: {len(answer.citations)}")
            print(f"   Confidence: {answer.confidence}")
            print(f"   Sample: {answer.raw_text[:100]}...")
            
            if answer.citations:
                print(f"   Top citation: {answer.citations[0]}")
            print()
            
        except Exception as e:
            print(f"❌ {engine_name}: {str(e)}")
            print()
    
    print("=" * 50)

def demo_score_calculation():
    """Demo: AI Visibility Score calculation logic"""
    print("🏆 DEMO: AI Visibility Score™ Calculation")
    print("=" * 50)
    
    # Mock data for demonstration
    mock_subscores = {
        'prompt_sov': 65.0,           # 30% weight
        'generative_appearance': 78.0, # 20% weight  
        'citation_authority': 82.0,   # 15% weight
        'answer_quality': 71.0,       # 10% weight
        'voice_presence': 25.0,       # 5% weight
        'ai_traffic': 45.0,           # 10% weight
        'ai_conversions': 38.0        # 10% weight
    }
    
    weights = {
        'prompt_sov': 0.30,
        'generative_appearance': 0.20,
        'citation_authority': 0.15,
        'answer_quality': 0.10,
        'voice_presence': 0.05,
        'ai_traffic': 0.10,
        'ai_conversions': 0.10
    }
    
    print("Score Components:")
    print("-" * 30)
    total_score = 0
    
    for component, score in mock_subscores.items():
        weight = weights[component]
        weighted_score = score * weight
        total_score += weighted_score
        
        print(f"{component.replace('_', ' ').title():25s}: {score:5.1f} × {weight:.0%} = {weighted_score:5.2f}")
    
    print("-" * 30)
    print(f"{'TOTAL AI VISIBILITY SCORE':25s}: {total_score:5.1f}/100")
    
    # Grade calculation
    if total_score >= 90:
        grade = "A+"
    elif total_score >= 80:
        grade = "A"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 60:
        grade = "C"
    else:
        grade = "D"
    
    print(f"{'GRADE':25s}: {grade}")
    
    # Recommendations
    print("\nRecommendations:")
    if mock_subscores['prompt_sov'] < 70:
        print("• Optimize content for better AI query presence")
    if mock_subscores['citation_authority'] < 70:
        print("• Target higher-authority publication mentions")
    if mock_subscores['ai_traffic'] < 50:
        print("• Implement AI source attribution tracking")
    
    print("\n" + "=" * 50)

def demo_project_structure():
    """Demo: Show what we've built"""
    print("📁 DEMO: Complete Project Structure")
    print("=" * 50)
    
    structure = {
        "Backend Microservices (8 services)": [
            "🎯 Tracker - LLM citation tracking across 5 AI engines",
            "🏆 Score - AI Visibility Score™ calculation engine", 
            "📊 Analytics - Data processing and insights",
            "🚀 Deployer - CMS auto-deployment system",
            "📡 Telemetry - Bot tracking and analytics",
            "⚙️ Generator - Content creation pipelines",
            "🔐 AuthZ - Authentication and authorization",
            "💳 Billing - Stripe subscription management"
        ],
        "Frontend Application": [
            "🏠 Home Dashboard - Service monitoring and quick actions",
            "🎯 Tracking Interface - Site and cluster management", 
            "📊 Results Dashboard - Answer and citation analysis",
            "🏆 AI Score™ Interface - Proprietary scoring system"
        ],
        "Database & Infrastructure": [
            "🗄️ PostgreSQL with pgvector - Comprehensive schemas",
            "🔴 Redis - Caching and task queues",
            "🐳 Docker - Complete containerization",
            "🔧 Configuration - Environment management"
        ],
        "AI Engine Integration": [
            "🤖 ChatGPT - With API key configured",
            "🧠 Claude - With API key configured", 
            "💎 Gemini - With API key configured",
            "🔍 Perplexity - Ready for implementation",
            "🌐 Bing Copilot - Ready for implementation"
        ]
    }
    
    for category, items in structure.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  {item}")
    
    print("\n" + "=" * 50)

async def main():
    """Run all demos"""
    print("🎉 OMNIFUNNEL AI VISIBILITY PLATFORM DEMO")
    print("=" * 60)
    print("This demonstrates the 70% complete production-ready platform")
    print("=" * 60)
    print()
    
    # Show project structure
    demo_project_structure()
    
    # Demo prompt variants
    await demo_prompt_variants()
    print()
    
    # Demo score calculation
    demo_score_calculation()
    print()
    
    # Demo AI engines (using mock responses)
    await demo_ai_engines()
    
    print("\n🌐 FRONTEND DEMO:")
    print("Visit http://localhost:3000 to see the complete dashboard!")
    print()
    print("🎯 WHAT YOU CAN TEST:")
    print("• Navigate between pages (Home, Tracking, Dashboard, Scores)")
    print("• See service status monitoring")  
    print("• View AI engine configurations")
    print("• Explore the UI workflow")
    print()
    print("🚀 READY FOR PRODUCTION COMPLETION!")

if __name__ == "__main__":
    asyncio.run(main())