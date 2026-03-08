import streamlit as st
import subprocess
import sys

# This is the "Skin"
st.set_page_config(page_title="2026 Dashboard", page_icon="📈")
st.title("🚀 Daily News & Stocks")

if st.button('🔄 Run My Script Now'):
    with st.spinner('Fetching latest data...'):
        # This line runs your ORIGINAL script exactly as it is
        # Replace 'your_original_script.py' with your actual filename
        result = subprocess.check_output([sys.executable, 'main.py'], text=True)

        # This shows the terminal output on the website
        st.code(result, language='text')
else:
    st.write("Click the button above to see your NBA scores, Stocks, and News.")

