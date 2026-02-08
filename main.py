# For streamlit cloud
import subprocess
subprocess.run(["playwright", "install", "chromium"], check=True)

# For streamlit on local
import sys
import asyncio
# Fix for Windows + Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st

# Initialize all chains
from backend.bootstrap import initialize_backend
initialize_backend()


# st.set_page_config - Set the configuration of the Streamlit page
st.set_page_config(
    page_title="My App",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CSS across app
st.markdown("""
<style>
    @media (max-width: 768px) {
        .block-container {padding: 1rem;}
        .stButton > button {width: 100%;}
    }
</style>
""", unsafe_allow_html=True)


home_page = st.Page(
    title='Home',
    page='ui/views/home.py',
    icon=":material/home:",
    default=True
)

shop_page = st.Page(
    title='SHOP',
    page='ui/views/shop.py',
    icon=":material/shopping_cart:",
)

item_page = st.Page(
    title='Item Info',
    page='ui/views/item.py',
    icon=":material/barcode:",
)

plan_page = st.Page(
    title='PLAN',
    page='ui/views/plan.py',
    icon=":material/list:",
)

shoppinglist_page = st.Page(
    title='Prepare Shoppinglist',
    page='ui/views/shoppinglist.py',
    icon=":material/list_alt:"
)

pricecomparison_page = st.Page(
    title='Price Comparison',
    page='ui/views/pricecomparison.py',
    icon=":material/compare_arrows:",
)

db_page = st.Page(
    title='Database',
    page='ui/views/db.py',
    icon=":material/data_table:",
)

test_page = st.Page(
    title='Test',
    page='ui/views/test.py'
)

pages = {
    "": [home_page],
    "Shopping": [shop_page, item_page],
    "Planning": [plan_page, shoppinglist_page, pricecomparison_page]
}

pg = st.navigation(pages=pages, position='top')

pg.run()
