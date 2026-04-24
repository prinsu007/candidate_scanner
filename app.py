import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Import logic from our existing files
from search_tool import perform_search
from extractor import determine_platforms, build_search_query, evaluate_candidate

# Ensure environment variables are loaded
load_dotenv(override=True)

st.set_page_config(page_title="Candidate Scanner", page_icon="🕵️‍♂️", layout="wide")

# Inject Custom CSS for premium glassmorphism & typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stTextArea textarea {
        border-radius: 12px;
        background: rgba(23, 23, 33, 0.7);
        border: 1px solid rgba(0, 229, 255, 0.3);
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border: 1px solid #00E5FF;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
    }
    
    .stButton button {
        border-radius: 8px;
        background: linear-gradient(135deg, #00E5FF 0%, #0077FF 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 229, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.title("🕵️‍♂️ Automated Candidate Scanner")
st.markdown("Enter your candidate requirements, and the agent will search LinkedIn and Naukri, evaluate profiles using Gemini, and return the best matches.")

# Optional Password Protection for Hosted Apps
app_password = os.getenv("APP_PASSWORD")
if app_password:
    with st.sidebar:
        st.markdown("### 🔒 Private Access")
        entered_pwd = st.text_input("Enter Password", type="password")
    if entered_pwd != app_password:
        st.info("👋 Welcome! This app is password protected to prevent unauthorized API token usage. Please enter the password in the sidebar.")
        st.stop()

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    st.error("🚨 Missing Gemini API Key! Please update the `.env` file or Streamlit Secrets with your actual key before running.")
    st.stop()

# User Input
col_input, col_settings = st.columns([3, 1])

with col_input:
    user_query = st.text_area("Candidate Requirements", placeholder="e.g., dotnet developer azure 2 years < 15 days notice", height=120)

with col_settings:
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    num_candidates = st.number_input("Candidates per Platform", min_value=5, max_value=50, value=15, step=5, help="How many raw search results to evaluate per platform.")
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    search_button = st.button("🚀 Start Scanner", type="primary", use_container_width=True)

if search_button:
    if not user_query.strip():
        st.warning("Please enter your candidate requirements first.")
    else:
        with st.status("Running Candidate Scanner...", expanded=True) as status:
            
            st.write("🕵️‍♂️ **Agent 1 (Strategy):** Determining best platforms...")
            strategy = determine_platforms(user_query)
            platforms = strategy['platforms']
            
            st.info(f"**Selected Platforms:** {', '.join([p.capitalize() for p in platforms])}\n\n*Reasoning:* {strategy['reasoning']}")
            
            st.write("🤖 **Agent 2 (Retrieval):** Parsing your query with Gemini...")
            dork_keywords = build_search_query(user_query)
            st.info(f"**Optimized Search Keywords:** `{dork_keywords}`")
            
            all_results = []
            
            for platform in platforms:
                st.write(f"🔍 Searching {platform.capitalize()}...")
                results = perform_search(dork_keywords, platform, max_results=num_candidates)
                st.write(f"Found {len(results)} potential profiles on {platform}.")
                all_results.extend(results)
            
            st.write(f"🧠 **Agent 3 (Evaluation):** Evaluating {len(all_results)} profiles with Gemini...")
            
            # Progress bar for evaluation
            progress_bar = st.progress(0)
            final_candidates = []
            
            for idx, res in enumerate(all_results):
                # Update progress bar
                progress = (idx + 1) / len(all_results)
                progress_bar.progress(progress, text=f"Evaluating profile {idx+1}/{len(all_results)}: {res['title'][:30]}...")
                
                eval_data = evaluate_candidate(res['title'], res['snippet'], user_query)
                
                if eval_data['is_match']:
                    final_candidates.append({
                        "Name": eval_data['candidate_name'],
                        "Score": eval_data['quality_score'],
                        "Elite Traits": ", ".join(eval_data['exceptional_traits']) if eval_data['exceptional_traits'] else "None",
                        "Fluff/Red Flags": ", ".join(eval_data['fluff_or_bluffs']) if eval_data['fluff_or_bluffs'] else "None",
                        "Platform": res['platform'].capitalize(),
                        "URL": res['url'],
                        "Reasoning": eval_data['reasoning'],
                        "Raw Snippet": res['snippet']
                    })
            
            status.update(label="Scanning Complete!", state="complete", expanded=False)
            
        # Display Results
        if final_candidates:
            # Sort the candidates by Score descending to get the "cream layer" on top
            final_candidates = sorted(final_candidates, key=lambda x: x["Score"], reverse=True)
            
            st.success(f"✅ Found {len(final_candidates)} matching candidates! Sorted by Quality Score.")
            
            df = pd.DataFrame(final_candidates)
            
            # Allow user to download the CSV directly from the frontend
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name='candidates.csv',
                mime='text/csv',
            )
            
            # Display interactive table
            st.dataframe(
                df,
                column_config={
                    "URL": st.column_config.LinkColumn("Profile Link"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.error("❌ No candidates matched your exact requirements. Try broadening your query.")

st.markdown("""
<hr style="border:1px solid rgba(255,255,255,0.1); margin-top: 50px;">
<div style="text-align: center; color: #888; font-family: 'Outfit', sans-serif;">
    <p>Made with 🩵 by <b>Antigravity</b> | Powered by Gemini 2.5 Flash</p>
</div>
""", unsafe_allow_html=True)
