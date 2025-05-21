import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pathlib
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_order_items_df(df):
    products_orders_df = df.groupby("product_category_name_english").order_id.count().sort_values(
        ascending=False).reset_index()
    products_orders_df.rename(
        columns={
            'product_category_name_english': 'product_category', 
            'order_id': 'order_total'
            }, inplace=True)
    
    return products_orders_df

def create_bystate_df(df):
    customers_states_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    customers_states_df.rename(
        columns={
            "customer_state": "state", 
            "customer_unique_id": "customer_count"
            }, inplace=True)
    
    return customers_states_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_label", as_index=False).agg({
    "order_purchase_timestamp": "max", # get last date order
    "order_id": "nunique", # count total order
    "price": "sum" # count revenue total
    })
    rfm_df.columns = ["customer_label", "max_order_timestamp", "frequency", "monetary"]
    
    # calculate the last day customer made a transaction
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    rfm_df.head()
    
    return rfm_df

csv_path = pathlib.Path("dashboard") / "main_data.csv"
all_df = pd.read_csv(csv_path)

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # # Menambahkan logo perusahaan
    # st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Period',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('E-Commerce Order Dashboard :sparkles:')

# Which Product has the most and the least sells?
st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_total", y="product_category", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Orders", fontsize=45)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_total", y="product_category", data=sum_order_items_df.sort_values(by="order_total", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Orders", fontsize=45)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

# How are the demographics of our customers?
st.subheader("Customer Demographics")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# When was the last time the customer made a transaction?
# How often has a customer made a purchase in the last few months?
# How much money have customers spent in the last few months?
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_label", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_label", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, labelrotation=45)
 
sns.barplot(y="frequency", x="customer_label", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_label", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, labelrotation=45)
 
sns.barplot(y="monetary", x="customer_label", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_label", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, labelrotation=45)
 
st.pyplot(fig)