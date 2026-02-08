import streamlit as st
import itertools
import math


def best_cost_for_k_stores(shoppinglist, k):
    """
    Calculate the best cost for shoppinglist using k stores

        store_data: {
            "StoreA": [ {item, quantity, price}, ... ],
            "StoreB": [...],
            ...
        }
        k: max number of stores to visit
    """

    stores = list(shoppinglist.keys())

    # Number of items from any store (all lists same length)
    n_items = len(next(iter(shoppinglist.values())))

    # ---- Build shopping list using QUANTITY from any store ----
    shopping_list = []
    for i in range(n_items):
        # quantity is identical across stores
        qty = shoppinglist[stores[0]][i]["quantity"]
        shopping_list.append({
            "idx": i,
            "quantity": qty
        })

    # ---- Build price maps ----
    price_maps = {
        store: {i: shoppinglist[store][i]["price"] for i in range(n_items)}
        for store in stores
    }

    best_combo = None
    best_total = math.inf
    best_plan = None

    # ---- Try store combinations ----
    for r in range(1, k + 1):
        for combo in itertools.combinations(stores, r):

            store_plan = {s: [] for s in combo}
            total_cost = 0

            for entry in shopping_list:
                idx = entry["idx"]
                qty = entry["quantity"]

                # available prices for this item index
                available = [(store, price_maps[store][idx]) for store in combo]

                # choose cheapest store
                best_store, unit_price = min(available, key=lambda x: x[1])
                cost = unit_price * qty

                # ⭐ USE THE ORIGINAL ITEM NAME FROM THE ASSIGNED STORE
                item_name = shoppinglist[best_store][idx]["item"]

                store_plan[best_store].append({
                    "item": item_name,  # original name from that store
                    "quantity": qty,
                    "unit_price": unit_price,
                    "total_price": cost
                })

                total_cost += cost

            # record best result
            if total_cost < best_total:
                best_total = total_cost
                best_combo = combo
                best_plan = store_plan

    return best_combo, best_total, best_plan


def shopping_list_with_unit_prices(shoppinglist):
    """ Add unit prices to shoppinglist entries """
    updated_list = {}
    for store, items in shoppinglist.items():
        updated_items = []
        for item in items:
            price = next(d['ItemPrice'] for d in st.session_state[store] if d['ItemCode'] == item['item'])
            updated_item = item.copy()
            updated_item["price"] = float(price)
            updated_items.append(updated_item)
        updated_list[store] = updated_items
    return updated_list


def max_stores():
    """ Get max number of stores in shoppinglist """
    return len(st.session_state['shoppinglist'].keys())


def total_per_store(shoppinglist):
    """ Calculate total cost per store """
    totals = {}
    for store, items in shoppinglist.items():
        total = sum(item['quantity'] * item['price'] for item in items)
        totals[store] = total
    return totals


def from_key_to_store_name(key):
    """ Convert session key to chain, store name """
    chain = next(d['chain_alias'] for d in st.session_state['selected_stores']
                 if d['chain_code'] == key.split('_')[0])
    store = next(d['store_name'] for d in st.session_state['selected_stores']
                 if d['chain_code'] == key.split('_')[0] and d['store_code'] == key.split('_')[1])
    return f'{chain} - {store}'


def render():
    """ Render the price comparison view """
    st.title('Price Comparison')
    st.divider()

    # Get shoppinglist from session state
    shoppinglist = st.session_state.get('shoppinglist', {})
    # Add unit prices to shoppinglist entries
    updated_shoppinglist = shopping_list_with_unit_prices(shoppinglist)

    tab1, tab2 = st.tabs(['Total per Store', 'Save the Most'])

    with tab1:
        # Display total per store
        totals = total_per_store(updated_shoppinglist)
        for key, value in totals.items():
            st.metric(
                label=from_key_to_store_name(key),
                value=f"₪ {value:.2f}"
            )

    with tab2:
        # Find best cost for k stores
        k = st.slider(
            label='Max Number of Stores to Visit',
            min_value=1,
            max_value=max_stores(),
            value=2,
            step=1
        )

        # Get best combination, total cost and shopping plan for each of k stores
        best_combo, best_total, best_plan = best_cost_for_k_stores(updated_shoppinglist, k=k)
        st.write(best_combo)
        st.subheader('Visit:')
        for store in best_combo:
            st.write(from_key_to_store_name(store))

        st.divider()

        st.write(best_total)
        st.metric(
            label='Total Cost',
            value=f"₪ {best_total:.2f}",
            delta=f"₪ {total_per_store(updated_shoppinglist)[best_combo[0]] - best_total:.2f} saved"
        )

        st.divider()
        st.write(best_plan)
        for store in best_combo:
            st.subheader(from_key_to_store_name(store))
            for item in best_plan[store]:
                st.write(st.session_state[store])
                # item_name = next(d.get('ItemName') or d.get('ItemNm') for d in st.session_state[store]
                #                             if d['ItemCode'] == item)
                st.write(f"{item['item']} - {item_name}: {item['quantity']} x ₪ {item['unit_price']:.2f} = ₪ {item['total_price']:.2f}")


if __name__ == "__main__":
    render()



