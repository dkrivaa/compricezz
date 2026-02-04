import streamlit as st
from backend.core.super_class import SupermarketChain
from backend.services.async_runner import run_async
from backend.services.db_service import get_stores_for_chain
from backend.utilities.general import get_chain_from_code


def chain_selector():
    """ Chain selector dropdown """
    # Get all registered supermarket chains
    chains = SupermarketChain.registry
    # Make dict with chain_code as key and alias as value
    code_to_alias = {c.chain_code: c.alias for c in chains}
    # Sort the chain codes by their alias
    sorted_codes = sorted(code_to_alias.keys(), key=lambda x: code_to_alias[x])

    chain = st.selectbox(
        label='Select Supermarket Chain',
        options=sorted_codes,  # Use sorted list instead of list(code_to_alias)
        format_func=lambda x: code_to_alias[x].capitalize(),
        index=None,
        placeholder='Select Chain',
        key='chain_selector'
    )

    chain_alias = next(c.alias for c in chains if c.chain_code == chain) if chain else None
    # Return chain_code of selected chain
    return chain, chain_alias


def store_selector(chain_code):
    """ Gets stores for chain defined by chain_code """
    # Get chain object matching given chain code
    chain = get_chain_from_code(chain_code)
    # Get stores for chain
    stores = run_async(get_stores_for_chain, chain=chain)

    # Make selectBox to select store
    store = st.selectbox(
        label='Select Store',
        placeholder='Select Store',
        options=sorted([s.store_code for s in stores], key=lambda x: int(x)),
        format_func=lambda x: f'{x} - {next(s.store_name for s in stores if s.store_code == x)}',
        index=None,
        key='store_selector'
    )

    store_name = next(s.store_name for s in stores if s.store_code == store) if store else None

    # Return store_code for selected store
    return store, store_name


def item_selector(price_data):
    item = st.selectbox(
        label='Item',
        placeholder='Select Item',
        options=sorted([d['ItemCode'] for d in price_data], key=int),
        format_func=lambda x: f"{x} - {next(d.get('ItemName') or d.get('ItemNm') for d in price_data
                                            if d['ItemCode'] == x)}",
        index=None,
        key='item_selector'
    )

    return item


def price_element(item: str, item_details: dict):
    """ Renders a single price element for the given item """
    st.subheader('Price')
    st.metric(
        label=f"{item} - {
        (
                item_details.get(item, {}).get("ItemName")
                or item_details.get(item, {}).get("ItemNm")
                or "N/A"
        )
        }",
        label_visibility='collapsed',
        value=(
            f"{item_details[item]['ItemPrice']} NIS"
            if item_details and item_details.get(item)
            else "N/A"
        ),
    )

    st.divider()


def promo_element(chain: SupermarketChain, promo: dict):
    """ Renders a single promo element according to reward type"""
    # Dispatcher
    PROMO_RENDERERS = {
        '1': render_quantity_discount,
        '2': render_percentage_discount,
        '3': render_percentage_discount,
        '6': render_quantity_discount,
        '10': render_quantity_discount,
    }
    # Get reward type and corresponding handler
    reward_type = promo.get('RewardType')
    handler = PROMO_RENDERERS.get(reward_type, None)
    # Call handler if exists
    handler(chain, promo)


def render_quantity_discount(chain: SupermarketChain, promo: dict):
    """ Renders a single promo element with reward type 1"""
    st.markdown(f"**{promo.get('PromotionDescription', 'N/A')}**")
    st.metric(
        label="Promotion Price",
        value=f"{promo.get('DiscountedPrice', 'N/A')} NIS",
    )
    st.write(f"- Minimum Quantity: {promo.get('MinQty', 'N/A')}")
    st.write(f"- Maximum Quantity: {promo.get('MaxQty', 'N/A')}")
    st.write(f"- Minimum Purchase: {promo.get('MinPurchaseAmnt', 'N/A')}")
    st.write(f"- Target Customers: {chain.promo_audience(promo)}")
    st.write(f"- Valid Until: {promo.get('PromotionEndDate', 'N/A')}")
    st.divider()


def render_percentage_discount(chain: SupermarketChain, promo: dict):
    """ Renders a single promo element with reward type 2"""
    st.markdown(f"**{promo.get('PromotionDescription', 'N/A')}**")
    st.metric(
        label="Promotion Discount",
        value=f"{int(promo.get('DiscountRate')) / 100}%",
    )
    st.write(f"- Minimum Quantity: {promo.get('MinQty', 'N/A')}")
    st.write(f"- Maximum Quantity: {promo.get('MaxQty', 'N/A')}")
    st.write(f"- Target Customers: {chain.promo_audience(promo)}")
    st.write(f"- Valid Until: {promo.get('PromotionEndDate', 'N/A')}")
    st.divider()


def selected_stores_for_planning():
    """ Returns a table like presentation of selected stores with option to delete selection """
    # Check if selected_stores exist and non empty
    if st.session_state.get('selected_stores'):
        with st.container():
            for idx, item in enumerate(st.session_state.get('selected_stores')):
                col1, col2 = st.columns(spec=[5, 1], vertical_alignment='center')

                col1.write(f"{item['chain_alias']} - {item['store_name']}")
                if col2.button(label='', icon=":material/delete:", key=f'{idx}_button'):
                    del st.session_state.selected_stores[idx]
                    st.rerun()

