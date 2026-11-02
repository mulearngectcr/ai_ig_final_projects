# backend/agents.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from rag_manager import RAGManager

load_dotenv()

rag = RAGManager()

# Retaining your specified Groq LLM setup
groq_llm = LLM(
    model="openai/openai/gpt-oss-120b",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.2
)

@tool("Kerala Tourism Database")
def search_kerala_tourism(query: str) -> str:
    """Search the local database for Kerala tourism facts, budgets, and travel times."""
    results = rag.query(query)
    if not results:
        return "No relevant information found in the database."
    return "\n".join(results)

class TripCrew:
    # Added travel_preferences here
    def __init__(self, starting_location, destination, travel_days, travelers, total_budget, travel_preferences="None"):
        self.inputs = {
            "starting_location": starting_location,
            "destination": destination,
            "travel_days": travel_days,
            "travelers": travelers,
            "total_budget": total_budget,
            "travel_preferences": travel_preferences
        }

    def run(self):
        researcher = Agent(
            role='Destination Researcher',
            goal='Retrieve factual tourism data, travel times, and daily costs for {destination} from the local database.',
            backstory='You are a meticulous local Kerala travel expert. You strictly rely on the provided database tool for factual information and never invent prices.',
            verbose=True,
            allow_delegation=False,
            tools=[search_kerala_tourism],
            llm=groq_llm
        )

        planner = Agent(
            role='Itinerary Planner',
            # Added preferences to the goal
            goal='Create a realistic, day-by-day itinerary for {travel_days} days to {destination} starting from {starting_location}, focusing on {travel_preferences}.',
            backstory='You are a master travel planner. You organize logical itineraries based ONLY on the factual data provided by the researcher and the user preferences.',
            verbose=True,
            allow_delegation=False,
            llm=groq_llm 
        )

        budget_analyst = Agent(
            role='Budget Analyst',
            goal='Review the itinerary and estimate total costs for {travelers} travelers. Compare it to the user budget of {total_budget} INR.',
            backstory='You are a strict financial advisor. You calculate estimated costs to ensure the trip is financially viable based on the researcher data. You highlight any deficits.',
            verbose=True,
            allow_delegation=False,
            llm=groq_llm 
        )

        research_task = Task(
            description='Search the database for details about {destination}. Extract daily budget estimates, attractions matching {travel_preferences}, and travel constraints.',
            expected_output='A clear summary of facts, costs, and travel times for the destination.',
            agent=researcher
        )

        plan_task = Task(
            description='Using the researcher data, create a {travel_days}-day itinerary. Factor in travel time from {starting_location} and accommodate {travel_preferences}.',
            expected_output='A structured, day-by-day itinerary with specific activities and logical travel logistics.',
            agent=planner
        )

        budget_task = Task(
            description='Calculate the total estimated cost for {travelers} people. Compare this to the {total_budget} INR budget. Determine if the trip is feasible and list any warnings.',
            expected_output='A detailed report containing the final itinerary, cost breakdown, a clear feasibility status (Feasible/Not Feasible), and a list of warnings. CRITICAL INSTRUCTION: You must calculate the itemized cost breakdown FIRST. Compare the total estimated cost to the user provided budget. You are STRICTLY FORBIDDEN from generating any warnings about the budget being "tight" or "insufficient" if the total estimated cost is lower than the user budget.',
            agent=budget_analyst
        )

        crew = Crew(
            agents=[researcher, planner, budget_analyst],
            tasks=[research_task, plan_task, budget_task],
            process=Process.sequential, 
            verbose=True
        )

        return crew.kickoff(inputs=self.inputs)