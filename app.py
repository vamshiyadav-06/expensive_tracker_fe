import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Expense Management System")

# =====================================
# BACKEND URL
# =====================================

local_server = "https://expensive-track-backend.onrender.com"

# =====================================
# API REQUEST FUNCTION
# =====================================

def make_request(method, endpoint, data=None):

    url = f"{local_server}{endpoint}"

    try:
        if method == "GET":
            res = requests.get(url, timeout=60)

        elif method == "POST":
            res = requests.post(
                url,
                json=data,
                timeout=60
            )

        elif method == "PUT":
            res = requests.put(
                url,
                json=data,
                timeout=60
            )

        elif method == "DELETE":
            res = requests.delete(
                url,
                timeout=60
            )

        if res.status_code != 200:
            st.error(
                f"Backend Error: {res.status_code}"
            )
            st.write(res.text)
            return None

        try:
            return res.json()

        except:
            st.error(
                "Backend is waking up. "
                "Wait 30 seconds and retry."
            )
            return None

    except requests.exceptions.Timeout:
        st.error(
            "Server timeout. Render may be waking up."
        )
        return None

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


# =====================================
# SIDEBAR
# =====================================

opt = st.sidebar.selectbox(
    "Choose Operation",
    [
        "add_expenses",
        "update_expenses",
        "view_expenses",
        "delete_expenses",
        "search_expenses",
        "sort_expenses",
        "filter_expenses",
        "analyze_expenses"
    ]
)

# =====================================
# ADD EXPENSE
# =====================================

if opt == "add_expenses":

    st.header("➕ Add Expense")

    with st.form("adding_expense"):

        category = st.selectbox(
            "📂 Category",
            [
                "",
                "Food 🍔",
                "Travel ✈️",
                "Shopping 🛍️",
                "Bills 💡",
                "Entertainment 🎬",
                "Health 🏥",
                "Education 📚",
                "Others 📦"
            ]
        )

        amount = st.number_input(
            "💰 Amount",
            min_value=0.0
        )

        payment_method = st.selectbox(
            "💳 Payment Method",
            [
                "",
                "Cash 💵",
                "UPI 📲",
                "Credit Card 💳",
                "Debit Card 🏦",
                "Net Banking 🌐"
            ]
        )

        expense_date = st.date_input(
            "📅 Expense Date"
        )

        description = st.text_area(
            "📝 Description"
        )

        btn = st.form_submit_button(
            "➕ Add Expense"
        )

        if btn:

            if (
                category == ""
                or amount == 0
                or payment_method == ""
            ):
                st.warning(
                    "Please fill all required fields"
                )

            else:

                payload = {
                    "category": category,
                    "amount": amount,
                    "payment_method": payment_method,
                    "expense_date": str(expense_date),
                    "description": description
                }

                response = make_request(
                    "POST",
                    "/add_expense",
                    payload
                )

                if response:
                    st.success(
                        response.get(
                            "msg",
                            "Expense Added"
                        )
                    )

# =====================================
# UPDATE EXPENSE
# =====================================

elif opt == "update_expenses":

    st.header("✏️ Update Expense")

    if "expense_data" not in st.session_state:
        st.session_state.expense_data = None

    expense_id = st.number_input(
        "Expense ID",
        min_value=1,
        step=1
    )

    if st.button("Fetch Expense"):

        response = make_request(
            "GET",
            f"/get_single_expense/{expense_id}"
        )

        if (
            response
            and response.get("expense_data")
        ):

            exp = response["expense_data"]

            st.session_state.expense_data = {
                "category": exp[1],
                "amount": float(exp[2]),
                "payment_method": exp[3],
                "expense_date": str(exp[4]),
                "description": exp[5]
            }

            st.success(
                "Expense Loaded"
            )

        else:
            st.warning(
                "Expense not found"
            )

    if st.session_state.expense_data:

        exp = st.session_state.expense_data

        category = st.text_input(
            "Category",
            exp["category"]
        )

        amount = st.number_input(
            "Amount",
            value=exp["amount"]
        )

        payment_method = st.text_input(
            "Payment Method",
            exp["payment_method"]
        )

        expense_date = st.text_input(
            "Expense Date",
            exp["expense_date"]
        )

        description = st.text_area(
            "Description",
            exp["description"]
        )

        if st.button("Update Expense"):

            payload = {
                "category": category,
                "amount": amount,
                "payment_method":
                payment_method,
                "expense_date":
                expense_date,
                "description":
                description
            }

            response = make_request(
                "PUT",
                f"/update_expense/{expense_id}",
                payload
            )

            if response:
                st.success(
                    response.get(
                        "updated_msg",
                        "Expense Updated"
                    )
                )

# =====================================
# VIEW EXPENSES
# =====================================

elif opt == "view_expenses":

    st.header("📋 View Expenses")

    if st.button("View Expenses"):

        response = make_request(
            "GET",
            "/get_all_expenses"
        )

        if response:

            data = response.get(
                "all_expenses",
                []
            )

            df = pd.DataFrame(
                data,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment",
                    "Date",
                    "Description"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

# =====================================
# DELETE EXPENSE
# =====================================

elif opt == "delete_expenses":

    st.header("🗑️ Delete Expense")

    expense_id = st.number_input(
        "Expense ID",
        min_value=1,
        step=1
    )

    if st.button("Delete"):

        response = make_request(
            "DELETE",
            f"/delete_expense/{expense_id}"
        )

        if response:
            st.success(
                response.get(
                    "msg",
                    "Deleted Successfully"
                )
            )

# =====================================
# SEARCH EXPENSES
# =====================================

elif opt == "search_expenses":

    st.header("🔍 Search Expense")

    search_text = st.text_input(
        "Search"
    )

    if st.button("Search"):

        response = make_request(
            "GET",
            f"/view_exp/{search_text}"
        )

        if response:

            data = response.get(
                "search_result",
                []
            )

            df = pd.DataFrame(
                data,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment",
                    "Date",
                    "Description"
                ]
            )

            st.dataframe(df)

# =====================================
# SORT EXPENSES
# =====================================

elif opt == "sort_expenses":

    st.header("📊 Sort Expenses")

    column = st.selectbox(
        "Sort By",
        [
            "Title",
            "Amount",
            "Category"
        ]
    )

    order = st.selectbox(
        "Order",
        [
            "Asc",
            "Desc"
        ]
    )

    if st.button("Sort"):

        response = make_request(
            "GET",
            f"/sort_exp/{column}/{order}"
        )

        if response:

            data = response.get(
                "sorted_expenses",
                []
            )

            df = pd.DataFrame(
                data,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment",
                    "Date",
                    "Description"
                ]
            )

            st.dataframe(df)

# =====================================
# FILTER EXPENSES
# =====================================

elif opt == "filter_expenses":

    st.header("📂 Filter Expense")

    category = st.selectbox(
        "Category",
        [
            "Food 🍔",
            "Travel ✈️",
            "Shopping 🛍️",
            "Bills 💡",
            "Entertainment 🎬",
            "Health 🏥",
            "Education 📚",
            "Others 📦"
        ]
    )

    if st.button("Filter"):

        response = make_request(
            "GET",
            f"/filter_exp/{category}"
        )

        if response:

            data = response.get(
                "filtered_expenses",
                []
            )

            df = pd.DataFrame(
                data,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment",
                    "Date",
                    "Description"
                ]
            )

            st.dataframe(df)

# =====================================
# ANALYZE EXPENSES
# =====================================

elif opt == "analyze_expenses":

    st.header("📈 Expense Analysis")

    if st.button("Analyze"):

        response = make_request(
            "GET",
            "/analyze_spending"
        )

        if response:

            total = response[
                "total_spending"
            ]["total"]

            category_data = response[
                "category_spending"
            ]

            st.success(
                f"💰 Total Spending: ₹{total}"
            )

            df = pd.DataFrame(
                category_data
            )

            fig = px.bar(
                df,
                x="category",
                y="total",
                title="Category Spending"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            fig2 = px.pie(
                df,
                names="category",
                values="total",
                title="Expense Distribution"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )