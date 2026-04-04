import streamlit as st
import subprocess
import sys

st.title("🚀 My Dashboard")

if st.button('🔄 Run My Script'):
    # We use 'capture_output=True' to grab the error message
    result = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True)

    if result.returncode == 0:
        #st.markdown(result.stdout.replace('\n',' \n'))
        # Split the output by lines and display each line separately
        for line in res.stdout.split('\n'):
            if line.strip():
                # st.write is natively responsive and adds proper spacing
                st.write(line.strip())
    else:
        st.error("❌ Your script crashed. Here is why:")
        st.code(result.stderr)  # This is the "magic" line that shows the bug

