import streamlit as st


def render():
    """ Main render function for home page """
    st.title('Welcome')
    st.divider()

    with st.container():
        # Select what to do - Shop or Plan
        if st.button(
            label='SHOP - Check Prices and Discounts',
            width='stretch',
            key='shop_button'
        ):
            st.switch_page('ui/views/shop.py')

        if st.button(
            label='PLAN - Make Shoppinglist and Compare Prices',
            width='stretch',
            key='plan_button'
        ):
            st.switch_page('ui/views/plan.py')


if __name__ == "__main__":
    render()
