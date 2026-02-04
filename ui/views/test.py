import streamlit as st

from backend.core.super_class import SupermarketChain
from backend.services.async_runner import run_async


chains = SupermarketChain.registry
st.write(chains)
chain = chains[-1]
st.write(run_async(chain.get_file, store_code=134, file_type=2))


