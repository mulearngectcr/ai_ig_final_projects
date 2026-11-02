# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TripRequest, TripResponse
from agents import TripCrew

app = FastAPI(title="TripSmith API")

# Setup CORS so the React frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "https://ai-ig-final-projects.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to TripSmith API! The backend is working."}

@app.post("/api/plan-trip", response_model=TripResponse)
def plan_trip(request: TripRequest):
    try:
        print(f"Starting trip generation for {request.destination}...")
        
        # 1. Initialize the AI Crew with user data
        crew = TripCrew(
            starting_location=request.starting_location,
            destination=request.destination,
            travel_days=request.travel_days,
            travelers=request.travelers,
            total_budget=request.total_budget,
            travel_preferences=request.travel_preferences
        )
        
        # 2. Run the agents (This will take 30-60 seconds)
        result = str(crew.run())
        print("Generation complete!")

        # 3. Simple Heuristic Parsing 
        # CrewAI outputs a free-form string. We do a quick check for feasibility keywords.
        feasibility = "Not Feasible" if "not feasible" in result.lower() else "Feasible"
        
        warnings = []
        if "warning" in result.lower() or "deficit" in result.lower():
            warnings.append("Budget might be tight or insufficient. Please review the breakdown carefully.")

        # 4. Return the structured response
        return TripResponse(
            feasibility_status=feasibility,
            itinerary=result,  # Passing the full detailed report here so the frontend can render it as Markdown
            estimated_expenses="See the detailed breakdown in the itinerary report above.",
            warnings=warnings
        )

    except Exception as e:
        print(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")