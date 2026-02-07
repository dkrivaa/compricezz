import streamlit as st
import asyncio

from backend.services.async_runner import run_async
from backend.services.session_state_service import force_value_into_session_state
from backend.utilities.url_to_dict import data_dict
from backend.utilities.general import session_code
from backend.core.super_class import SupermarketChain


# @st.cache_data(ttl=1800)
async def fresh_price_data(chain_code: str | int, store_code: str | int, ) -> dict | None:
    """ Fetch fresh data for the given chain and store code """
    # Get the supermarket chain class from its chain code
    chain = next((c for c in SupermarketChain.registry if c.chain_code == str(chain_code)), None)
    # Get the latest price URLs for the given chain and store code
    urls = await chain.safe_prices(store_code=store_code) if chain and store_code else None
    # Use pricefull URL and cookies if available
    url = urls.get('pricefull') or urls.get('PriceFull') if urls else None
    cookies = urls.get('cookies', None) if urls else None
    # Make data dict from data in pricefull URL
    price_dict = await data_dict(url=url, cookies=cookies) if url else None
    # Clean data dict to only include dicts of items
    price_data = chain.get_price_data(price_data=price_dict) if price_dict else None
    return price_data


# @st.cache_data(ttl=1800)
async def fresh_promo_data(chain_code: str | int, store_code: str | int, ) -> dict | None:
    """ Fetch fresh data for the given chain and store code """
    # Get the supermarket chain class from its alias
    chain = next((c for c in SupermarketChain.registry if c.chain_code == str(chain_code)), None)
    # Get the latest price URLs for the given chain and store code
    urls = await chain.safe_prices(store_code=store_code) if chain and store_code else None
    # Use promofull URL and cookies if available
    url = urls.get('promofull') or urls.get('PromoFull') if urls else None
    cookies = urls.get('cookies', None) if urls else None
    # Make data dict from data in pricefull URL
    promo_dict = await data_dict(url=url, cookies=cookies) if url else None
    # Clean data dict to only include dicts of items
    promo_data = chain.get_promo_data(promo_data=promo_dict) if promo_dict else None
    return promo_data


async def shopping_data(chain_code: str | int, store_code: str | int):
    """ Get price and promo data for selected store and enter into session_state """
    # Key to store data in session_state
    session_key = session_code(chain_code=chain_code, store_code=store_code)

    try:
        async with asyncio.TaskGroup() as tg:
            price_task = tg.create_task(fresh_price_data(chain_code=chain_code, store_code=store_code))
            promo_task = tg.create_task(fresh_promo_data(chain_code=chain_code, store_code=store_code))

        price_data = price_task.result()
        promo_data = promo_task.result()

        # Enter price and promo data into session_state
        if price_data:
            force_value_into_session_state(f'{session_key}_price_data', price_data)
        else:
            raise RuntimeError("No data returned from selected chain.")
        # Enter promo data into session_state
        if promo_data:
            force_value_into_session_state(f'{session_key}_promo_data', promo_data)
    except Exception as e:
        print(f"ERROR in shopping_data: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


async def planning_data(stores_list: list[dict]):
    """
    Getting price data from all selected stores.
    Each store represented by dict:
        {chain_code: 123,
        chain_alias: some_chain_name,
        store_code: 456,
        store_name: some_store_name}
    """
    try:
        # Get price data for all selected stores
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    fresh_price_data(
                        chain_code=item['chain_code'],
                        store_code=item['store_code']
                    )
                )
                for item in stores_list
            ]
    except ExceptionGroup as e:
        pass

    # Get results of all the tasks
    results = [task.result() for task in tasks]

    # Enter price data (results) into session stage
    for idx, item in enumerate(stores_list):
        session_key = f'{item['chain_code']}_{item['store_code']}'
        st.session_state[session_key] = results[idx]
