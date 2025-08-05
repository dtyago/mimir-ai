from fastapi import APIRouter, Depends, HTTPException, Body
from ..dependencies import get_current_user
from ..utils.chat_rag import llm_infer
from ..utils.chat_rag import sanitize_collection_name
from ..utils.enhanced_rag import enhanced_chat_inference, DataSourceType, get_enhanced_rag_system
from typing import Any, List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/user/chat")
async def chat_with_llama(
    user_input: str = Body(..., embed=True), 
    use_enhanced_rag: bool = Body(True, embed=True),
    data_sources: Optional[List[str]] = Body(None, embed=True),
    current_user: Any = Depends(get_current_user)
):
    """
    Enhanced chat endpoint with multi-source RAG capabilities
    """
    try:
        user_id = current_user["user_id"]
        role = current_user["role"]
        name = current_user["name"]
        
        if use_enhanced_rag:
            # Use enhanced RAG system with multiple data sources
            logger.info(f"Using enhanced RAG for user {user_id} with role {role}")
            
            # Determine data sources based on role if not specified
            if data_sources is None:
                # Default data sources based on role
                default_sources = [
                    DataSourceType.USER_DOCUMENTS,
                    DataSourceType.COMMON_KNOWLEDGE,
                    DataSourceType.CONVERSATION_HISTORY
                ]
                
                # Add role-specific sources
                if "Analyst" in role:
                    default_sources.extend([
                        DataSourceType.DATA_MART,
                        DataSourceType.ROLE_SPECIFIC
                    ])
                elif "Leadership" in role:
                    default_sources.extend([
                        DataSourceType.DATA_MART,
                        DataSourceType.ROLE_SPECIFIC
                    ])
                
                # Auto-populate data mart with relevant data
                await _populate_data_mart_for_role(role)
                
            else:
                # Convert string data sources to enum
                default_sources = []
                for source in data_sources:
                    try:
                        default_sources.append(DataSourceType(source))
                    except ValueError:
                        logger.warning(f"Invalid data source: {source}")
            
            # Use enhanced RAG inference
            model_response = await enhanced_chat_inference(
                user_id=user_id,
                role=role,
                query=user_input,
                data_sources=default_sources
            )
            
        else:
            # Use traditional RAG system
            logger.info(f"Using traditional RAG for user {user_id}")
            model_response = await llm_infer(
                user_collection_name=sanitize_collection_name(user_id), 
                prompt=user_input
            )
        
        return {
            "ai_response": model_response,
            "user_id": user_id,
            "name": name,
            "role": role,
            "enhanced_rag_used": use_enhanced_rag,
            "data_sources_used": [ds.value for ds in default_sources] if use_enhanced_rag and 'default_sources' in locals() else []
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _populate_data_mart_for_role(role: str):
    """
    Populate data mart with role-specific data
    """
    try:
        rag_system = await get_enhanced_rag_system()
        
        # Check if role contains "Gaming" to determine gaming focus
        gaming_focus = "Gaming" in role
        
        if "Analyst" in role:
            # Get analyst-specific data
            if gaming_focus:
                analyst_data = {
                    "business_metrics": {
                        "gaming_revenue": 15000000.0,
                        "average_revenue_per_paying_user": 125.0,
                        "conversion_to_premium": 0.08,
                        "in_game_purchases_rate": 0.25
                    },
                    "user_analytics": {
                        "daily_active_players": 750000,
                        "average_session_duration": 45.2,
                        "games_per_session": 3.8,
                        "completion_rate": 0.67
                    },
                    "gaming_data": {
                        "total_games": 1250,
                        "active_games": 890,
                        "top_categories": ["Strategy", "Action", "Puzzle", "RPG"]
                    }
                }
            else:
                analyst_data = {
                    "business_metrics": {
                        "monthly_revenue": 2500000.0,
                        "average_revenue_per_user": 45.50,
                        "customer_lifetime_value": 850.0
                    },
                    "user_analytics": {
                        "daily_active_users": 125000,
                        "monthly_active_users": 450000,
                        "average_session_duration": 18.5,
                        "user_retention_rate": 0.78
                    }
                }
            
            # Add to data mart
            for data_type, data in analyst_data.items():
                await rag_system.add_to_data_mart(data, data_type)
                
        elif "Leadership" in role:
            # Get leadership-specific data
            if gaming_focus:
                leadership_data = {
                    "strategic_metrics": {
                        "total_gaming_revenue": 15000000,
                        "market_share": 0.15,
                        "year_over_year_growth": 0.28,
                        "profit_margin": 0.22
                    },
                    "gaming_overview": {
                        "total_registered_players": 2500000,
                        "active_players_30d": 750000,
                        "tournaments_hosted": 156
                    }
                }
            else:
                leadership_data = {
                    "strategic_metrics": {
                        "market_share": 0.15,
                        "year_over_year_growth": 0.28,
                        "profit_margin": 0.22
                    },
                    "user_insights": {
                        "total_users": 450000,
                        "growth_rate": 0.12,
                        "customer_satisfaction": 4.2
                    }
                }
            
            # Add to data mart
            for data_type, data in leadership_data.items():
                await rag_system.add_to_data_mart(data, data_type)
        
        logger.info(f"Populated data mart for role: {role}")
        
    except Exception as e:
        logger.error(f"Error populating data mart for role {role}: {e}")

@router.post("/user/chat/data-sources")
async def get_available_data_sources(current_user: Any = Depends(get_current_user)):
    """
    Get available data sources for the current user's role
    """
    try:
        role = current_user["role"]
        
        # Base data sources available to all users
        available_sources = [
            {
                "name": "user_documents",
                "description": "Your uploaded documents and files",
                "enabled": True
            },
            {
                "name": "common_knowledge",
                "description": "Shared knowledge base and documentation",
                "enabled": True
            },
            {
                "name": "conversation_history",
                "description": "Your previous conversations with Mimir",
                "enabled": True
            }
        ]
        
        # Role-specific data sources
        if "Analyst" in role or "Leadership" in role:
            available_sources.extend([
                {
                    "name": "data_mart",
                    "description": "Business metrics and analytical data",
                    "enabled": True
                },
                {
                    "name": "role_specific",
                    "description": f"Content specific to {role} role",
                    "enabled": True
                }
            ])
        
        return {
            "user_role": role,
            "available_sources": available_sources,
            "enhanced_rag_available": True
        }
        
    except Exception as e:
        logger.error(f"Error getting data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
