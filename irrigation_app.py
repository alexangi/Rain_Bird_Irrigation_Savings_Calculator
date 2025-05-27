import streamlit as st
import matplotlib
import os
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np
from datetime import date

# Import the translations from the external file
from irrigation_app_translations import TRANSLATIONS

# Choose good Unicode-aware system fonts as fallbacks
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False  # For minus sign display

# ---------- TEXT SANITIZER FOR PDF ----------
def latin1_sanitize(text):
    return (
        str(text)
        .replace('₂', '2')  # Handle subscript 2 character
        .replace('–', '-')  # Handle en dash
        .replace('—', '-')  # Handle em dash
        .replace('→', '->')  # Handle arrow
        .replace('"', '"')   # Handle quotes
        .replace('“', '"')   # Handle left quote
        .replace('”', '"')   # Handle right quote
        .replace('‘', "'")   # Handle left single quote
        .replace('’', "'")   # Handle right single quote
        .replace('…', '...')  # Handle ellipsis
    )


# ---------- PAGE CONFIG (Must be first Streamlit command) ----------
st.set_page_config(
    page_title="Irrigation Savings Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

def info_icon(label_key, labels):
    """Returns an info icon with a localized tooltip based on the label key and translations."""
    return f"""<span style="cursor: help; color: #00703c;" title="{labels.get(label_key, '')}">🛈</span>"""


def apply_styles():
    css = """
    <style>
        /* Global Styles */
        html, body, .stApp {
            margin: 0;
            padding: 0;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #f4f6f9;
            color: #000 !important;
            font-family: 'DejaVu Sans'!important;
        }
        /* Sidebar Styles */
        section[data-testid='stSidebar'] {
            background: #004d24 !important;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            padding: 24px 28px !important;
            border-right: 1px solid rgba(0,0,0,0.1);
            color: white !important;
        }
        /* Label Styling for Sidebar */
        section[data-testid='stSidebar'] .stTextInput label,
        section[data-testid='stSidebar'] .stSelectbox label,
        section[data-testid='stSidebar'] .stNumberInput label,
        section[data-testid='stSidebar'] .stSlider label {
            color: white !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        /* Label Styling for Main Content */
        .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
            color: black !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        /* Button Styling */
        .stButton>button, .stDownloadButton>button {
            background-color: #00703c !important;
            color: #FFFFFF !important;
            width: 100% !important;
            padding: 12px;
            font-size: 16px !important;
            border-radius: 8px;
        }
        /* Footer Styles */
        .footer {
            background-color: #f1f1f1;
            padding: 15px;
            text-align: center;
            font-size: 13px;
            color: #444;
            margin-top: auto;
        }
    @media print {
        html, body, .stApp, .block-container, .main, .appview-container {
            zoom: 95% !important;    /* Most browsers (Chrome, Edge, Brave, Opera, etc.) */
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 1000px !important;
            background: #fff !important;
            box-sizing: border-box !important;
            overflow: visible !important;

        }
        /* Stack columns vertically for print */
        .stColumns {
            display: block !important;
        }
        .stColumn {
            width: 100% !important;
            display: block !important;
            position: static !important;
        }    
        /* Hide ALL columns except 2 */
        .stColumn:not(:nth-of-type(2)) {
            display: none !important;
        }
        /* Sidebar: 300px left */
        section[data-testid="stSidebar"] {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 300px !important;
            min-width: 300px !important;
            max-width: 300px !important;
            background: #004d24 !important;
            color: #fff !important;
            padding: 24px 16px 24px 24px !important;
            border-right: 1px solid #e0e0e0 !important;
            box-sizing: border-box !important;
            z-index: 10;
            overflow-wrap: break-word !important;
            overflow: visible !important;

        }
        /* Main content (column 2): 900px right */
        .stColumn:nth-of-type(2) {
            position: absolute !important;
            left: 300px !important;
            top: 0 !important;
            width: 900px !important;
            min-width: 900px !important;
            max-width: 900px !important;
            background: #fff !important;
            color: #000 !important;
            padding: 12px 8px 12px 12px !important;
            box-sizing: border-box !important;
            z-index: 10;
            overflow-wrap: break-word !important;
            overflow: visible !important;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Sidebar content with dynamic translation values
    st.sidebar.image(
        "https://www.rainbird.com/sites/default/files/RainBirdLogo_330x100.png",  # Rain Bird logo
        use_container_width=True
    )

    # Ensure dynamic translation replacement here
    st.sidebar.markdown(
        f"""
        <div class='section-title'>
        <p style="font-size: 24px;">
            {TRANSLATIONS[st.session_state.lang]['irrigation_savings_calculator']}
        </p>
        </div>
        <p style="font-size: 14px;">
            {TRANSLATIONS[st.session_state.lang]['tool_description']}
        </p>
        """,
        unsafe_allow_html=True
    )

    # Insert the image in between the two text sections
    st.sidebar.image(
        "https://www.rainbird.com/sites/default/files/styles/scaled_1400x1400/public/media/images/2022-10/weather-header-mobile.jpg?itok=69uXfYo9",  # Path to the uploaded image
        use_container_width=True
    )

    # Detailed Description and Link with dynamic translations
    st.sidebar.markdown(
        f"""
        <p style="font-size: 14px;">
            {TRANSLATIONS[st.session_state.lang]['evapotranspiration_description']}
        </p>
        <p style="font-size: 14px; color: #ffffff;">
            <a href="{TRANSLATIONS[st.session_state.lang]['learn_more_link']}" target="_blank" style="color: white;">{TRANSLATIONS[st.session_state.lang]['learn_more_text']}</a>
        </p>
        """,
        unsafe_allow_html=True
    )

# ---------- CONSTANTS ----------
ET_DATA = {
    "Bangkok": 1280,
    "Jakarta": 1135,
    "Kuala Lumpur": 1300,
    "Manila": 1370,
    "Singapore": 1200,
    "Hanoi": 1300,
    "Ho Chi Minh City": 1500,
    "Tokyo": 1100,
    "Seoul": 1050,
    "Dubai": 2100,
    "Mexico City": 950,
    "São Paulo": 1250,
    "Buenos Aires": 1000,
    "Beijing": 980,
    "Shanghai": 1050,
    "Guangzhou": 1150,
    "Shenzhen": 1200,
    "Chengdu": 1000,
    "Wuhan": 1020,
    "Xi'an": 970,
    "Hangzhou": 1100,
    "Nanjing": 1080,
    "Tianjin": 990
}
UNIT_MULTIPLIERS = {"m²": 1, "Rai": 1600, "Hectare": 10000, "Acre": 4046.86}
EXCHANGE_RATES_FALLBACK = {
    'MXN': 0.5,
    'BRL': 0.19,
    'ARS': 25.0,
    'JPY': 4.5,
    'KRW': 38.0,
    'AED': 0.1,
    'USD': 0.029, 
    'SGD': 0.038, 
    'THB': 1.0, 
    'VND': 735.0, 
    'IDR': 420.0, 
    'PHP': 1.5
}

# Define the construction cost coefficients for each city
updated_city_coefficients_reviewed = {
    "Bangkok": 1.0,
    "Jakarta": 0.9,
    "Kuala Lumpur": 1.1,
    "Manila": 1.3,
    "Singapore": 1.6,
    "Hanoi": 0.8,
    "Ho Chi Minh City": 1.0,
    "Tokyo": 2.2,
    "Seoul": 1.8,
    "Dubai": 2.5,
    "Mexico City": 0.9,
    "São Paulo": 1.2,
    "Buenos Aires": 0.9,
    "Beijing": 1.6,
    "Shanghai": 1.7,
    "Guangzhou": 1.5,
    "Shenzhen": 1.5,
    "Chengdu": 1.3,
    "Wuhan": 1.2,
    "Xi'an": 1.1,
    "Hangzhou": 1.5,
    "Nanjing": 1.4,
    "Tianjin": 1.3
}



# ---------------------------- Initialize Session State ----------------------------
def initialize_session_state():
    if 'inputs' not in st.session_state:
        st.session_state.inputs = {'client': '', 'unit': 'm²', 'area': 1600.0, 'city': 'Bangkok', 'years': 5, 'currency': 'USD', 'water_price': 10.5}
    if 'lang' not in st.session_state:
        st.session_state.lang = 'English'  # Default language
    if 'calc_results' not in st.session_state:
        st.session_state.calc_results = {}
    if 'city_coefficient' not in st.session_state:
        st.session_state.city_coefficient = 1.0  # Initialize city coefficient to 1.0 as default


# ---------- SIDEBAR INPUTS ----------
def get_inputs():
    apply_styles()

    # Initialize session_state if not already
    initialize_session_state()

    # Language selection dropdown at the bottom of the sidebar
    lang = st.sidebar.selectbox(
        TRANSLATIONS[st.session_state.lang]['input_language'],
        list(TRANSLATIONS.keys()),
        index=list(TRANSLATIONS.keys()).index(st.session_state.lang)
    )

    # Update session language state when changed
    if lang != st.session_state.lang:
        st.session_state.lang = lang  # Save the selected language to session state
        st.experimental_rerun()  # Trigger a rerun to apply language change

    # Update labels based on the selected language
    labels = TRANSLATIONS[st.session_state.lang]

    # 1. Client or Project Name should have black font
    # Here we apply custom styling to the input label directly
    st.sidebar.markdown(f"<p style='color: black; font-weight: 500;'>{labels['input_client']}</p>", unsafe_allow_html=True)
    client = st.sidebar.text_input(labels['input_client'], st.session_state.inputs['client'], key='client_input')

    # 2. Add label "Base Method" above the corresponding field
    st.sidebar.markdown(f"**{labels['base_method']}**", unsafe_allow_html=True)
    base_method_display = st.selectbox("", options=[labels['method_manual'], labels['method_truck']], key='base_method')

    # 3. Add label "Comparison Method" above the corresponding field
    st.sidebar.markdown(f"**{labels['comparison_method']}**", unsafe_allow_html=True)
    comp_method_display = st.selectbox("", options=[labels['method_auto'], labels['method_etbased']], key='comparison_method')

    # 4. Continue with other inputs, using translated labels for the remaining fields
    unit = st.selectbox(labels['input_unit'], list(UNIT_MULTIPLIERS.keys()), index=list(UNIT_MULTIPLIERS.keys()).index(st.session_state.inputs['unit']))
    area = st.number_input(labels['input_area'], min_value=0.0, value=st.session_state.inputs['area'])
    city = st.selectbox(labels['input_city'], list(ET_DATA.keys()), index=list(ET_DATA.keys()).index(st.session_state.inputs['city']))
    years = st.slider(labels['input_years'], 1, 50, st.session_state.inputs['years'])
    currency = st.selectbox(labels['input_currency'], list(EXCHANGE_RATES_FALLBACK.keys()), index=list(EXCHANGE_RATES_FALLBACK.keys()).index(st.session_state.inputs['currency']))
    water_price = st.number_input(labels['input_water_cost'], min_value=0.0, value=st.session_state.inputs['water_price'])

    # Save inputs to session state
    st.session_state.inputs = {'client': client, 'unit': unit, 'area': area, 'city': city, 'years': years, 'currency': currency, 'water_price': water_price}

    # Full width button in column 1
    st.markdown("<br>", unsafe_allow_html=True)  # Add some space above the button
    calculate_button = st.button(labels['calculate_button'], use_container_width=True)  # Language-specific label for button

    return client, area, unit, years, currency, water_price, city, lang, labels

# ---------- CALCULATE COSTS ----------
@st.cache_data
def calculate_costs(area, unit, years, city, price, currency):
    if city not in ET_DATA:
        st.error(f"City '{city}' not found in ET data. Please select a valid city.")
        return None, None, None, None, None

    # Get the infrastructure coefficient for the selected city
    city_coefficient = updated_city_coefficients_reviewed.get(city, 1.0)

    # Store city_coefficient in session_state for later use
    st.session_state.city_coefficient = city_coefficient  # Store it for later use in the summary

    et_mm = ET_DATA[city]
    m2 = area * UNIT_MULTIPLIERS[unit]
    et_m3 = et_mm * m2 / 1000

    # Calculate water usage per year for each method
    usage_per_year = {
        'Manual': et_m3 * 6,
        'Truck': et_m3 * 8,
        'Auto': et_m3 * 1.3,
        'ET-Based': et_m3 * 1.0
    }

    # Calculate the total water usage across all methods for the given years
    usage = {m: round(v * years, 2) for m, v in usage_per_year.items()}

    # Base capital costs for each method
    bases = {'Manual': 613006, 'Truck': 2160000, 'Auto': 280901.4, 'ET-Based': 280901.4}

    # Exchange rate for currency conversion
    rate = EXCHANGE_RATES_FALLBACK[currency]

    # Adjust capital costs by multiplying with the city coefficient
    capital = {m: round(bases[m] * (m2 / UNIT_MULTIPLIERS['Rai']) * rate * city_coefficient, 2) for m in bases}

    # Operational costs
    labor_cost = 0.4
    electricity_cost = 0.3
    water_cost_ratio = 0.3

    # Calculate operational expenses per year for each method
    opex_per_year = {m: round(usage_per_year[m] * price * (labor_cost + electricity_cost + water_cost_ratio), 2) for m in usage_per_year}

    # Calculate total operational expenses over the given number of years
    opex = {m: round(opex_per_year[m] * years, 2) for m in opex_per_year}

    # Total cost is capital plus operational expenses
    total = {m: round(capital[m] + opex_per_year[m] * years, 2) for m in usage_per_year}

    # Store results in session state for further use
    st.session_state.calc_results = {
        'usage_per_year': usage_per_year,
        'usage': usage,
        'total': total,
        'capital': capital,
        'opex_per_year': opex_per_year
    }

    # Return all calculated values
    return usage_per_year, usage, total, capital, opex_per_year


# ---------------------------- Matplotlib and Chart Setup ----------------------------
# Force Matplotlib to use English labels and font
matplotlib.rcParams['axes.unicode_minus'] = False  # Prevent issues with negative signs
matplotlib.rcParams['font.family'] = 'DejaVu Sans'  

# Function to render charts
def render_charts(df, currency):
    """Render the Matplotlib charts with all text in English and proper number formatting."""

    # Explicitly set English labels for all chart titles and axes
    english_labels = {
        'cost': f'Cost (in {currency})',
        'water': 'Water Usage (m³)',
        'co2': 'CO2 Savings (Tons)',  # Explicitly use "CO2" instead of the superscript version
        'irrigation_method': 'Irrigation Method'
    }

    # Hardcode irrigation methods in English
    english_methods = ['Manual', 'Truck', 'Auto', 'ET-Based']
    
    # Replace df['Method'] with the English methods
    df['Method'] = english_methods  # Set the methods to the hardcoded English names

    def currency_format(x, pos):
        """Format y-axis numbers to display currency and avoid any scientific notation or superscript."""
        return f'{x:,.2f}'  # This will format the numbers with comma separation and 2 decimal places

    # Create the first chart (Cost)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(df['Method'], df['Cost_k'])
    ax1.set_title(f'Cost Comparison (in {currency})')  # Explicit English title
    ax1.set_xlabel(english_labels['irrigation_method'])  # Hardcoded English axis label
    ax1.set_ylabel(english_labels['cost'])
    ax1.yaxis.set_major_formatter(FuncFormatter(currency_format))  # Apply currency formatting to y-axis

    # Explicitly set the font for the x-axis labels
    for tick in ax1.get_xticklabels():
        tick.set_fontname('DejaVu Sans')  
        tick.set_fontsize(12)

    # Create the second chart (Water usage)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.bar(df['Method'], df['Water'])
    ax2.set_title('Water Usage Comparison')  # Explicit English title
    ax2.set_xlabel(english_labels['irrigation_method'])  # Hardcoded English axis label
    ax2.set_ylabel(english_labels['water'])
    ax2.yaxis.set_major_formatter(FuncFormatter(currency_format))  # Apply number formatting to y-axis

    # Explicitly set the font for the x-axis labels
    for tick in ax2.get_xticklabels():
        tick.set_fontname('DejaVu Sans')  
        tick.set_fontsize(12)

    # Create the third chart (CO2 savings)
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.bar(df['Method'], df['CO2'])
    ax3.set_title('CO2 Savings Comparison')  # Explicit English title
    ax3.set_xlabel(english_labels['irrigation_method'])  # Hardcoded English axis label
    ax3.set_ylabel(english_labels['co2'])  # Explicitly use "CO₂" and not superscript
    ax3.yaxis.set_major_formatter(FuncFormatter(currency_format))  # Apply number formatting to y-axis

    # Explicitly set the font for the x-axis labels
    for tick in ax3.get_xticklabels():
        tick.set_fontname('DejaVu Sans')  
        tick.set_fontsize(12)

    return fig1, fig2, fig3

    
# Add a table that displays the cost, water usage, and CO2 reduction data with proper units
def display_table(df, labels, currency):
    df_display = df.copy()

    # Add units to the labels in the table for better clarity
    df_display['Cost_k'] = df_display['Cost_k'].apply(lambda x: f"{currency} {x:,.2f}")  # Add currency symbol
    df_display['Water'] = df_display['Water'].apply(lambda x: f"{x:,.2f} m³")  # Add m³ unit for water usage
    df_display['CO2'] = df_display['CO2'].apply(lambda x: f"{x:,.2f} Tons")  # Add Tons unit for CO2 savings

    st.write(df_display)  # Display the table with units



def get_label(labels, key, fallback_lang="English"):
    """Return the label if available, else fallback to English."""
    if key in labels:
        return labels[key]
    else:
        # Fallback to English if the label is missing
        return TRANSLATIONS[fallback_lang].get(key, key)
    

def main():
    # Initialize session state before using it
    initialize_session_state()

    # Apply styles (unchanged)
    apply_styles()

    # Language dropdown now correctly triggers the language change and rerun
    lang = st.sidebar.selectbox(
        get_label(TRANSLATIONS[st.session_state.lang], 'input_language'),
        list(TRANSLATIONS.keys()),
        index=list(TRANSLATIONS.keys()).index(st.session_state.lang)  # Default value from session state
    )

    # Update session language state when changed
    if lang != st.session_state.lang:
        st.session_state.lang = lang  # Save the selected language to session state
        st.rerun()  # Trigger a rerun to apply language change

    # Now get the corresponding labels for the selected language
    labels = TRANSLATIONS[st.session_state.lang]  # Translate labels based on selected language

    # Define methods for irrigation calculation
    method_map = {
        'Manual': get_label(labels, 'method_manual'),
        'Truck': get_label(labels, 'method_truck'),
        'Auto': get_label(labels, 'method_auto'),
        'ET-Based': get_label(labels, 'method_etbased')
    }
    method_map_rev = {v: k for k, v in method_map.items()}  # Reverse map for getting method names back

    col1, col2 = st.columns([1.1, 1.5], gap='large')  # Define col1 and col2

    with col1:
        # Collect project inputs with translated labels
        city = st.selectbox(get_label(labels, 'input_city'), options=list(ET_DATA.keys()), index=0)
        unit = st.selectbox(get_label(labels, 'input_unit'), options=list(UNIT_MULTIPLIERS.keys()), index=0)
        area = st.number_input(get_label(labels, 'input_area'), min_value=0.0, value=1600.0)
        years = st.slider(get_label(labels, 'input_years'), min_value=1, max_value=30, value=5)
        currency = st.selectbox(get_label(labels, 'input_currency'), options=list(EXCHANGE_RATES_FALLBACK.keys()), index=0)
        water_price = st.number_input(get_label(labels, 'input_water_cost'), min_value=0.0, value=10.5)
        client = st.text_input(get_label(labels, 'input_client'), "Unnamed Project")
        c1, c2 = st.columns(2)
        with c1:
            base_method_display = st.selectbox(get_label(labels, 'base_method'), options=list(method_map.values()), key='base_method')
        with c2:
            comp_method_display = st.selectbox(get_label(labels, 'comparison_method'), options=[get_label(labels, 'method_auto'), get_label(labels, 'method_etbased')], key='comparison_method')
        
        st.caption(f"Estimated ET₀ for {city}: {ET_DATA[city]} mm/year")

        # Add the "Calculate" button with an emoji at the bottom of col1
        st.markdown("<br>", unsafe_allow_html=True)  # Add some space above the button
        calculate_button = st.button(labels['calculate_button'], use_container_width=True)  # Language-specific label for button
        st.markdown(
        """
        <div style="font-size: 16px; color: #004d24; text-align: center; margin-top: 5x;">
            <strong>To print this page, press "Ctrl + P" (Windows) or "Cmd + P" (Mac) and select "Save as PDF".</strong>
        </div>
        """,
        unsafe_allow_html=True
        )
        
    with col2:

        # Fetch methods selected
        base_method = method_map_rev.get(base_method_display, 'Manual')
        comp_method = method_map_rev.get(comp_method_display, 'Auto')

        if calculate_button:
            # Ensure that costs are calculated first when the button is pressed
            usage_per_year, usage, total, capital, opex_per_year = calculate_costs(
                area, unit, years, city, water_price, currency
            )

            # Calculate savings and metrics
            annual_savings = round(opex_per_year[base_method] - opex_per_year[comp_method], 2) if base_method != comp_method else 0
            total_savings = annual_savings * years
            capex_diff = capital[base_method] - capital[comp_method]
            payback = f"{round(capex_diff / annual_savings, 1)}" if (annual_savings > 0 and capex_diff > 0) else 'N/A'
            co2_saving = round((usage_per_year[base_method] - usage_per_year[comp_method]) * years * 0.5, 2) if base_method != comp_method else 0

            # Save results to session state
            st.session_state.calc_results = {
                'usage_per_year': usage_per_year,
                'usage': usage,
                'total': total,
                'capital': capital,
                'opex_per_year': opex_per_year,
                'annual_savings': annual_savings,
                'total_savings': total_savings,
                'capex_diff': capex_diff,
                'payback': payback,
                'co2_saving': co2_saving,
                'currency': currency,  # Store selected currency in session state
                'client': client,  # Store client name in session state
                'city': city,  # Store city in session state
                'area': area,  # Store area in session state
                'unit': unit,  # Store unit in session state
                'years': years  # Store years in session state
            }

            # Display the savings and sustainability overview using translated terms
            st.markdown(
                f"""
                <div style='background-color:#e6f4ea;padding:5px 25px;border-radius:10px;margin-bottom:30px;'>
                    <h3 style='color:#004d24;font-weight: 700; text-align:center;'>{get_label(labels, 'savings_and_sustainability')}</h3>
                    <p style='font-size: 14px; color:#004d24; line-height:1.6;'>
                        {get_label(labels, 'annual_savings_description')}
                        <strong>{base_method}</strong> {get_label(labels, 'vs')} <strong>{comp_method}</strong>
                        {get_label(labels, 'long_term_planning')}
                    </p>
                    <!-- Summary of input data used in calculations -->
                    <div style="margin-top: 15px; font-size: 14px; color:#004d24;">
                        <strong>{get_label(labels, 'input_data_summary')}</strong>:
                        <ul>
                            <li><strong>{get_label(labels, 'input_city')}:</strong> {city}</li>
                            <li><strong>{get_label(labels, 'input_area')}:</strong> {area} {unit}</li>
                            <li><strong>{get_label(labels, 'input_currency')}:</strong> {currency}</li>
                            <li><strong>{get_label(labels, 'input_water_cost')}:</strong> {water_price} / m³</li>
                            <li><strong>{get_label(labels, 'input_years')}:</strong> {years} {get_label(labels, 'years')}</li>
                            <li><strong>{get_label(labels, 'base_method')}:</strong> {base_method}</li>
                            <li><strong>{get_label(labels, 'comparison_method')}:</strong> {comp_method}</li>
                            <li><strong>{get_label(labels, 'construction_coefficient')}:</strong> {st.session_state.city_coefficient} (Coefficient for {city})</li>
                        </ul>
                    </div>
                    <div style='flex: 1; padding: 8px; min-width: 220px;'>
                        <h4 style='font-weight: bold; color: #00703c;'>
                            {get_label(labels, 'annual_savings')} {info_icon('annual_savings_info', labels)}
                        </h4>
                        <p style='font-size: 16px; color:#004d24; font-weight: 600;'>{currency} {annual_savings:,.2f} / year</p>
                    </div>
                    <div style='flex: 1; padding: 8px; min-width: 220px;'>
                        <h4 style='font-weight: bold; color: #00703c;'>
                            {get_label(labels, 'total_savings')} {info_icon('total_savings_info', labels)}
                        </h4>
                        <p style='font-size: 16px; color:#004d24; font-weight: 600;'>{currency} {total_savings:,.2f} / {years} {get_label(labels, 'input_years')}</p>
                    </div>
                    <div style='flex: 1; padding: 8px; min-width: 220px;'>
                        <h4 style='font-weight: bold; color: #00703c;'>
                            {get_label(labels, 'capex_diff')} {info_icon('capex_difference_info', labels)}
                        </h4>
                        <p style='font-size: 16px; color:#004d24; font-weight: 600;'>{currency} {capex_diff:,.2f}</p>
                    </div>
                    <div style='flex: 1; padding: 8px; min-width: 220px;'>
                        <h4 style='font-weight: bold; color: #00703c;'>
                            {get_label(labels, 'payback')} {info_icon('payback_period_info', labels)}
                        </h4>
                        <p style='font-size: 16px; color:#004d24; font-weight: 600;'>{payback} {get_label(labels, 'input_years')}</p>
                    </div>
                    <div style='flex: 1; padding: 8px; min-width: 220px;'>
                        <h4 style='font-weight: bold; color: #00703c;'>
                            {get_label(labels, 'co2_saving')} {info_icon('co2_reduction_info', labels)}
                        </h4>
                        <p style='font-size: 16px; color:#004d24; font-weight: 600;'>{co2_saving:,.2f} tons</p>
                    </div>
                    <div style='flex: 1; padding: 8px; min-width: 220px;'>
                        <h4 style='font-weight: bold; color: #00703c;'>
                            {get_label(labels, 'water_efficiency')} {info_icon('water_efficiency_info', labels)}
                        </h4>
                        <p style='font-size: 16px; color:#004d24; font-weight: 600;'>Enhanced</p>
                    </div>
                </div>
                    <div style='margin-top: 5px; text-align: left;'>
                        <h4 style='color:#004d24; font-weight: 700;'>{get_label(labels, 'key_benefits')}</h4>
                        <ul style='list-style: none; padding-left: 0; font-size: 14px;'>
                            <li>🔑 <strong>{get_label(labels, 'water_efficiency_benefit')}</strong></li>
                            <li>🌍 <strong>{get_label(labels, 'environmental_impact_benefit')}</strong></li>
                            <li>💡 <strong>{get_label(labels, 'operational_efficiency_benefit')}</strong></li>
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="footer">
                    <div class="disclaimer">
                        <strong>Disclaimer:</strong> The information provided in this tool is for informational purposes only. The savings, environmental benefits, and other calculations are estimates based on the data provided. Actual results may vary.
                    </div>
                    <div class="credit">
                        <strong>© 2025 Rain Bird Corporation. All rights reserved.</strong> | <a href="https://www.rainbird.com" target="_blank" style="color: #00703c;">Visit our website</a>
                    </div>
                </div>
                """,
            unsafe_allow_html=True
            )
            
            # Create df with the relevant data for charts
            df = pd.DataFrame([{
                'Method': get_label(labels, f'method_{m.lower().replace("-", "").replace(" ", "")}'),
                'Cost_k': round(total[m] / 1000, 2),
                'Water': round(usage_per_year[m], 2),
                'CO2': round(usage_per_year[m] * 0.5 / 1000, 2)
            } for m in usage_per_year])

            # Call the function to display the table with units
            display_table(df, labels, currency)

            # Render the charts after the table
            fig1, fig2, fig3 = render_charts(df, currency)



            # Display the charts
            if fig1 and fig2 and fig3:
                st.pyplot(fig1)
                st.pyplot(fig2)
                st.pyplot(fig3)
            else:
                st.error("Error rendering charts, please check data.")
            


if __name__ == '__main__':
    # Button export color styling
    main()  # Main function call is properly indented


