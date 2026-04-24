import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    keywords: str = Field(description="Broad search keywords. e.g. '(\"dotnet\" OR \".net\" OR \"c#\") AND \"azure\"'")
    
class CandidateEvaluation(BaseModel):
    candidate_name: str = Field(description="The name of the candidate extracted from the title or snippet. If unknown, put 'Unknown'.")
    is_match: bool = Field(description="True if the snippet indicates they match the requirements (e.g., notice period, skills).")
    quality_score: int = Field(description="A strict score from 0 to 100 representing candidate quality. 100=Elite, 50=Average, 0=Poor.")
    exceptional_traits: list[str] = Field(description="Concrete, high-signal achievements or elite skills found. Must be factual from text. Empty if none.")
    fluff_or_bluffs: list[str] = Field(description="Low-value buzzwords, generic claims, or entry-level certs used as filler.")
    reasoning: str = Field(description="A brief explanation of the score and match.")

class SearchStrategy(BaseModel):
    platforms: list[str] = Field(description="List of platforms to search. Choose from: 'linkedin', 'naukri', 'github', 'kaggle', 'behance', 'dribbble'. Max 3.")
    reasoning: str = Field(description="Explanation of why these platforms are the best fit for the role.")

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Please set a valid GEMINI_API_KEY in the .env file.")
    # gemini-2.5-flash is extremely fast and cost-effective
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key, temperature=0.1)

def determine_platforms(user_request: str) -> dict:
    """Agent 1: Decides which platforms are best suited for the query."""
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(SearchStrategy)
        prompt = f"""
        You are the Strategy Agent. Analyze the candidate request and select the BEST platforms to search.
        - UI/UX Designers -> behance, dribbble, linkedin
        - Data Scientists/Engineers -> kaggle, github, linkedin
        - Software Developers -> github, linkedin
        - Non-tech or generic roles -> linkedin, naukri
        
        User Request: {user_request}
        """
        result = structured_llm.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        return {"platforms": ["linkedin", "naukri"], "reasoning": "Fallback to default platforms."}

def build_search_query(user_request: str) -> str:
    """Uses LLM to convert a natural language request into Google Dork keywords."""
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(SearchQuery)
        
        prompt = f"""
        You are an expert technical recruiter. Your task is to maximize the number of relevant resumes retrieved from a search engine.
        Extract ONLY the core technologies, titles, and hard skills from the user request. 
        DO NOT include constraints like years of experience (e.g., "2 years"), notice periods, soft skills, or complex phrases in the search query. The search query must be very BROAD.
        Use OR for synonyms to cast a wide net (e.g., ("dotnet" OR ".net" OR "c#")).
        DO NOT include the 'site:' operator. Do not output anything else but the keywords.
        
        User Request: {user_request}
        """
        result = structured_llm.invoke(prompt)
        return result.keywords
    except Exception as e:
        print(f"\nError parsing query with Gemini: {e}")
        print("Falling back to raw query...")
        return user_request

def evaluate_candidate(title: str, snippet: str, user_request: str) -> dict:
    """Evaluates a search snippet to see if it matches the user requirements."""
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(CandidateEvaluation)
        
        prompt = f"""
        You are an elite, no-nonsense technical recruiter evaluating a candidate profile snippet from a search engine result.
        User Requirements: {user_request}
        
        Candidate Title: {title}
        Candidate Snippet: {snippet}
        
        Step 1: Determine `is_match`. Does this person meet the core technical requirements? (Be generous if the snippet is short but mentions core tech).
        Step 2: Assign a strict `quality_score` (0-100). You MUST adapt your rubric based on the user's requested experience level:
            - If requesting SENIOR/LEAD: Elite (80-100) means leading teams, scaling systems, high-impact verbs.
            - If requesting FRESHER/JUNIOR (e.g., "0-2 years"): Elite (80-100) means top-tier universities (like IIT/NIT), competitive programming achievements (ICPC, high ratings), elite internships, or exceptional personal projects.
            - Average (40-79) means they meet the baseline requirements but have generic descriptions.
            - Poor (0-39) means keyword stuffing, irrelevant low-tier certs used as fluff, or generic buzzwords.
        Step 3: Extract `exceptional_traits` and `fluff_or_bluffs`. DO NOT hallucinate! If the snippet is too short to prove elite status, leave traits empty and give an average score. True quality means undeniable evidence of impact.
        """
        
        result = structured_llm.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        # If extraction fails, we assume it's a match so we don't lose potential data
        return {
            "candidate_name": "Unknown",
            "is_match": True, 
            "quality_score": 50,
            "exceptional_traits": [],
            "fluff_or_bluffs": [],
            "reasoning": f"Evaluation failed due to API error, included for manual review."
        }
