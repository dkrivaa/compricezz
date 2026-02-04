import streamlit as st


def reset_chain():
    st.session_state.chain_selector = None


@st.dialog(
    title='Error',
    icon=":material/database_off:",
    on_dismiss=reset_chain
)
def no_data_error(errorType: str):
    """ RuntimeError when no price data returned from chain """
    st.write(f'{errorType} - No data available from supermarket chain.')



