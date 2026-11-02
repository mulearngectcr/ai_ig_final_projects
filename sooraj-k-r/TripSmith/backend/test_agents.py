# backend/test_agents.py
import sys
print("1. Python executed the file...")

try:
    from agents import TripCrew
    print("2. Successfully imported TripCrew...")
except Exception as e:
    print(f"FAILED AT IMPORT: {e}")
    sys.exit(1)

def run_test():
    print("3. --- Starting TripSmith AI Crew ---")
    
    try:
        print("4. Initializing TripCrew object...")
        trip_crew = TripCrew(
            starting_location="Kochi",
            destination="Munnar, Kerala",
            travel_days=3,
            travelers=2,
            total_budget=15000
        )
        
        print("5. Kicking off the Crew (Connecting to Groq)...")
        result = trip_crew.run()
        
        print("6. === FINAL TRIP PLAN ===")
        print(result)
        
    except Exception as e:
        print(f"FAILED DURING EXECUTION: {e}")

if __name__ == "__main__":
    run_test()