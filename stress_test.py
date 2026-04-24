import time
from dotenv import load_dotenv
load_dotenv(override=True)
from extractor import determine_platforms, build_search_query, evaluate_candidate
from search_tool import perform_search

QUERIES = [
    "Looking for a 10x developer who knows Rust, Go, and Haskell with 15 years experience, willing to work for equity only",
    "Fresher from IIT Bombay CS branch 2024 passout",
    "Someone who is good at computers",
    "Cybersecurity expert CEH certified, reverse engineering malware, secret clearance",
]

def run_stress_test():
    for q in QUERIES:
        print(f"\n======================================")
        print(f"QUERY: {q}")
        print(f"======================================")
        
        # Agent 1
        platforms = determine_platforms(q)
        print(f"[Agent 1 Strategy] Platforms: {platforms['platforms']} | Reasoning: {platforms['reasoning']}")
        
        # Agent 2
        keywords = build_search_query(q)
        print(f"[Agent 2 Retrieval] Keywords: {keywords}")
        
        # Search
        for plat in platforms['platforms'][:1]: # Test first platform to avoid IP ban
            print(f"Fetching 30 candidates from {plat}...")
            try:
                results = perform_search(keywords, plat, max_results=30)
                print(f"Scraped {len(results)} raw results.")
            except Exception as e:
                print(f"DDG Scrape Error: {e}")
                continue
                
            # Agent 3
            matches = 0
            elite = 0
            for idx, r in enumerate(results):
                try:
                    # Implement backoff for Gemini free tier rate limits
                    time.sleep(2) 
                    eval_data = evaluate_candidate(r['title'], r['snippet'], q)
                    if eval_data['is_match']:
                        matches += 1
                    if eval_data['quality_score'] >= 80:
                        elite += 1
                except Exception as e:
                    print(f"LLM Eval Error: {e}")
            
            print(f"[Agent 3 Evaluation] Out of {len(results)} raw results -> {matches} Matches | {elite} Elite candidates.")

if __name__ == "__main__":
    run_stress_test()
