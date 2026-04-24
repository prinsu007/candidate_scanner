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

# Inject Custom CSS for premium glassmorphism, symmetry & elevation
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Input Fields */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px;
        background: rgba(21, 13, 30, 0.6);
        border: 1px solid rgba(157, 78, 221, 0.2);
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border: 1px solid #9D4EDD;
        box-shadow: 0 0 15px rgba(157, 78, 221, 0.25), inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 10px;
        background: linear-gradient(135deg, #9D4EDD 0%, #5A189A 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(157, 78, 221, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Optional Password Protection for Hosted Apps
app_password = os.getenv("APP_PASSWORD")
if app_password:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #9D4EDD; font-weight: 600;'>Welcome to the hacker's club 🕵️‍♂️</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 16px; color: #A594BA; margin-bottom: 30px;'>enter top secret code to continue</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            entered_pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Secret Code...")
            if st.button("Unlock", use_container_width=True):
                if entered_pwd == app_password:
                    st.session_state.authenticated = True
                    st.rerun()
                elif entered_pwd:
                    st.error("Incorrect code. Access Denied.")
        st.stop()

# Now show the main app title since we are authenticated (or no password required)
st.title("🕵️‍♂️ Automated Candidate Scanner")
st.markdown("Enter your candidate requirements, and the agent will search LinkedIn and Naukri, evaluate profiles using Gemini, and return the best matches.")

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
            
            # Save results to session state so they survive interactions
            if final_candidates:
                st.session_state.final_candidates = sorted(final_candidates, key=lambda x: x["Score"], reverse=True)
            else:
                st.session_state.final_candidates = []
            
# Display Results from Session State
if "final_candidates" in st.session_state:
    candidates = st.session_state.final_candidates
    if candidates:
        st.success(f"✅ Found {len(candidates)} matching candidates! Sorted by Quality Score.")
        
        df = pd.DataFrame(candidates)
        
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
<hr style="border:1px solid rgba(157, 78, 221, 0.15); margin-top: 60px;">
<div style="text-align: center; color: #A594BA; font-family: 'Outfit', sans-serif;">
    <p>Author: <b>Abhinav Jha</b> | <a href="https://github.com/prinsu007/candidate_scanner" target="_blank" style="color: #9D4EDD; text-decoration: none; font-weight: 600;">GitHub Repo</a></p>
</div>
""", unsafe_allow_html=True)
