import streamlit as st
import numpy as np
import plotly.graph_objects as go

# App title
st.title('3-Slope Jump Rate Interest Model')

# Input fields for the parameters with appropriate formatting and default values
base_rate = st.number_input('Base Borrow Rate', format="%.10e", value=0.0)
low_slope = st.number_input('Low Slope', format="%.10e", value=0.0)
first_jump_slope = st.number_input('First Jump Slope', format="%.10e", value=1.5854895990e-9)
second_jump_slope = st.number_input('Second Jump Slope', format="%.10e", value=3.4563673262e-8)
reserve_factor = st.number_input('Reserve Factor (%)', value=5.0)

# Sliders for the kinks (utilization points) with default values
first_kink = st.slider('First Kink (%)', min_value=0, max_value=100, value=5)
second_kink = st.slider('Second Kink (%)', min_value=0, max_value=100, value=85)

# Function to calculate borrow and supply rates with APR (annual percentage rates)
def calculate_rates(base_rate, low_slope, first_jump_slope, second_jump_slope, first_kink, second_kink, reserve_factor):
    utilization = np.linspace(0, 100, 100)
    borrow_rates = []
    supply_rates = []
    borrow_aprs = []
    supply_aprs = []

    for U in utilization:
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

        # Ensure borrow rate is non-negative
        borrow_rate = max(0, borrow_rate)

        # Calculate supply rate based on borrow rate
        supply_rate = borrow_rate * (U / 100) * (1 - reserve_factor / 100)

        # Calculate APR (annualized percentage rate)
        borrow_apr = borrow_rate * 31536000  # Seconds in a year
        supply_apr = supply_rate * 31536000

        borrow_rates.append(borrow_rate)
        supply_rates.append(supply_rate)
        borrow_aprs.append(borrow_apr)
        supply_aprs.append(supply_apr)

    return utilization, borrow_rates, supply_rates, borrow_aprs, supply_aprs

# Button to trigger the calculation and plot
if st.button('Calculate Rates'):
    utilization, borrow_rates, supply_rates, borrow_aprs, supply_aprs = calculate_rates(
        base_rate, low_slope, first_jump_slope, second_jump_slope,
        first_kink, second_kink, reserve_factor
    )

    # Create an interactive plot with Plotly
    fig = go.Figure()

    # Add borrow rate trace with hover displaying APR and rate
    fig.add_trace(go.Scatter(
        x=utilization, y=borrow_rates,
        mode='lines',  # Only lines, no markers
        name='Borrow Rates',
        hovertemplate="Borrow Rate: %{y:.2e}<br>Borrow APR: %{customdata:.2f}%",
        customdata=borrow_aprs  # Pass APR as custom data
    ))

    # Add supply rate trace with hover displaying APR and rate
    fig.add_trace(go.Scatter(
        x=utilization, y=supply_rates,
        mode='lines',  # Only lines, no markers
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