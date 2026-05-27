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

# Local
# local_server = "http://localhost:8000"

# Render URL (change later)
local_server = "http://localhost:8000"


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
            "📂 Select Category",
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
            "💵 Enter Amount",
            min_value=0.0,
            step=1.0
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

        btn = st.form_submit_button("➕ Add Expense")

        if btn:

            if (
                category == ""
                or amount == 0
                or payment_method == ""
            ):
                st.warning("⚠️ Please fill all required details")

            else:

                new_data = {
                    "category": category,
                    "amount": amount,
                    "payment_method": payment_method,
                    "expense_date": str(expense_date),
                    "description": description
                }

                try:
                    res = requests.post(
                        f"{local_server}/add_expense",
                        json=new_data
                    )

                    response = res.json()

                    if "msg" in response:
                        st.success(response["msg"])
                    else:
                        st.error(response["error"])

                except Exception as e:
                    st.error(f"❌ Error: {e}")


# =====================================
# UPDATE EXPENSE
# =====================================

elif opt == "update_expenses":

    st.header("✏️ Update Expense")

    if "expense_data" not in st.session_state:
        st.session_state.expense_data = None

    expense_id = st.number_input(
        "🆔 Enter Expense ID",
        min_value=1,
        step=1
    )

    if st.button("📥 Fetch Expense"):

        try:

            res = requests.get(
                f"{local_server}/get_single_expense/{expense_id}"
            )

            data = res.json()

            if data["expense_data"]:

                exp = data["expense_data"]

                st.session_state.expense_data = {
                    "category": exp[1],
                    "amount": float(exp[2]),
                    "payment_method": exp[3],
                    "expense_date": str(exp[4]),
                    "description": exp[5]
                }

                st.success("✅ Expense Loaded")

            else:
                st.warning("Expense not found")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    if st.session_state.expense_data:

        exp = st.session_state.expense_data

        category = st.text_input(
            "📂 Category",
            value=exp["category"]
        )

        amount = st.number_input(
            "💰 Amount",
            value=exp["amount"]
        )

        payment_method = st.text_input(
            "💳 Payment Method",
            value=exp["payment_method"]
        )

        expense_date = st.text_input(
            "📅 Expense Date",
            value=exp["expense_date"]
        )

        description = st.text_area(
            "📝 Description",
            value=exp["description"]
        )

        if st.button("🔄 Update Expense"):

            updated_data = {
                "c": category,
                "a": amount,
                "p": payment_method,
                "e": expense_date,
                "d": description
            }

            try:

                res = requests.put(
                    f"{local_server}/update_expense/{expense_id}",
                    json=updated_data
                )

                response = res.json()

                if "updated_msg" in response:
                    st.success(response["updated_msg"])
                else:
                    st.error(response["error"])

            except Exception as e:
                st.error(f"❌ Error: {e}")


# =====================================
# VIEW EXPENSES
# =====================================

elif opt == "view_expenses":

    st.header("📋 View Expenses")

    if st.button("View All Expenses"):

        try:

            res = requests.get(
                f"{local_server}/get_all_expenses"
            )

            data = res.json()

            all_expenses = data["all_expenses"]

            df = pd.DataFrame(
                all_expenses,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment Method",
                    "Expense Date",
                    "Description"
                ]
            )

            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")


# =====================================
# DELETE EXPENSE
# =====================================

elif opt == "delete_expenses":

    st.header("🗑️ Delete Expense")

    expense_id = st.number_input(
        "Enter Expense ID",
        min_value=1,
        step=1
    )

    if st.button("Delete Expense"):

        try:

            res = requests.delete(
                f"{local_server}/delete_expense/{expense_id}"
            )

            response = res.json()

            if "msg" in response:
                st.success(response["msg"])
            else:
                st.error(response["error"])

        except Exception as e:
            st.error(f"❌ Error: {e}")


# =====================================
# SEARCH EXPENSES
# =====================================

elif opt == "search_expenses":

    st.header("🔍 Search Expenses")

    search_text = st.text_input(
        "Enter Category or Description"
    )

    if st.button("Search"):

        try:

            res = requests.get(
                f"{local_server}/view_exp/{search_text}"
            )

            data = res.json()

            search_result = data["search_result"]

            df = pd.DataFrame(
                search_result,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment Method",
                    "Expense Date",
                    "Description"
                ]
            )

            if df.empty:
                st.warning("No matching expenses found")
            else:
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")


# =====================================
# SORT EXPENSES
# =====================================

elif opt == "sort_expenses":

    st.header("📊 Sort Expenses")

    sort_column = st.selectbox(
        "Select Column",
        ["Title", "Amount", "Category"]
    )

    sort_order = st.selectbox(
        "Sort Order",
        ["Asc", "Desc"]
    )

    if st.button("Sort"):

        try:

            res = requests.get(
                f"{local_server}/sort_exp/{sort_column}/{sort_order}"
            )

            data = res.json()

            sorted_data = data["sorted_expenses"]

            df = pd.DataFrame(
                sorted_data,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment Method",
                    "Expense Date",
                    "Description"
                ]
            )

            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")


# =====================================
# FILTER EXPENSES
# =====================================

elif opt == "filter_expenses":

    st.header("📂 Filter Expenses")

    selected_category = st.selectbox(
        "Select Category",
        [
            "Food 🍔",
            "Travel ✈️",
            "Bills 💡",
            "Entertainment 🎬",
            "Health 🏥",
            "Shopping 🛍️",
            "Education 📚",
            "Others 📦"
        ]
    )

    if st.button("Filter"):

        try:

            res = requests.get(
                f"{local_server}/filter_exp/{selected_category}"
            )

            data = res.json()

            filtered_data = data["filtered_expenses"]

            df = pd.DataFrame(
                filtered_data,
                columns=[
                    "ID",
                    "Category",
                    "Amount",
                    "Payment Method",
                    "Expense Date",
                    "Description"
                ]
            )

            if df.empty:
                st.warning("No expenses found")
            else:
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")


# =====================================
# ANALYZE EXPENSES
# =====================================

elif opt == "analyze_expenses":

    st.header("📈 Expense Analysis")

    if st.button("Show Analysis"):

        try:

            res = requests.get(
                f"{local_server}/analyze_spending"
            )

            data = res.json()

            total = data["total_spending"]["total"]

            category_data = data["category_spending"]

            st.success(
                f"💰 Total Spending: ₹{total}"
            )

            df = pd.DataFrame(category_data)

            # Bar Chart
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

            # Pie Chart
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

            st.dataframe(df)

        except Exception as e:
            st.error(f"❌ Error: {e}")