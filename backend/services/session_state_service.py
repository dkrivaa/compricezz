import streamlit as st
from typing import Any


def enter_value_into_session_state(key_name: str, value: Any):
    """ Function to enter value into streamlit session_state if doesn't exist """
    if key_name not in st.session_state:
        st.session_state[key_name] = value


def force_value_into_session_state(key_name: str, value: Any):
    """ Function to enter value into streamlit session_state overwriting existing value """
    st.session_state[key_name] = value


def get_value_from_session_state(key_name: str) -> Any | None:
    """ Function to get value from streamlit session_state """
    if key_name in st.session_state:
        return st.session_state[key_name]

