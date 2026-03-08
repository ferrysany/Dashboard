import streamlit as st
import subprocess
import sys

st.title("🚀 My Dashboard")

if st.button('🔄 Run My Script'):
    # We use 'capture_output=True' to grab the error message
    result = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True)

    if result.returncode == 0:
        st.code(result.stdout)
    else:
        st.error("❌ Your script crashed. Here is why:")
        st.code(result.stderr)  # This is the "magic" line that shows the bug

