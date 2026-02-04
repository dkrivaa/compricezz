import streamlit as st
from backend.core.super_class import SupermarketChain


def get_chain_from_code(chain_code):
    """ Get chain object from chain code """
    # List of all registered supermarket chains
    chains = SupermarketChain.registry
    # Get chain matching given chain code
    chain = next(c for c in chains if c.chain_code == chain_code)

    return chain


def session_code(chain_code: str | int, store_code: str | int) -> str:
    """ Make unique key combining chain_code and store_code """
    return f'{str(chain_code)}_{str(store_code)}'
