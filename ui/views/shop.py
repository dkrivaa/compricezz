import streamlit as st
from backend.services.async_runner import run_async
from backend.services.session_state_service import force_value_into_session_state
from backend.services.error_service import no_data_error
from backend.pipelines.fresh_price_promo import shopping_data
from ui.common_elements import chain_selector, store_selector


def render():
    """ The main function to render SHOP page """
    st.title('SHOP')
    st.subheader('Check Prices and Discounts')
    st.divider()

    with st.container():
        # Select supermarket chain
        chain_code, _ = chain_selector()

        if chain_code:
            # Enter chain_code into session_state
            force_value_into_session_state('chain_code', chain_code)
            # Select store
            if 'store_code' not in st.session_state:
                with st.spinner('Loading Stores...'):
                    store_code, _ = store_selector(chain_code=chain_code)
            else:
                store_code = st.session_state['store_code']

            if store_code:
                # Enter store_code into session_state
                force_value_into_session_state('store_code', store_code)

                with st.spinner('Loading Data, One Moment.....'):
                    try:
                        # Get price and promo data for selected store and enter into session_state
                        run_async(shopping_data, chain_code=chain_code, store_code=store_code)
                        # Go to item details page
                        st.switch_page('ui/views/item.py')
                    # Price_data = None
                    except RuntimeError as e:
                        no_data_error('RuntimeError')
                    # Price_data not the right type (got error result)
                    except TypeError:
                        no_data_error('TypeError')
                    # No access to site
                    except KeyError:
                        no_data_error('KeyError')


if __name__ == "__main__":
    render()
