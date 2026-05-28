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

local_server = st.secrets["server_url"]

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

        try:
            response = res.json()
        except:
            response = {}

        # HTTP ERROR
        if res.status_code != 200:
            st.error(
                f"Backend Error: {res.status_code}"
            )
            st.write(response)
            return None

        # CUSTOM BACKEND ERROR
        if (
            isinstance(response, dict)
            and "error" in response
        ):
            st.error(
                f"❌ {response['error']}"
            )
            return None

        return response

    except requests.exceptions.Timeout:

        st.error(
            "Server timeout. "
            "Render may be sleeping."
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
        "analyze_expenses"
    ]
)


# =====================================
# ADD EXPENSE
# =====================================

elif opt == "add_expenses":

    st.header("➕ Add Expense")

    with st.form("adding_expense"):

        category = st.selectbox(
            "📂 Category",
            [
                "",
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Entertainment",
                "Health",
                "Education",
                "Others"
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
                "Cash",
                "UPI",
                "Credit Card",
                "Debit Card",
                "Net Banking"
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
                    "Fill all required fields"
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
# VIEW EXPENSES
# =====================================

elif opt == "view_expenses":

    st.header("📋 View Expenses")

    if st.button(
        "View Expenses"
    ):

        response = make_request(
            "GET",
            "/get_all_expenses"
        )

        if response:

            data = response.get(
                "all_expenses",
                []
            )

            if len(data) == 0:

                st.warning(
                    "No expenses found"
                )

            else:

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
# SEARCH EXPENSE
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
# ANALYZE EXPENSES
# =====================================

elif opt == "analyze_expenses":

    st.header("📈 Expense Analysis")

    if st.button("Analyze"):

        response = make_request(
            "GET",
            "/analyze_spending"
        )

        if not response:
            st.stop()

        total = response.get(
            "total_spending",
            {}
        ).get("total", 0)

        category_data = response.get(
            "category_spending",
            []
        )

        st.success(
            f"💰 Total Spending: ₹{total}"
        )

        if len(category_data) == 0:

            st.warning(
                "No expense data found"
            )

        else:

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