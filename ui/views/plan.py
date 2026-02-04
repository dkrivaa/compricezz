import streamlit as st

from backend.services.async_runner import run_async
from backend.pipelines.fresh_price_promo import planning_data
from ui.common_elements import chain_selector, store_selector, selected_stores_for_planning


@st.dialog(title='Select Main Store', dismissible=False)
def leading_store():
    """ Determine main store to use for preparation of shoppinglist """
    if 'main_store' in st.session_state and st.session_state['main_store'] in st.session_state['selected_stores']:
        main_store = st.session_state['main_store']
        st.write(f'Current Main Store: {main_store["chain_alias"]} - {main_store["store_name"]}')
    else:
        main_store = st.radio(
            label='Main Store',
            options=[d for d in st.session_state['selected_stores']],
            format_func=lambda x: f"{x['chain_alias']} - {x['store_name']}",
            index=None
        )

    if main_store:
        if st.button('Continue'):
            # Set main_store in session state
            st.session_state['main_store'] = main_store

            # Getting price data for all selected stores
            with st.spinner('Getting Your Data'):
                stores_list = st.session_state.get('selected_stores')
                if stores_list:
                    run_async(planning_data, stores_list=stores_list)

            # if shoppinglist exist, delete
            if 'shoppinglist' in st.session_state:
                del st.session_state['shoppinglist']
            # Continue to shoppinglist page
            st.switch_page('ui/views/shoppinglist.py')


@st.dialog('No Stores Selected')
def no_stores():
    """ Error if 'Continue' pressed without any stores selected """
    st.error('Please select one or more stores.')


def render():
    # Initiate session_state
    # Flag to indicate whether to reset selectors or not
    if 'reset_selectors' not in st.session_state:
        st.session_state['reset_selectors'] = False
    if 'chain_code' in st.session_state:
        del st.session_state['chain_code']
    # A list to hold stores added by user -
    # {chain_code: 123, chain_alias: shufersal, store_code: 456, store_name: xyz}
    if 'selected_stores' not in st.session_state:
        st.session_state['selected_stores'] = []

    if st.session_state['reset_selectors']:
        if 'chain_selector' in st.session_state:
            st.session_state['chain_selector'] = ''
        if 'store_selector' in st.session_state:
            st.session_state['store_selector'] = ''
        st.session_state['reset_selectors'] = False
        st.rerun()

    st.title('PLAN')
    st.subheader('Make Shoppinglist and Compare Prices')
    st.divider()

    # Selection of chain and store
    with st.container(border=True):
        st.subheader(':blue[Select Stores:]')
        chain_code, chain_alias = chain_selector()
        if chain_code:
            # Only run spinner when actually loading stores
            with st.spinner('Loading Stores...'):
                store_code, store_name = store_selector(chain_code=chain_code)

            if store_code:
                # Add selected store to session_state
                st.session_state['selected_stores'].append({'chain_code': chain_code,
                                                            'chain_alias': chain_alias,
                                                            'store_code': store_code,
                                                            'store_name': store_name})
                st.session_state['reset_selectors'] = True
                st.rerun()

    # Display of already selected stores
    with st.container(border=True):
        # Title row for selected stores with option to reset
        col1, col2 = st.columns(spec=[5, 1], vertical_alignment='bottom')
        col1.subheader(':orange[Selected Stores:]')
        if col2.button(label='Reset', icon=":material/cleaning_bucket:"):
            st.session_state['selected_stores'] = []
            if 'lead_store' in st.session_state:
                del st.session_state['lead_store']
        # Selected stores
        if len(st.session_state['selected_stores']) > 0:
            selected_stores_for_planning()
        else:
            st.info('No Stores Selected Yet')

    # Continue to shoppinglist
    if st.button(label='Continue', key='continue'):
        if len(st.session_state['selected_stores']) > 0:
            leading_store()
        else:
            no_stores()


if __name__ == "__main__":
    render()