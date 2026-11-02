# backend/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class TripRequest(BaseModel):
    starting_location: str = Field(..., min_length=2, description="Where the user is starting from")
    destination: str = Field(..., min_length=2, description="Destination in Kerala")
    travel_days: int = Field(..., gt=0, le=30, description="Number of days (1 to 30)")
    travelers: int = Field(..., gt=0, le=20, description="Number of people traveling")
    total_budget: float = Field(..., gt=0, description="Total budget for the trip in INR")
    travel_preferences: Optional[str] = Field("None", description="e.g., adventure, relaxing, historical")

class TripResponse(BaseModel):
    # This matches the core project objectives you defined
    feasibility_status: str = Field(..., description="Is the trip practical? e.g., 'Feasible' or 'Not Feasible'")
    itinerary: str = Field(..., description="Day-wise travel itinerary")
    estimated_expenses: str = Field(..., description="Estimated expenses and budget breakdown")
    warnings: List[str] = Field(default=[], description="Warnings about impractical plans")