import streamlit as st

from backend.utilities.general import get_chain_from_code, session_code
from ui.common_elements import item_selector, price_element, promo_element


def session_keys():
    """ Helper - Getting essential info from session_state """
    chain_code = st.session_state.get('chain_code')
    store_code = st.session_state.get('store_code')
    # Reconstruct session keys
    if chain_code and store_code:
        session_key_price = f'{session_code(chain_code, store_code)}_price_data'
        session_key_promo = f'{session_code(chain_code, store_code)}_promo_data'

        return session_key_price, session_key_promo


def render():
    """ The main function to render the item page """
    # Get chain object matching given chain code
    chain = get_chain_from_code(st.session_state.get('chain_code'))
    # Get session keys for stored price_data and promo_data
    session_key_price, session_key_promo = session_keys()
    # Populate item selector
    item = item_selector(st.session_state.get(session_key_price))

    if item:
        # Get price details for item from price data
        item_details = chain.get_shopping_prices(price_data=st.session_state.get(session_key_price),
                                                 shoppinglist=[item]) if st.session_state.get(session_key_price) else None
        # Get relevant promo blacklist for the chain
        blacklist = chain.promo_blacklist() if chain else set()
        # Get promo details for item from promo data
        item_promos = chain.get_shopping_promos(promo_data=st.session_state.get(session_key_promo),
                                                shoppinglist=[item],
                                                blacklist=blacklist) if st.session_state.get(session_key_promo) else None

        # Show price
        price_element(item, item_details)

        # Show promotions
        if item_promos:
            st.subheader('Promotions')
            if item_promos and item_promos.get(item):
                for promo in item_promos[item]:
                    promo_element(chain, promo)
            else:
                st.info("No promotions available for this product at the moment.")



if __name__ == "__main__":
    render()