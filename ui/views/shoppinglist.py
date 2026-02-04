import streamlit as st
from backend.services.async_runner import run_async
from backend.pipelines.fresh_price_promo import planning_data
from backend.utilities.general import session_code
from backend.agent.alternative_product import get_alternatives
from ui.common_elements import item_selector


def main_store_session_key():
    """ Return main store session key """
    main_store = st.session_state.get('main_store')
    main_session_key = session_code(chain_code=main_store['chain_code'],
                                    store_code=main_store['store_code'])
    return main_session_key


def check_data():
    """ Check if selected stores have data and open dialog if missing """

    @st.dialog(title='Missing Data', dismissible=False)
    def missing_data_dialog(store: dict):
        """ If missing data, open dialog """
        st.write(f"No data available for {store['chain_alias']} - {store['store_name']}")
        # Remove store without data
        st.session_state['selected_stores'] = [d for d in st.session_state['selected_stores']
                                               if d != store]
        # User decision if missing data
        options_map = {
            0: ':material/arrow_back:',
            1: ':material/shopping_cart:'
        }
        decision = st.pills(
            label='Decision',
            label_visibility='hidden',
            options=list(options_map.keys()),
            format_func=lambda x: options_map[x],
            default=None
        )

        if decision == 0:
            st.switch_page('ui/views/plan.py')
        if decision == 1:
            st.session_state.data_checked = True
            st.rerun()

    for store in st.session_state.get('selected_stores'):
        key = session_code(store['chain_code'], store['store_code'])

        if st.session_state[key] is None:
            missing_data_dialog(store=store)
        else:
            st.session_state.data_checked = True


def not_main_store_session_keys():
    """ Returns list of session keys, except main store """
    # Get list of dicts with selected stores
    selected_stores = st.session_state.get('selected_stores')
    # Return list of session keys, except main store
    return [session_code(d['chain_code'], d['store_code'])
            for d in selected_stores
            if d != st.session_state.get('main_store')]


def get_alternative_products(store_key: str, item: str):
    """ Runs the algorithm to get alternative products for missing barcodes """
    # Get all products in alternative store
    all_products = st.session_state[store_key]
    # Get the input_product
    main_store_key = main_store_session_key()
    print(item, main_store_key)
    print(len(st.session_state[main_store_key]))
    input_product = next(d for d in st.session_state[main_store_key]
                         if d['ItemCode'] == item)

    alternatives = run_async(get_alternatives,
                             all_products=all_products,
                             input_product=input_product)
    return alternatives


def add_item(item: str, quantity: float):
    """ Add item to shoppinglist """
    # Get session keys (chain_code_store_code) - i.e 123_456
    main_store_key = main_store_session_key()
    other_store_keys = not_main_store_session_keys()

    # Append new item to main shoppinglist
    st.session_state.shoppinglist[main_store_key].append({'item': item, 'quantity': quantity})
    # list to hold alternative products for all stores where original ItemCode not available
    all_alternatives = []
    for store_key in other_store_keys:
        if st.session_state[store_key]:
            if any(d['ItemCode'] == item for d in st.session_state[store_key]):
                st.session_state.shoppinglist[store_key].append({'item': item, 'quantity': quantity})
            else:
                print(item, 'Not available')
                # Get a list of alternative products
                alternatives = get_alternative_products(store_key=store_key, item=item)
                all_alternatives.append([alternatives, quantity, store_key])
        else:
            print('No data')

    # if alternatives exist, open dialog to select alternative product
    @st.dialog(title='Select Alternative Item', dismissible=False)
    def select_alternative_item(all_alternatives: list[list]):
        """ Dialog for selection of alternative item """
        # Initialize session state for tracking selections
        if 'alternative_selections' not in st.session_state:
            st.session_state.alternative_selections = {}
        # Number of stores that need alternative item
        num_stores = len(all_alternatives)

        # Each alternative = [alternatives, quantity, store_key] where alternatives is list of items
        for alternative in all_alternatives:
            alternatives = alternative[0]
            quantity = alternative[1]
            store_key = alternative[2]

            options = [d['ItemCode'] for d in alternatives]

            selection = st.radio(
                label='Select Alternative Item',
                options=options,
                format_func=lambda x: f'{x} - {next(d.get('ItemName') or d.get('ItemNm') 
                                                    for d in alternatives 
                                                    if d['ItemCode'] == x)}',
                index=None,
                key=f'alt_selection_{store_key}'
            )

            # Store selection in session state
            if selection:
                st.session_state.alternative_selections[store_key] = {
                    'item': selection,
                    'quantity': quantity
                }

        # Check if all selections made
        all_selected = len(st.session_state.alternative_selections) == num_stores

        # Show button only when all selections made
        if all_selected:
            if st.button('Back to Shoppinglist'):
                # Now add all selections to shoppinglist
                for store_key, data in st.session_state.alternative_selections.items():
                    st.session_state.shoppinglist[store_key].append(data)

                # Clear selections
                del st.session_state.alternative_selections
                st.rerun()

    if all_alternatives:
        select_alternative_item(all_alternatives=all_alternatives)
    else:
        st.rerun()


def delete_item(idx: int):
    """ Delete item from shoppinglist according to index """
    main_store_key = main_store_session_key()
    other_store_keys = not_main_store_session_keys()
    del st.session_state.shoppinglist[main_store_key][idx]
    for key in other_store_keys:
        del st.session_state.shoppinglist[key][idx]


def update_quantity(idx: int, updated_quantity):
    """ Update item quantity from user input in shoppinglist display """
    main_store_key = main_store_session_key()
    other_store_keys = not_main_store_session_keys()
    st.session_state.shoppinglist[main_store_key][idx]['quantity'] = updated_quantity
    for key in other_store_keys:
        st.session_state.shoppinglist[key][idx]['quantity'] = updated_quantity


@st.dialog(title='Item Already in Shoppinglist')
def item_already_in_shoppinglist():
    """ Dialog box just to show item already in shoppinglist"""
    if st.button('Back'):
        st.rerun()


def render():
    """
    The main function to render shoppinglist page
    The price data for each selected store is in session_state with session_key:
        chain_code _ store_code: 123456789_18 - {123456789_18: price_data}
    Selected stores - in session_state with key: selected_stores -
        {'chain_code': chain_code,
        'chain_alias': chain_alias,
        'store_code': store_code,
        'store_name': store_name}
    Main store (included in selected_stores) - in session_state with key: main_store -
        {'chain_code': chain_code,
        'chain_alias': chain_alias,
        'store_code': store_code,
        'store_name': store_name}
    """
    # Setting flag if data checked
    if 'data_checked' not in st.session_state:
        st.session_state.data_checked = False

    # Check availability of data - opening dialog
    if not st.session_state['data_checked']:
        check_data()

    # Add main shoppinglist to session_state if not exist
    main_store_key = main_store_session_key()
    other_store_keys = not_main_store_session_keys()
    if 'shoppinglist' not in st.session_state:
        # dict to hold all shoppinglists
        st.session_state['shoppinglist'] = {}
        # list for main store shoppinglist
        st.session_state.shoppinglist[main_store_key] = []
        # lists for other stores shoppinglist
        for key in other_store_keys:
            st.session_state.shoppinglist[key] = []

    # Mechanism to reset quantity input to default value
    if "reset_quantity" in st.session_state and st.session_state.reset_quantity:
        st.session_state.quantity_input = 1
        st.session_state.item_selector = ''
        st.session_state.reset_quantity = False
        st.rerun()

    st.title('Prepare Shoppinglist')
    st.subheader('Add items to basket')
    st.divider()

    # Get price_data for main store
    # Set an item selector element, quantity and add button
    with st.form(key='add_item_form'):
        st.subheader(':blue[Add Item]')
        col1, col2, col3 = st.columns([0.6, 0.3, 0.1], vertical_alignment='bottom')
        with col1:
            item = item_selector(st.session_state.get(main_store_key))
        with col2:
            quantity = st.number_input(label='Quantity', min_value=0.0, step=0.5, key='quantity_input')
        with col3:
            submitted = st.form_submit_button(label='', icon=':material/add_shopping_cart:')

    if submitted and item:
        if quantity == 0:
            quantity = 1
        st.session_state['reset_quantity'] = True
        # Check item is not in shoppinglist
        if item not in [d['item'] for d in st.session_state.shoppinglist[main_store_key]]:
            add_item(item=item, quantity=quantity)
        else:
            item_already_in_shoppinglist()

    # Display shoppinglist items
    delete_idx = None
    with st.container(border=True):
        st.subheader(':blue[Shoppinglist]')
        for idx, item in enumerate(st.session_state.shoppinglist.get(main_store_key)):
            col1, col2, col3 = st.columns([0.6, 0.3, 0.1], vertical_alignment='bottom')
            with col1:
                # The value displayed - item code and item name
                st.text_input(label='not to show',
                              label_visibility='hidden',
                              key=f'{idx}_item_name_{item['item']}',
                              value=f"{item['item']} - {next(d.get('ItemName') or d.get('ItemNm') 
                                       for d in st.session_state[main_store_session_key()] 
                                       if d['ItemCode'] == item['item'])}")
            with col2:
                updated_quantity = st.number_input(label='Quantity', value=item['quantity'],
                                                   key=f'q_{item['item']}')
                if updated_quantity != item['quantity']:
                    update_quantity(idx, updated_quantity)
            with col3:
                st.button(label='', icon=':material/delete:', key=item['item'],
                          on_click=lambda i=idx: delete_item(i))

    st.write(st.session_state.shoppinglist)

    # Continue to price comparison
    if st.button('Compare Prices', key='compare_prices'):
        # Switch to price comparison page
        st.switch_page('ui/views/pricecomparison.py')


if __name__ == "__main__":
    render()

