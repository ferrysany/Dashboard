import streamlit as st
import subprocess, sys, json
import panda as pd

st.set_page_config(layout="wide")

# High-Contrast Personal Mode
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    * { color: #FFFFFF !important; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { background-color: #333; color: white; border: 1px solid #555; }
    hr { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# Add your key visual/JPEG here
if os.path.exists("header.jpeg"):
    st.image("header.jpeg", use_container_width=True)

if st.button('🔄 Run My Script'):
    # We use 'capture_output=True' to grab the error message
    result = subprocess.run([sys.executable, 'main.py'], capture_output=True, text=True)

    if result.returncode == 0:
        #lines = result.stdout.split('\n')

        try:
            # Extract the JSON data from the output
            raw_output = result.stdout.split("---DATA_START---")[-1]
            data = json.loads(raw_output)

            col1, col2, col3 = st.columns(3)

            # Define a helper to format the table
            def show_table(stock_list, title):
                if stock_list:
                    df = pd.DataFrame(stock_list)
                    # Format the change column to show + and %
                    df['Change'] = df['Change'].apply(lambda x: f"{x:+.2f}%")
                    st.subheader(title)
                    st.table(df)  # st.table is a static, clean view

            with col1:
                show_table(data["US"], "🇺🇸 US")
            with col2:
                show_table(data["HK"], "🇭🇰 HK")
            with col3:
                show_table(data["CN"], "🇨🇳 CN")
        except Exception as e:
            st.error("Display Error: Use the refresh button again.")

    else:
        st.error("❌ Your script crashed. Here is why:")
        st.code(result.stderr)  # This is the "magic" line that shows the bug


