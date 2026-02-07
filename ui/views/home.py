import streamlit as st


def render():
    """ Main render function for home page """
    st.title('Welcome')
    st.divider()

    # Select what to do - Shop or Plan
    i_want_to = st.radio(
        label='I want to:',
        options=['SHOP', 'PLAN'],
        index=None,
        width='stretch'
        )

    if i_want_to == 'SHOP':
        st.switch_page('ui/views/shop.py')

    if i_want_to == 'PLAN':
        st.switch_page('ui/views/plan.py')


if __name__ == "__main__":
    render()
