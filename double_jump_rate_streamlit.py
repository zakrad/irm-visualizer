import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title('2-Slope and 3-Slope Jump Rate Interest Models')

# Model type selection
model_type = st.radio("Select Interest Rate Model", ('2-Slope', '3-Slope'))

base_rate = st.number_input('Base Borrow Rate', format="%.10e", value=0.0)
reserve_factor = st.number_input('Reserve Factor (%)', value=5.0)

if model_type == '3-Slope':
    low_slope = st.number_input('Low Slope (3-Slope)', format="%.10e", value=0.0)
    first_jump_slope = st.number_input('First Jump Slope (3-Slope)', format="%.10e", value=1.5854895990e-9)
    second_jump_slope = st.number_input('Second Jump Slope (3-Slope)', format="%.10e", value=3.4563673262e-8)
    first_kink = st.slider('First Kink (%) (3-Slope)', min_value=0, max_value=100, value=5)
    second_kink = st.slider('Second Kink (%) (3-Slope)', min_value=0, max_value=100, value=85)
else:
    low_slope = st.number_input('Low Slope (2-Slope)', format="%.10e", value=1.5854895990e-9)
    jump_slope = st.number_input('Jump Slope (2-Slope)', format="%.10e", value=3.4563673262e-8)
    kink = st.slider('Kink (%) (2-Slope)', min_value=0, max_value=100, value=80)

# Function to calculate borrow and supply rates
def calculate_rates(base_rate, low_slope, jump_slope=None, first_jump_slope=None, second_jump_slope=None, first_kink=None, second_kink=None, reserve_factor=0, model_type='2-Slope'):
    utilization = np.linspace(0, 100, 100)
    borrow_rates = []
    supply_rates = []
    borrow_aprs = []
    supply_aprs = []

    for U in utilization:
        if model_type == '3-Slope':
            if U <= first_kink:
                borrow_rate = base_rate + (U * low_slope)
            elif U <= second_kink:
                normal_rate = base_rate + (first_kink * low_slope)
                excess_util = U - first_kink
                borrow_rate = normal_rate + (excess_util * first_jump_slope)
            else:
                normal_rate = base_rate + (first_kink * low_slope)
                normal_rate += (second_kink - first_kink) * first_jump_slope
                excess_util = U - second_kink
                borrow_rate = normal_rate + (excess_util * second_jump_slope)
        else:
            if U <= kink:
                borrow_rate = base_rate + (U * low_slope)
            else:
                normal_rate = base_rate + (kink * low_slope)
                excess_util = U - kink
                borrow_rate = normal_rate + (excess_util * jump_slope)

        borrow_rate = max(0, borrow_rate)

        supply_rate = borrow_rate * (U / 100) * (1 - reserve_factor / 100)

        # Calculate APR (annual percentage rate)
        borrow_apr = borrow_rate * 31536000  # Seconds in a year
        supply_apr = supply_rate * 31536000

        borrow_rates.append(borrow_rate)
        supply_rates.append(supply_rate)
        borrow_aprs.append(borrow_apr)
        supply_aprs.append(supply_apr)

    return utilization, borrow_rates, supply_rates, borrow_aprs, supply_aprs

if st.button('Calculate Rates'):
    if model_type == '3-Slope':
        utilization, borrow_rates, supply_rates, borrow_aprs, supply_aprs = calculate_rates(
            base_rate, low_slope, first_jump_slope=first_jump_slope, second_jump_slope=second_jump_slope,
            first_kink=first_kink, second_kink=second_kink, reserve_factor=reserve_factor, model_type=model_type
        )
    else:
        utilization, borrow_rates, supply_rates, borrow_aprs, supply_aprs = calculate_rates(
            base_rate, low_slope, jump_slope=jump_slope, reserve_factor=reserve_factor, model_type=model_type
        )

    fig = go.Figure()

    # Add borrow rate trace with hover displaying APR and rate
    fig.add_trace(go.Scatter(
        x=utilization, y=borrow_rates,
        mode='lines+markers',
        name='Borrow Rates',
        hovertemplate="Borrow Rate: %{y:.2e}<br>Borrow APR: %{customdata:.2f}%",
        customdata=borrow_aprs  # Pass APR as custom data
    ))

    # Add supply rate trace with hover displaying APR and rate
    fig.add_trace(go.Scatter(
        x=utilization, y=supply_rates,
        mode='lines+markers',
        name='Supply Rates',
        hovertemplate="Supply Rate: %{y:.2e}<br>Supply APR: %{customdata:.2f}%",
        customdata=supply_aprs  # Pass APR as custom data
    ))

    # Update plot layout
    fig.update_layout(
        title="Borrow and Supply Rates with APR",
        xaxis_title="Utilization (%)",
        yaxis_title="Rate",
        hovermode="x",
        legend=dict(x=0, y=1)
    )

    # Display the plot
    st.plotly_chart(fig)