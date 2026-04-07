import streamlit as st
import subprocess
import sys

st.set_page_config(layout="wide")
st.title("🚀 My Dashboard")

if st.button('🔄 Run My Script'):
    # We use 'capture_output=True' to grab the error message
    result = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True)

    if result.returncode == 0:
        lines = result.stdout.split('\n')

        try:
            # 1. Split the data based on the markers we set in main.py
            # This looks for the start and end of each section
            us_list = [l for l in lines[lines.index("---US---") + 1: lines.index("---HK---")] if l.strip()]
            hk_list = [l for l in lines[lines.index("---HK---") + 1: lines.index("---CN---")] if l.strip()]
            cn_list = [l for l in lines[lines.index("---CN---") + 1:] if l.strip()]

            # 2. Create the side-by-side layout
            col1, col2, col3  = st.columns(3)

            with col1:
                st.subheader("🇺🇸 US Stocks")
                for row in us_list:
                    # st.write ensures it wraps correctly on your phone
                    st.write(row)

            with col2:
                st.subheader("🇭🇰 HK Stocks")
                for row in hk_list:
                    st.write(row)

            with col3:
                st.subheader("🇨🇳 CN")
                for row in cn_list: st.write(row)

        except ValueError:
            # If the markers aren't found, just display everything normally
            for line in lines:
                if line.strip():
                    st.write(line.strip())
    else:
        st.error("❌ Your script crashed. Here is why:")
        st.code(result.stderr)  # This is the "magic" line that shows the bug


