import streamlit as st
import json
import os
from google import genai
from google.genai import types
from dotenv import load_model

# Load environment variables (API Key)
load_dotenv()

# Initialize Gemini Client (It automatically picks up GEMINI_API_KEY from .env)
try:
    client = genai.Client()
except Exception as e:
    st.error("API Client initialization failed. Please check your .env file.")

# Set up Streamlit Page Layout
st.set_page_config(page_title="AI Customer Message Processor", page_icon="🤖", layout="centered")

st.title("🤖 Customer Message AI Processor")
st.caption("Automatically classifies category, analyzes sentiment, and generates auto-replies.")

# 1. Input Message Section
st.subheader("1. Enter Customer Message")
user_message = st.text_area(
    "Paste or type the customer message below:",
    placeholder="e.g., My order #12344 still hasn't arrived. It's been two weeks. Please help!",
    height=150
)

# Process Button
if st.button("Process Message", type="primary"):
    if not user_message.strip():
        st.warning("Please enter a message first!")
    else:
        # 2. Processing State (Shows clearly on video recording)
        with st.spinner("AI is analyzing the message..."):
            
            # System instructions and prompt to enforce structured JSON output
            prompt = f"""
            You are an advanced customer support AI assistant. 
            Analyze the following customer message and provide a structured JSON response.
            
            Strictly use only these options for your analysis:
            - category: 'Complaint', 'Refund/Return', 'Sales Inquiry', 'Delivery Question', 'Account/Technical Issue', 'General Query', or 'Spam'.
            - sentiment: 'Positive', 'Neutral', or 'Negative'.
            - auto_reply: A short, professional, and empathetic email/message response addressing the customer's specific issue.

            Customer Message: "{user_message}"
            """
            
            try:
                # Call Gemini 2.5 Flash (Fast and Free Tier)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        # Forces the model to return valid JSON
                        response_mime_type="application/json",
                    ),
                )
                
                # Parse JSON output
                result = json.loads(response.text)
                
                # 3. Final Outputs Section
                st.success("Processing Complete!")
                st.markdown("---")
                st.subheader("📋 System Analysis Outputs")
                
                # Create visual columns for Category and Sentiment
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="📊 Category", value=result.get("category", "N/A"))
                with col2:
                    # Color code sentiment visually
                    sentiment = result.get("sentiment", "N/A")
                    st.metric(label="🎭 Sentiment", value=sentiment)
                
                st.markdown("---")
                st.subheader("✉️ Generated Auto-Reply")
                st.info(result.get("auto_reply", "Could not generate reply."))
                
            except Exception as e:
                st.error(f"An error occurred during API processing: {e}")