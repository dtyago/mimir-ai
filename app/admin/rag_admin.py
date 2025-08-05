#!/usr/bin/env python3
"""
Admin endpoints for Enhanced RAG System management
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils.enhanced_rag import (
    get_enhanced_rag_system, 
    add_pdf_to_common_knowledge,
    add_business_data_to_mart,
    add_role_specific_content,
    DataSourceType
)
from langchain.schema import Document

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/admin/templates")

@router.get("/admin/rag_management", response_class=HTMLResponse)
async def rag_management_page(request: Request):
    """RAG system management page"""
    try:
        rag_system = await get_enhanced_rag_system()
        
        # Get status of different collections
        collection_stats = {
            "common_knowledge": await _get_collection_stats(rag_system.common_knowledge_db),
            "data_mart": await _get_collection_stats(rag_system.data_mart_db),
            "role_collections": {}
        }
        
        for role, collection in rag_system.role_collections.items():
            collection_stats["role_collections"][role] = await _get_collection_stats(collection)
        
        return templates.TemplateResponse("rag_management.html", {
            "request": request,
            "collection_stats": collection_stats,
            "available_roles": list(rag_system.role_collections.keys()),
            "data_sources": [ds.value for ds in DataSourceType]
        })
        
    except Exception as e:
        logger.error(f"Error in RAG management page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _get_collection_stats(collection) -> Dict[str, Any]:
    """Get statistics for a ChromaDB collection"""
    try:
        count = collection._collection.count()
        return {
            "document_count": count,
            "status": "active" if count > 0 else "empty"
        }
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        return {"document_count": 0, "status": "error"}

@router.post("/admin/rag/upload_knowledge")
async def upload_knowledge_base(
    file: UploadFile = File(...),
    source_name: str = Form(...),
    target_collection: str = Form("common_knowledge")
):
    """Upload documents to knowledge base"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        upload_dir = "/workspaces/mimir-api/data/tmp"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process based on target collection
        if target_collection == "common_knowledge":
            await add_pdf_to_common_knowledge(file_path, source_name)
        elif target_collection.startswith("role_"):
            role = target_collection.replace("role_", "").replace("_", "-")
            # Load PDF and add to role-specific collection
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            await add_role_specific_content(role, "\n".join([doc.page_content for doc in documents]))
        
        # Clean up temporary file
        os.remove(file_path)
        
        return {
            "message": f"Successfully uploaded {file.filename} to {target_collection}",
            "source_name": source_name,
            "file_name": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/rag/add_business_data")
async def add_business_data(
    data_type: str = Form(...),
    data_content: str = Form(...),
    format_type: str = Form("json")
):
    """Add business data to data mart"""
    try:
        if format_type == "json":
            business_data = json.loads(data_content)
        else:
            # Treat as plain text and structure it
            business_data = {
                "content": data_content,
                "added_at": "manual_entry"
            }
        
        await add_business_data_to_mart(business_data, data_type)
        
        return {
            "message": f"Successfully added business data of type {data_type}",
            "data_type": data_type
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error adding business data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/rag/populate_sample_data")
async def populate_sample_data():
    """Populate system with sample data for testing"""
    try:
        rag_system = await get_enhanced_rag_system()
        
        # Add sample business data directly
        analyst_gaming_data = {
            "revenue_metrics": {
                "gaming_revenue": 15000000.0,
                "average_revenue_per_paying_user": 125.0,
                "conversion_to_premium": 0.08,
                "in_game_purchases_rate": 0.25
            },
            "user_engagement": {
                "daily_active_players": 750000,
                "average_session_duration": 45.2,
                "games_per_session": 3.8,
                "completion_rate": 0.67
            },
            "performance_kpis": {
                "player_retention_rate": 0.82,
                "tournament_participation": 0.43,
                "social_features_usage": 0.52
            }
        }
        await rag_system.add_to_data_mart(analyst_gaming_data, "business_metrics")
        
        analyst_non_gaming_data = {
            "user_demographics": {
                "age_distribution": {"18-25": 0.25, "26-35": 0.40, "36-45": 0.20, "46+": 0.15},
                "geographic_distribution": {"NA": 0.45, "EU": 0.30, "APAC": 0.20, "Other": 0.05},
                "device_usage": {"mobile": 0.65, "desktop": 0.30, "tablet": 0.05}
            },
            "behavior_patterns": [
                "Peak usage hours: 7-9 PM",
                "Weekend engagement 30% higher than weekdays",
                "Mobile users have shorter but more frequent sessions"
            ]
        }
        await rag_system.add_to_data_mart(analyst_non_gaming_data, "user_analytics")
        
        leadership_gaming_data = {
            "strategic_overview": {
                "total_gaming_revenue": 15000000,
                "market_share": 0.15,
                "year_over_year_growth": 0.28,
                "profit_margin": 0.22
            },
            "game_catalog": {
                "total_games": 1250,
                "active_games": 890,
                "new_releases_this_month": 15,
                "top_categories": ["Strategy", "Action", "Puzzle", "RPG"]
            }
        }
        await rag_system.add_to_data_mart(leadership_gaming_data, "gaming_data")
        
        # Add sample role-specific content
        role_contents = {
            "Analyst-Gaming": """
            Gaming Analytics Best Practices:
            1. Track player engagement metrics including session duration, retention rates, and in-game purchases
            2. Analyze player behavior patterns to identify opportunities for game improvement
            3. Monitor competitive landscape and market trends
            4. Use cohort analysis to understand player lifecycle
            5. Implement A/B testing for game features and monetization strategies
            """,
            "Analyst-Non-Gaming": """
            General Analytics Guidelines:
            1. Focus on user acquisition cost and lifetime value metrics
            2. Analyze conversion funnels and identify optimization opportunities
            3. Track customer satisfaction and Net Promoter Score
            4. Monitor market trends and competitive positioning
            5. Use predictive analytics for forecasting and planning
            """,
            "Leadership-Gaming": """
            Gaming Strategy Leadership Framework:
            1. Define long-term vision for gaming portfolio
            2. Assess market opportunities and competitive threats
            3. Make strategic decisions on game development investments
            4. Build partnerships with gaming studios and publishers
            5. Oversee portfolio performance and resource allocation
            """,
            "Leadership-Non-Gaming": """
            Strategic Leadership Principles:
            1. Develop comprehensive business strategy and vision
            2. Lead organizational transformation initiatives
            3. Build strong stakeholder relationships
            4. Drive innovation and digital transformation
            5. Ensure sustainable growth and profitability
            """
        }
        
        for role, content in role_contents.items():
            await add_role_specific_content(role, content, {"source": "sample_data", "type": "guidelines"})
        
        # Add sample common knowledge
        common_knowledge_content = """
        Mimir AI Assistant User Guide:
        
        Mimir is an advanced AI assistant designed to help with business analysis, gaming insights, and strategic decision-making.
        
        Key Features:
        - Multi-source data integration
        - Role-based content filtering
        - Conversation history tracking
        - Real-time business metrics access
        
        Best Practices:
        1. Be specific in your questions to get more targeted responses
        2. Use role-specific terminology for better context understanding
        3. Reference previous conversations for continuity
        4. Ask for data visualization when dealing with metrics
        5. Request comparisons between different time periods or segments
        """
        
        doc = Document(
            page_content=common_knowledge_content,
            metadata={"source": "user_guide", "type": "documentation"}
        )
        
        await rag_system.add_to_common_knowledge([doc], "user_guide")
        
        return {
            "message": "Successfully populated system with sample data",
            "data_added": {
                "business_metrics": True,
                "user_analytics": True,
                "gaming_data": True,
                "role_specific_content": len(role_contents),
                "common_knowledge": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error populating sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/rag/collection_status")
async def get_collection_status():
    """Get status of all RAG collections"""
    try:
        rag_system = await get_enhanced_rag_system()
        
        status = {
            "common_knowledge": await _get_collection_stats(rag_system.common_knowledge_db),
            "data_mart": await _get_collection_stats(rag_system.data_mart_db),
            "role_collections": {}
        }
        
        for role, collection in rag_system.role_collections.items():
            status["role_collections"][role] = await _get_collection_stats(collection)
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting collection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/rag/clear_collection")
async def clear_collection(collection_name: str = Form(...)):
    """Clear a specific collection"""
    try:
        rag_system = await get_enhanced_rag_system()
        
        if collection_name == "common_knowledge":
            # Clear common knowledge
            rag_system.common_knowledge_db.delete_collection()
            rag_system.common_knowledge_db = rag_system._init_collections()
        elif collection_name == "data_mart":
            # Clear data mart
            rag_system.data_mart_db.delete_collection()
        elif collection_name in rag_system.role_collections:
            # Clear role-specific collection
            rag_system.role_collections[collection_name].delete_collection()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown collection: {collection_name}")
        
        return {
            "message": f"Successfully cleared collection: {collection_name}",
            "collection": collection_name
        }
        
    except Exception as e:
        logger.error(f"Error clearing collection {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
