import sys
import logging
from mcp.server.fastmcp import FastMCP

# Configure logging strictly to sys.stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("roi_calculator_server")

# Initialize FastMCP
mcp = FastMCP("ROI Calculator Server")

@mcp.tool()
def calculate_task_tax(frequency_per_week: float, minutes_lost_per_incident: float, hourly_rate: float) -> dict:
    """Translates inputs into annual hours lost and opportunity costs.
    
    Args:
        frequency_per_week: How many times per week the incident occurs.
        minutes_lost_per_incident: Productive time lost per incident in minutes.
        hourly_rate: The user's hourly rate or opportunity cost in dollars.
    """
    logger.info(f"calculate_task_tax: freq={frequency_per_week}, minutes={minutes_lost_per_incident}, rate={hourly_rate}")
    annual_hours_lost = (frequency_per_week * 52.0 * minutes_lost_per_incident) / 60.0
    annual_cost = annual_hours_lost * hourly_rate
    
    return {
        "annual_hours_lost": round(annual_hours_lost, 2),
        "one_year_opportunity_cost": round(annual_cost, 2),
        "three_year_opportunity_cost": round(annual_cost * 3.0, 2),
        "five_year_opportunity_cost": round(annual_cost * 5.0, 2)
    }

@mcp.tool()
def calculate_brain_fog_impact(ideas_captured_weekly: int, ideas_lost_weekly: int, minutes_lost_reconstructing: float = 15.0) -> dict:
    """Calculates capture yield and annual reconstruction hours wasted.
    
    Args:
        ideas_captured_weekly: Number of ideas successfully captured per week.
        ideas_lost_weekly: Number of ideas lost per week.
        minutes_lost_reconstructing: Time spent reconstructing each lost idea in minutes.
    """
    logger.info(f"calculate_brain_fog_impact: captured={ideas_captured_weekly}, lost={ideas_lost_weekly}, reconstruct_time={minutes_lost_reconstructing}")
    total = ideas_captured_weekly + ideas_lost_weekly
    capture_yield = (ideas_captured_weekly / total * 100.0) if total > 0 else 0.0
    annual_reconstruction_hours_wasted = (ideas_lost_weekly * 52.0 * minutes_lost_reconstructing) / 60.0
    
    return {
        "capture_yield": round(capture_yield, 2),
        "annual_reconstruction_hours_wasted": round(annual_reconstruction_hours_wasted, 2)
    }

@mcp.tool()
def calculate_content_factory_value(posts_per_week: float, asset_type: str) -> dict:
    """Calculates weekly and annual marketing equity based on standard market values.
    
    Args:
        posts_per_week: Number of content pieces produced per week.
        asset_type: Type of asset ('Blog Posts', 'Social Posts', 'Email Newsletters', 'Proposal Templates').
    """
    logger.info(f"calculate_content_factory_value: posts={posts_per_week}, type={asset_type}")
    normalized = asset_type.strip().lower()
    
    # Map input to standard values
    if normalized in ["blog posts", "blog post", "blog", "blogs"]:
        asset_value = 200.0
    elif normalized in ["social posts", "social post", "social", "socials"]:
        asset_value = 100.0
    elif normalized in ["email newsletters", "email newsletter", "email", "emails", "newsletter", "newsletters"]:
        asset_value = 150.0
    elif normalized in ["proposal templates", "proposal template", "proposal", "proposals", "template", "templates"]:
        asset_value = 300.0
    else:
        raise ValueError(
            f"Unknown asset type: '{asset_type}'. "
            "Expected one of: 'Blog Posts', 'Social Posts', 'Email Newsletters', 'Proposal Templates'."
        )
        
    weekly_equity = posts_per_week * asset_value
    annual_equity = weekly_equity * 52.0
    
    return {
        "weekly_marketing_equity": round(weekly_equity, 2),
        "annual_marketing_equity": round(annual_equity, 2)
    }

if __name__ == "__main__":
    mcp.run()
