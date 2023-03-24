import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
from millify import millify
from millify import prettify
import folium
from folium.features import GeoJsonTooltip
from streamlit_folium import st_folium
import geopandas as gpd

# custo-myze vvvvvvvvvvvvvvvvvvvvvvvv
im = Image.open('content/migration.png')
st.set_page_config(page_title='IRS Migration', layout="wide", page_icon=im)

hide_default_format = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        section.main > div:has(~ footer ) {
        padding-bottom: 5px;}
        div.block-container{padding-top:1.5rem;}
       </style>
       """

st.markdown(hide_default_format, unsafe_allow_html=True)
# custo-myze ^^^^^^^^^^^^^^^^^^^^^^^^^

accent_color = '#E2F1AF'

# sidebar ------------------------------------------------------------------------------------------------------------------------------
summary = st.sidebar.radio(
    'Summary level:',
    ('NE Georgia Region', 'Single County')
    )

county = ''

if summary == 'NE Georgia Region':
    county = ''
else:
    county = st.sidebar.selectbox(
        'Select metro county:',
        ('Banks County', 
        'Dawson County', 
        'Habersham County', 
        'Hall County', 
        'Jackson County', 
        'Lumpkin County',  
        'White County'),
    )

summary_dict = {
    'NE Georgia Region':'Northeast Georgia',
    'Single County':f'{county}'
}

# MIGRATION VARIABLE VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
mig_variable = st.sidebar.selectbox(
    'Dashboard variable:',
    ('People', 'Dollars', 'Dollars per capita')
)

# lower case-ify
var_lower = mig_variable.lower()

var_csv_dict = {
    'People':'n2',
    'Dollars':'agi',
}
var_csv_dict2 = {
    'n2_inflow':['Total inflow', 'Where they\'re coming from'],
    'n2_outflow':['Total outflow', 'Where they\'re going'],
    'agi_inflow':['Total inflow', 'Where dollars are coming from'],
    'agi_outflow':['Total outflow', 'Where dollars are going']
}


# MIGRATION VARIABLE ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



# MIGRATION DIRECTION vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
mig_direction = st.sidebar.radio(
    f'Flow direction:',
    ('In', 'Out')
)

direction_lower = mig_direction.lower()

var_csv_dict3 = {
    'n2_net':f'Net {direction_lower}flow of {var_lower}',
    'agi_net':f'Net {direction_lower}flow of {var_lower}($)'
}


mig_direction_dict = {
    'In': 'into',
    'Out': 'out of'
}

mig_direction_dict2 = {
    'In': 'originations',
    'Out': 'destinations'
}

mig_direction_dict3 = {
    'In': 'Origination',
    'Out': 'Destination'
}


# MIGRATION DIRECTION ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# SLIDERvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
slider_years = [2015, 2016, 2017, 2018, 2019, 2020]
slider_start = slider_years[0]
slider_end = slider_years[-1]

years = st.sidebar.slider(
    'Year range:',
    slider_start,slider_end,(2017,2019)
)
# convert years selected to list
years = list(years)

# get full range of years included by the slider
def fill_in_years(lst):
    n1 = lst[0]
    n2 = lst[-1]
    lst[:] = range(n1, n2 + 1)
    return lst

full_years = fill_in_years(years)

# SLIDER^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# sidebar source
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.write("")
st.sidebar.markdown("*Source: [IRS Statistics of Income](https://www.irs.gov/statistics/soi-tax-stats-migration-data)*")

# main content -------------------------------------------------------------------------------------------------

# set header
st.markdown(f"<h2><span style='color:{accent_color}'>NE Georgia Migration Dashboard</span> | {years[0]} to {years[-1]}</h2>", unsafe_allow_html=True)

# set subheader
if years[0] == years[-1]:
    st.info('***Error!**  Please select separate start & end years via the year range slider.*')
else:
    st.subheader("")

fips_dict = {
    'Habersham County':137,
    'Lumpkin County':187,
    'Hall County':139,
    'White County':311,
    'Dawson County':85,
    'Banks County':11,
    'Jackson County':157
}

# reverse the fips_dict above
fips_dict2 = {v: k for k, v in fips_dict.items()}

# county-metro mapping dictionary
secondary_metro = {
    'Miami, Dade County': 'Miami-Dade County, FL',
    'New York County, NY': 'New York County, NY (Manhattan)',
    'Kings County, NY': 'Kings County, NY (Brooklyn)',
    'Queens County, NY': 'Queens County, NY (Queens)',
    'Broward County, FL': 'Broward County, FL (Miami metro)',
    'Cook County, IL': 'Cook County, IL (Chicago)',
    'Palm Beach County, FL':'Palm Beach County, FL (Miami metro)',
    'Broward County, FL':'Broward County, FL (Miami metro)',
    'Fairfield County, CT':'Fairfield County, CT (NYC metro)',
    'Harris County, TX':'Harris County, TX (Houston)',
    'Shelby County, TN':'Shelby County, TN (Memphis)',
    'Nassau County, NY':'Nassau County, NY (Long Island)',
    'Walton County, FL':'Walton County, FL (Panhandle)',
    'Bronx County, NY':'Bronx County, NY (The Bronx)',
    'Beaufort County, SC':'Beaufort County, SC (Hilton Head)',
    'Alameda County, CA':'Alameda County, CA (Bay Area)',
    'Hudson County, NJ':'Hudson County, NJ (NYC metro)',
    'Oakland County, MI':'Oakland County, MI (Detroit metro)',
    'Bergen County, NJ':'Bergen County, NJ (NYC metro)',
    'Westchester County, NY':'Westchester County, NY (NYC metro)',
    'Essex County, NJ':'Essex County, NJ (NYC metro)',
    'Duval County, FL':'Duval County, FL (Jacksonville)',
    'Hennepin County, MN':'Hennepin County, MN (Minneapolis)',
    'Travis County, TX':'Travis County, TX (Austin)',
    'Cuyahoga County, OH':'Cuyahoga County, OH (Cleveland)',
    'Middlesex County, NJ':'Middlesex County, NJ (NYC metro)',
    'Mecklenburg County, NC':'Mecklenburg County, NC (Charlotte)',
    'Contra Costa County, CA':'Contra Costa County, CA (Bay Area)',
    'Morris County, NJ':'Morris County, NJ (NYC metro)',
    'Collier County, FL':'Collier County, FL (Naples)',
    'Arlington County, VA':'Arlington County, VA (DC metro)',
    'Lake County, IL':'Lake County, IL (Chicago metro)',
    'St. Johns County, FL':'St. Johns County, FL (Jacksonville metro)',
    'Norfolk County, MA':'Norfolk County, MA (Boston metro)',
    'DuPage County, IL':'DuPage County, IL (Chicago metro)',
    'San Mateo County, CA':'San Mateo County, CA (Bay Area)',
    'Montgomery County, PA':'Montgomery County, PA (Philadelphia metro)',
    'Benton County, AR':'Benton County, AR (Bentonville)',
    'Santa Clara County, CA':'Santa Clara County, CA (San Jose)',
    'Chester County, PA':'Chester County, PA (Philadelphia metro)',
    'Boulder County, CO':'Boulder County, CO (Boulder)',
    'Delaware County, PA':'Delaware County, PA (Philadelphia metro)',
    'Manatee County, FL':'Manatee County, FL (Tampa metro)',
    'Williamson County, TN':'Williamson County, TN (Nashville metro)',
    'Warren County, OH':'Warren County, OH (Cincinnati metro)',
    'Johnson County, KS':'Johnson County, KS (Kansas City metro)',
    'Somerset County, NJ':'Somerset County, NJ (NYC metro)',
    'Maricopa County, AZ':'Maricopa County, AZ (Phoenix)',
    'Jefferson County, AL':'Jefferson County, AL (Birmingham)',
    'Hillsborough County, FL':'Hillsborough County, FL (Tampa)',
    'Lee County, AL':'Lee County, AL (Opelika)',
    'Okaloosa County, FL':'Okaloosa County, FL (Panhandle)',
    'Loudoun County, VA':'Loudoun County, VA (DC metro)',
    'Fairfax County, VA':'Fairfax County, VA (DC metro)',
    'King County, WA':'King County, WA (Seattle)',
    'Fort Bend County, TX':'Fort Bend County, TX (Houston metro)',
    'Forsyth County, NC':'Forsyth County, NC (Winston-Salem)',
    'Collin County, TX':'Collin County, TX (Dallas metro)',
    'Orange County, CA':'Orange County, CA (LA metro)',
    'Chesterfield County, VA':'Chesterfield County, VA (Richmond metro)',
    'Tarrant County, TX':'Tarrant County, TX (Fort Worth)',
    'Brevard County, FL':'Brevard County, FL (Melbourne)',
    'Lee County, FL':'Lee County, FL (Fort Myers)',
    'Wake County, NC':'Wake County, NC (Raleigh)',
    'Pinellas County, FL':'Pinellas County, FL (St. Pete/Clearwater)',
    'Clarke County, GA':'Athens-Clarke County, GA',
    'Richmond County, GA':'Augusta-Richmond County, GA',
    'Buncombe County, NC':'Buncombe County, NC (Asheville)',
    'Middlesex County, MA':'Middlesex County, MA (Boston metro)',
    'District of Columbia, DC':'Washington, D.C.',
    'Henrico County, VA':'Henrico County, VA (Richmond metro)',
    'Jefferson County, KY':'Jefferson County, KY (Louisville)',
    'Bexar County, TX':'Bexar County, TX (San Antonio)',
    'Davidson County, TN':'Davidson County, TN (Nashville)',
    'Suffolk County, MA':'Suffolk County, MA (Boston)',
    'Denton County, TX':'Denton County, TX (Dallas metro)',
    'Prince George\'s County, MD':'Prince George\'s County, MD (DC metro)',
    'Richland County, SC':'Richland County, SC (Columbia)',
    'Cumberland County, NC':'Cumberland County, NC (Fayetteville)',
    'Orange County, FL':'Orange County, FL (Orlando)',
    'Suffolk County, NY':'Suffolk County, NY (Long Island)'
}

format_dict = {
    'Dollars':'$~s',
    'People':',',
    'Dollars per capita':'$.2f'
}


# function that calculates the CUMULATIVE flow of dollars or people at a metro level
def metro_metric_cumulative():
    df = pd.read_csv('Data/metro_ALL.csv')
    df = df[(df['year1'].isin(full_years)) & (df['year2'].isin(full_years))]
    # migration summary
    var_people = df[f'n2_{direction_lower}flow'].sum().astype(int)
    var_prettify_people = prettify(var_people)
    value1 = var_prettify_people
    # agi summary
    var_agi = df[f'agi_{direction_lower}flow'].sum()
    var_prettify_agi = millify(var_agi, precision=1)
    value2 = f'${var_prettify_agi}'
    # agi per capita summary
    var_agi_capita = var_agi / var_people
    var_agi_capita = round(var_agi_capita.astype(int), 0)
    var_prettify_agi_capita = prettify(var_agi_capita)
    value3 = f'${var_prettify_agi_capita}'
    metric_dict = {
        'People':value1,
        'Dollars':value2,
        'Dollars per capita':value3
    }
    x1 = metric_dict[mig_variable]
    return x1

# function that calculates the CUMULATIVE flow of dollars or people at a county level
def county_metric_cumulative():
    df = pd.read_csv('Data/county_total_ALL.csv')
    df = df[(df['year1'].isin(full_years)) & (df['year2'].isin(full_years))]
    df = df.groupby('arc_county').sum().reset_index()
    df = df[df['arc_county'] == county]
    # migration summary
    var_people = df[f'n2_{direction_lower}flow'].sum().astype(int)
    var_prettify_people = prettify(var_people)
    value1 = var_prettify_people
    # agi summary
    var_agi = df[f'agi_{direction_lower}flow'].sum()
    var_prettify_agi = millify(var_agi, precision=1)
    value2 = f'${var_prettify_agi}'
    # agi per capita summary
    var_agi_capita = var_agi / var_people
    var_agi_capita = round(var_agi_capita.astype(int), 0)
    var_prettify_agi_capita = prettify(var_agi_capita)
    value3 = f'${var_prettify_agi_capita}'
    metric_dict = {
        'People':value1,
        'Dollars':value2,
        'Dollars per capita':value3
    }
    x1 = metric_dict[mig_variable]
    return x1

# function that calculates the NET flow of dollars or people at a metro level
def metro_metric_net():
    df = pd.read_csv('Data/metro_ALL.csv')
    df = df[(df['year1'].isin(full_years)) & (df['year2'].isin(full_years))]
    net_people = df['n2_net'].sum()
    net_people = prettify(net_people)
    net_dollars = df['agi_net'].sum()
    net_dollars = millify(net_dollars, precision=1)
    metric_dict1 = {
        'People':net_people,
        'Dollars':f'${net_dollars}',
    }
    x2 = metric_dict1[mig_variable]
    return x2

# function that calculates the NET flow of dollars or people at a county level
def county_metric_net():
    df = pd.read_csv('Data/county_total_ALL.csv')
    df = df[(df['year1'].isin(full_years)) & (df['year2'].isin(full_years))]
    df = df.groupby('arc_county').sum().reset_index()
    df = df[df['arc_county'] == county]
    net_people = df['n2_net'].sum()
    net_people = prettify(net_people)
    net_dollars = df['agi_net'].sum()
    net_dollars = millify(net_dollars, precision=1)
    metric_dict1 = {
        'People':net_people,
        'Dollars':f'${net_dollars}',
    }
    x2 = metric_dict1[mig_variable]
    return x2

# function to draw Plotly line chart of the variable in question
def plotly_line_1():
    # to be used for charting yearly net flow of persons & dollars
    df_line = pd.read_csv('Data/metro_ALL.csv')

    format_dict = {
        'Dollars':'$~s',
        'People':','
    }

    fig = px.line(
        df_line, 
        x="year2", 
        y=f'{var_csv_dict[mig_variable]}_net', 
        title=f'Yearly <span style="text-decoration: underline;">net</span> flow of {var_lower}',
        labels={
            'year2':'Year',
            f'{var_csv_dict[mig_variable]}_net': f'Net flow of {var_lower}'
        },
    )

    fig.update_traces(
        mode="markers+lines",
        line_color='#FFFFFF',
        hovertemplate=None
        )

    fig.update_layout(
        xaxis = dict(
            showticklabels = True,
            tickmode = 'array',
            tickvals = slider_years,
            ticktext = slider_years,
            title = None
            ),
        margin = {
            'l':10,
            'r':10,
            't':50,
            'b':10
            },
        width=550,
        height=275,
        hovermode="x unified",
        yaxis = dict(
            title = None,
            tickformat = format_dict[mig_variable],
            showgrid = False
            )
        )

   
    if slider_start in years:
        fig.add_vline(x=years[1], line_width=0, line_dash="dash", line_color=accent_color)
    else:
        fig.add_vline(x=years[0], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_vline(x=years[-1], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_hline(y=0, line_width=1, line_dash="solid", line_color="#FFFFFF")
    
    return fig

def plotly_line_1_county():
    # to be used for charting yearly net flow of persons & dollars
    df_line = pd.read_csv('Data/county_total_ALL.csv')
    df_line = df_line[df_line['arc_county'] == county]


    fig = px.line(
        df_line, 
        x="year2", 
        y=f'{var_csv_dict[mig_variable]}_net', 
        title=f'Yearly <span style="text-decoration: underline;">net</span> flow of {var_lower} {mig_direction_dict[mig_direction]} {county}',
        labels={
            'year2':'Year',
            f'{var_csv_dict[mig_variable]}_net': f'Net flow of {var_lower}'
        },
    )

    fig.update_traces(
        mode="markers+lines",
        line_color='#FFFFFF',
        hovertemplate=None
        )

    format_dict = {
        'Dollars':'$~s',
        'People':','
    }

    fig.update_layout(
        xaxis = dict(
            showticklabels = True,
            tickmode = 'array',
            tickvals = slider_years,
            ticktext = slider_years,
            title = None
            ),
        margin = {
            'l':10,
            'r':10,
            't':50,
            'b':10
            },
        width=550,
        height=275,
        hovermode="x unified",
        yaxis = dict(
            title = None,
            tickformat = format_dict[mig_variable],
            showgrid = False
            )
        )

   
    if slider_start in years:
        fig.add_vline(x=years[1], line_width=0, line_dash="dash", line_color=accent_color)
    else:
        fig.add_vline(x=years[0], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_vline(x=years[-1], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="#FFFFFF")
    
    return fig

def plotly_line_2():
    # used to chart yearly inflow/outflow of dollars per capita
    df_line = pd.read_csv('Data/metro_ALL.csv')

    format_dict = {
        'Dollars':'$~s',
        'People':',',
        'Dollars per capita':'$~s'
    }

    fig = px.line(
        df_line, 
        x="year2", 
        y=f'agi_{direction_lower}flow_capita', 
        title=f'Yearly {direction_lower}flow of dollars per capita',
        labels={
            'year2':'Year',
            f'agi_{direction_lower}flow_capita': f'{mig_direction}flow of dollars per capita'},
    )

    fig.update_traces(
        mode="markers+lines",
        line_color='#FFFFFF',
        hovertemplate=None
        )

    fig.update_layout(
        xaxis = dict(
            showticklabels = True,
            tickmode = 'array',
            tickvals = slider_years,
            ticktext = slider_years,
            title = None
            ),
        yaxis = dict(
            title = None,
            tickformat = format_dict[mig_variable],
            showgrid = False
        ),
        margin = {
            'l':10,
            'r':10,
            't':100,
            'b':10
            },
        width=400,
        height=300,
        hovermode="x unified"
        )

    if slider_start in years:
        fig.add_vline(x=years[1], line_width=0, line_dash="dash", line_color=accent_color)
    else:
        fig.add_vline(x=years[0], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_vline(x=years[-1], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_hline(y=0, line_width=1, line_dash="solid", line_color="#FFFFFF")

    return fig

def plotly_line_2_county():
    # used to chart yearly inflow/outflow of dollars per capita
    df_line = pd.read_csv('Data/county_total_ALL.csv')
    df_line = df_line[df_line['arc_county'] == county]

    format_dict = {
        'Dollars':'$~s',
        'People':',',
        'Dollars per capita':'$~s'
    }

    fig = px.line(
        df_line, 
        x="year2", 
        y=f'agi_{direction_lower}flow_capita', 
        title=f'Yearly {direction_lower}flow of dollars per capita',
        labels={
            'year2':'Year',
            f'agi_{direction_lower}flow_capita': f'{mig_direction}flow of dollars per capita'},
    )

    fig.update_traces(
        mode="markers+lines",
        line_color='#FFFFFF',
        hovertemplate=None
        )

    fig.update_layout(
        yaxis_title = None,
        xaxis = dict(
            showticklabels = True,
            tickmode = 'array',
            tickvals = slider_years,
            ticktext = slider_years,
            title = None
            ),
        yaxis = dict(
            tickformat = format_dict[mig_variable],
            showgrid = False
        ),
        margin = {
            'l':10,
            'r':10,
            't':100,
            'b':10
            },
        width=400,
        height=400,
        hovermode="x unified"
        )

    if slider_start in years:
        fig.add_vline(x=years[1], line_width=0, line_dash="dash", line_color=accent_color)
    else:
        fig.add_vline(x=years[0], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_vline(x=years[-1], line_width=3, line_dash="dash", line_color=accent_color)
    fig.add_hline(y=0, line_width=1, line_dash="solid", line_color="#FFFFFF")
    
    return fig

def plotly_bar_total():
    # used to chart top origins / destinations
    df_bar = pd.read_csv('Data/county_to_county_ALL.csv')
    df_bar = df_bar.loc[:, ~df_bar.columns.str.startswith('Unnamed')]
    df_bar = df_bar[(df_bar['year1'].isin(full_years)) & (df_bar['year2'].isin(full_years))]
    # fill in the counties with their respective metro areas parenthetically
    df_bar['sec_unique'] = df_bar['sec_unique'].map(secondary_metro).fillna(df_bar['sec_unique'])
    df_bar_grouped = df_bar.groupby('sec_unique').sum().reset_index()
    df_bar_grouped = df_bar_grouped.sort_values(f'{var_csv_dict[mig_variable]}_{direction_lower}flow', ascending=False).head(10)

    tick_format_dict = {
        'Dollars':'$~s',
        'People':','
    }

    fig = px.bar(
        df_bar_grouped, 
        x='sec_unique', 
        y=f'{var_csv_dict[mig_variable]}_{direction_lower}flow',
        title=f"Top {mig_direction_dict2[mig_direction]} outside the region (<span style='text-decoration: underline;'>gross</span>)",
        labels={
            'sec_unique':f'{mig_direction_dict3[mig_direction]}',
            f'{var_csv_dict[mig_variable]}_{direction_lower}flow': var_csv_dict2[f'{var_csv_dict[mig_variable]}_{direction_lower}flow'][0]},
    )

    fig.update_layout(
        xaxis_title = None,
        margin = {
            'l':0,
            'r':10,
            't':50,
            'b':10
            },
        height=380,
        width=550,
        bargap=0.7,
        yaxis = dict(
            title = None,
            tickformat = tick_format_dict[mig_variable],
            showgrid = False
        )
    )

    fig.update_traces(
        marker_color=accent_color, 
        marker_line_color=accent_color,
        marker_line_width=3, 
        )
    fig.add_hline(y=0, line_width=1, line_dash="solid", line_color="#FFFFFF")
    
    return fig

def plotly_bar_total_county():
    # used to chart top origins / destinations
    df_bar = pd.read_csv('Data/total_tester_init.csv')
    df_bar = df_bar[df_bar['arc_county'] == county]
    df_bar = df_bar.loc[:, ~df_bar.columns.str.startswith('Unnamed')]
    df_bar = df_bar[(df_bar['year1'].isin(full_years)) & (df_bar['year2'].isin(full_years))]
    # fill in the counties with their respective metro areas parenthetically
    df_bar['secondary_county_y'] = df_bar['secondary_county_y'].map(secondary_metro).fillna(df_bar['secondary_county_y'])
    df_bar_grouped = df_bar.groupby('secondary_county_y').sum().reset_index()
    df_bar_grouped = df_bar_grouped.sort_values(f'{var_csv_dict[mig_variable]}_{direction_lower}flow', ascending=False).head(10)

    tick_format_dict = {
        'Dollars':'$~s',
        'People':','
    }

    fig = px.bar(
        df_bar_grouped, 
        x='secondary_county_y', 
        y=f'{var_csv_dict[mig_variable]}_{direction_lower}flow',
        title=f"Top {mig_direction_dict2[mig_direction]} (<span style='text-decoration: underline;'>gross</span>)",
        labels={
            'secondary_county_y':f'{mig_direction_dict3[mig_direction]}',
            f'{var_csv_dict[mig_variable]}_{direction_lower}flow': var_csv_dict2[f'{var_csv_dict[mig_variable]}_{direction_lower}flow'][0]},
    )

    fig.update_layout(
        xaxis_title = None,
        margin = {
            'l':0,
            'r':10,
            't':50,
            'b':10
            },
        height=380,
        width=550,
        bargap=0.7,
        yaxis = dict(
            tickformat = tick_format_dict[mig_variable],
            showgrid = False
        )
    )

    fig.update_traces(
        marker_color=accent_color, 
        marker_line_color=accent_color,
        marker_line_width=3, 
        )
    fig.add_hline(y=0, line_width=1, line_dash="solid", line_color="#FFFFFF")
    
    return fig

def plotly_bar_net():
    df_bar_2 = pd.read_csv('Data/county_to_county_ALL.csv')
    df_bar_2 = df_bar_2.loc[:, ~df_bar_2.columns.str.startswith('Unnamed')]
    df_bar_2 = df_bar_2[(df_bar_2['year1'].isin(full_years)) & (df_bar_2['year2'].isin(full_years))]
    df_bar_2['sec_unique'] = df_bar_2['sec_unique'].map(secondary_metro).fillna(df_bar_2['sec_unique'])
    df_bar_grouped_2 = df_bar_2.groupby('sec_unique').sum().reset_index()
    df_bar_grouped_2 = df_bar_grouped_2[['sec_unique', 'n2_net', 'agi_net']]

    # the 2 easy dataframes - just take the top 10
    df_n2_in = df_bar_grouped_2.sort_values('n2_net', ascending=False).head(10)
    df_agi_in = df_bar_grouped_2.sort_values('agi_net', ascending=False).head(10)

    # some extra work for the 'bottom 10' dataframes
    df_n2_out = df_bar_grouped_2.sort_values('n2_net', ascending=False).tail(10)
    df_n2_out['n2_net'] = df_n2_out['n2_net'] * -1
    df_n2_out = df_n2_out.sort_values('n2_net', ascending=False)

    df_agi_out = df_bar_grouped_2.sort_values('agi_net', ascending=False).tail(10)
    df_agi_out['agi_net'] = df_agi_out['agi_net'] * -1
    df_agi_out = df_agi_out.sort_values('agi_net', ascending=False)

    if mig_variable == 'People' and direction_lower == 'in':
        df = df_n2_in
    elif mig_variable == 'People' and direction_lower == 'out':
        df = df_n2_out
    elif mig_variable == 'Dollars' and direction_lower == 'in':
        df = df_agi_in
    else:
        df = df_agi_out

    tick_format_dict = {
    'Dollars':'$~s',
    'People':','
        }

    fig = px.bar(
        df,
        y='sec_unique', 
        x=f'{var_csv_dict[mig_variable]}_net',
        title=f"{var_csv_dict2[f'{var_csv_dict[mig_variable]}_{direction_lower}flow'][1]}: top {mig_direction_dict2[mig_direction]} outside the region (<span style='text-decoration: underline;'>net</span>)",
        labels={
            'sec_unique':f'{mig_direction_dict3[mig_direction]}',
            f'{var_csv_dict[mig_variable]}_net': var_csv_dict3[f'{var_csv_dict[mig_variable]}_net']
            },
        orientation='h'
    )

    fig.update_layout(
        xaxis_title = None,
        yaxis_title = None,
        margin = {
            'l':0,
            'r':10,
            't':50,
            'b':10
            },
        width=400,
        height=725,
        bargap=0.5,
        xaxis = dict(
            tickformat = tick_format_dict[mig_variable]
        ),
    )

    fig.update_traces(
        marker_color=accent_color, 
        marker_line_color=accent_color,
        marker_line_width=3,
        )

    fig.update_yaxes(autorange="reversed")

    return fig

def plotly_bar_net_county():
    df_bar_2 = pd.read_csv('Data/total_tester_init.csv')
    df_bar_2 = df_bar_2[df_bar_2['arc_county'] == county]
    df_bar_2 = df_bar_2.loc[:, ~df_bar_2.columns.str.startswith('Unnamed')]
    df_bar_2 = df_bar_2[(df_bar_2['year1'].isin(full_years)) & (df_bar_2['year2'].isin(full_years))]
    df_bar_2['secondary_county_y'] = df_bar_2['secondary_county_y'].map(secondary_metro).fillna(df_bar_2['secondary_county_y'])
    df_bar_grouped_2 = df_bar_2.groupby('secondary_county_y').sum().reset_index()
    df_bar_grouped_2 = df_bar_grouped_2[['secondary_county_y', 'n2_net', 'agi_net']]

    # the 2 easy dataframes - just take the top 10
    df_n2_in = df_bar_grouped_2.sort_values('n2_net', ascending=False).head(5)
    df_agi_in = df_bar_grouped_2.sort_values('agi_net', ascending=False).head(5)

    # some extra work for the 'bottom 10' dataframes
    df_n2_out = df_bar_grouped_2.sort_values('n2_net', ascending=False).tail(5)
    df_n2_out['n2_net'] = df_n2_out['n2_net'] * -1
    df_n2_out = df_n2_out.sort_values('n2_net', ascending=False)

    df_agi_out = df_bar_grouped_2.sort_values('agi_net', ascending=False).tail(5)
    df_agi_out['agi_net'] = df_agi_out['agi_net'] * -1
    df_agi_out = df_agi_out.sort_values('agi_net', ascending=False)

    if mig_variable == 'People' and direction_lower == 'in':
        df = df_n2_in
    elif mig_variable == 'People' and direction_lower == 'out':
        df = df_n2_out
    elif mig_variable == 'Dollars' and direction_lower == 'in':
        df = df_agi_in
    else:
        df = df_agi_out

    tick_format_dict = {
        'Dollars':'$~s',
        'People':','
    }

    fig = px.bar(
        df,
        y='secondary_county_y', 
        x=f'{var_csv_dict[mig_variable]}_net',
        title=f"{var_csv_dict2[f'{var_csv_dict[mig_variable]}_{direction_lower}flow'][1]}: top {mig_direction_dict2[mig_direction]} (<span style='text-decoration: underline;'>net</span>)",
        labels={
            'secondary_county_y':f'{mig_direction_dict3[mig_direction]}',
            f'{var_csv_dict[mig_variable]}_net': var_csv_dict3[f'{var_csv_dict[mig_variable]}_net']
            },
        orientation='h'
    )

    fig.update_layout(
        xaxis_title = None,
        yaxis_title = None,
        margin = {
            'l':0,
            'r':10,
            't':50,
            'b':10
            },
        width=400,
        height=725,
        bargap=0.5,
        xaxis = dict(
            tickformat = tick_format_dict[mig_variable]
        ),
    )

    fig.update_traces(
        marker_color=accent_color, 
        marker_line_color=accent_color,
        marker_line_width=3,
        )

    fig.update_yaxes(autorange="reversed")

    return fig

def dollars_person_bar():
    df = pd.read_csv('Data/county_to_county_ALL.csv')
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    df = df[(df['year1'].isin(full_years)) & (df['year2'].isin(full_years))]
    df['sec_unique'] = df['sec_unique'].map(secondary_metro).fillna(df['sec_unique'])
    df = df.groupby('sec_unique').sum().reset_index()
    df['agi_capita_in'] = df['agi_inflow'] / df['n2_inflow']
    df['agi_capita_out'] = df['agi_outflow'] / df['n2_outflow']
    df = df[['sec_unique', 'agi_capita_in', 'agi_capita_out']]

    if mig_direction == 'In':
        df = df.sort_values('agi_capita_in', ascending=False).head(10)
    else:
        df = df.sort_values('agi_capita_out', ascending=False).head(10)

    fig = px.bar(
        df, 
        x=f'agi_capita_{direction_lower}', 
        y='sec_unique', 
        orientation='h',
        title=f'Top 10 AGI / capita {mig_direction_dict2[mig_direction]} flowing {mig_direction_dict[mig_direction]} {summary_dict[summary]}',
        labels={
            'sec_unique':f'{mig_direction_dict3[mig_direction]}',
            f'agi_capita_{direction_lower}': f'Average AGI per capita {direction_lower}flow'
            })

    fig.update_traces(
        marker_color=accent_color, 
        marker_line_color=accent_color,
        marker_line_width=3, 
        )

    fig.update_layout(
        xaxis_title = None,
        yaxis_title = None,
        margin = {
            'l':0,
            'r':10,
            't':50,
            'b':10
            },
        width=500,
        height=350,
        bargap=0.7,
        xaxis = dict(
            tickformat = "$~s"
        ),
    )

    fig.update_yaxes(autorange="reversed")


    return fig

def dollars_person_bar_county():
    df = pd.read_csv('Data/total_tester_init.csv')
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    df = df[(df['year1'].isin(full_years)) & (df['year2'].isin(full_years))]
    df = df[df['arc_county'] == county]
    df['sec_unique'] = df['secondary_county_y'].map(secondary_metro).fillna(df['secondary_county_y'])
    df = df.groupby('sec_unique').sum().reset_index()
    df['agi_capita_in'] = df['agi_inflow'] / df['n2_inflow']
    df['agi_capita_out'] = df['agi_outflow'] / df['n2_outflow']
    df = df[['sec_unique', 'agi_capita_in', 'agi_capita_out']]

    if mig_direction == 'In':
        df = df.sort_values('agi_capita_in', ascending=False).head(12)
    else:
        df = df.sort_values('agi_capita_out', ascending=False).head(12)

    fig = px.bar(
        df, 
        x=f'agi_capita_{direction_lower}', 
        y='sec_unique', 
        orientation='h',
        title=f'Top AGI / capita {mig_direction_dict2[mig_direction]} flowing {mig_direction_dict[mig_direction]} {summary_dict[summary]}',
        labels={
            'sec_unique':f'{mig_direction_dict3[mig_direction]}',
            f'agi_capita_{direction_lower}': f'Average AGI per capita {direction_lower}flow'
            })

    fig.update_traces(
        marker_color=accent_color, 
        marker_line_color=accent_color,
        marker_line_width=3, 
        )

    fig.update_layout(
        xaxis_title = None,
        yaxis_title = None,
        margin = {
            'l':0,
            'r':10,
            't':50,
            'b':10
            },
        width=500,
        height=725,
        bargap=0.5,
        xaxis = dict(
            tickformat = "$~s"
        ),
    )

    fig.update_yaxes(autorange="reversed")


    return fig


def dollars_person_map():
    m = folium.Map(location=[34.479469076350846, -83.74332002597043], zoom_start=9, tiles='CartoDB positron')

    df_counties = pd.read_csv('Data/county_total_ALL.csv')
    df_counties['arc_county'] = df_counties['unique_tag'].map(lambda x: x.replace(' total migration-', ""))
    df_counties['arc_county'] = df_counties['arc_county'].str[:-4]
    df_counties = df_counties[(df_counties['year1'].isin(full_years)) & (df_counties['year2'].isin(full_years))]
    df_counties = df_counties.groupby('arc_county').sum().reset_index()
    df_counties['agi_capita_in'] = df_counties['agi_inflow'] / df_counties['n2_inflow']
    df_counties['agi_capita_out'] = df_counties['agi_outflow'] / df_counties['n2_outflow']

    gdf = gpd.read_file('Data/NE_counties.geojson')

    gdf2 = gdf.merge(df_counties, left_on='NAMELSAD', right_on='arc_county')
    gdf2['agi_capita_in'] = gdf2['agi_capita_in'].astype(int)
    gdf2['agi_capita_out'] = gdf2['agi_capita_out'].astype(int)

    gdf2['county_tooltip'] = gdf2['arc_county'].str.split(' ').str[0]
    gdf2['in_tooltip'] = gdf2['agi_capita_in'].apply(lambda x: "${:,.0f}".format(x))
    gdf2['out_tooltip'] = gdf2['agi_capita_out'].apply(lambda x: "${:,.0f}".format(x))

    choro_dict_value = {
        'In':'agi_capita_in',
        'Out':'agi_capita_out'
    }

    choro_dict_tooltip = {
        'In':'in_tooltip',
        'Out':'out_tooltip'
    }

    # choropleth
    delta_choro = folium.Choropleth(
        geo_data=gdf2,
        data=gdf2,
        columns=['arc_county', choro_dict_value[mig_direction], 'county_tooltip', 'in_tooltip'],
        bins=4,  
        key_on='feature.properties.NAMELSAD', 
        fill_color='Greens',
        name='AGI per capita',
        fill_opacity=0.6,
        nan_fill_color="Black", 
        line_opacity=0.2,
        highlight=True,
        show=True,
        control=False,
        line_color='black')
    
    delta_choro.geojson.add_to(m)

    # tooltip
    delta_choro.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields = [
                'arc_county', 
                choro_dict_tooltip[mig_direction]
                ], 
            aliases = [
                'County:', 
                f"Average AGI per capita {direction_lower}flow: "
                ],
            style = ('background-color:grey; color:white; font-family:helvetica; font-size:12px; margin:1px'),
            localize = True,
            labels = False
        ))

    # remove stock legend from map
    for key in delta_choro._children:
        if key.startswith('color_map'):
            del(delta_choro._children[key])
    delta_choro.add_to(m)

    return m


# decision time
if summary == 'NE Georgia Region':
    if mig_variable == 'Dollars per capita':
        col1, col2 = st.columns([1.5,1])
        with col1:
            st.write(f"Average AGI per capita ({direction_lower}flow)")
            st_map = st_folium(dollars_person_map(), width=650)
        with col2:
            subcol1, subcol2 = st.columns([1, 1])
            subcol1.metric(label=f'Average metro {direction_lower}flow per capita:', value=metro_metric_cumulative())
            subcol2.write("")
        col2.plotly_chart(plotly_line_2(), use_container_width=True, config = {'displayModeBar': False})
        col2.plotly_chart(dollars_person_bar(), use_container_width=True, config = {'displayModeBar': False})
    else:
        col1, col2 = st.columns([1.5,1])
        col1.plotly_chart(plotly_bar_net(), use_container_width=True, config = {'displayModeBar': False})
        with col2:
            subcol1, subcol2 = st.columns([1, 1])
            subcol2.metric(label=f'Total {direction_lower}flow (net):', value=metro_metric_net())
            subcol1.metric(label=f'Total {direction_lower}flow (gross):', value=metro_metric_cumulative())
        col2.plotly_chart(plotly_line_1(), use_container_width=True, config = {'displayModeBar': False})
        col2.plotly_chart(plotly_bar_total(), use_container_width=True, config = {'displayModeBar': False})
        

else:
    if mig_variable == 'Dollars per capita':
        col1, col2 = st.columns([1.5,1])
        col1.plotly_chart(dollars_person_bar_county(), use_container_width=True, config = {'displayModeBar': False})
        with col2:
            subcol1, subcol2 = st.columns([1, 1])
            subcol1.metric(label=f'Average {direction_lower}flow per capita', value=county_metric_cumulative())
            subcol2.write("")
        col2.plotly_chart(plotly_line_2_county(), use_container_width=True, config = {'displayModeBar': False})
    else:
        col1, col2 = st.columns([1.5,1])
        col1.plotly_chart(plotly_bar_net_county(), use_container_width=True, config = {'displayModeBar': False})
        with col2:
            subcol1, subcol2 = st.columns([1, 1])
            subcol1.metric(label=f'Total {direction_lower}flow (gross)', value=county_metric_cumulative())
            subcol2.metric(label=f'Total {direction_lower}flow (net)', value=county_metric_net())
        col2.plotly_chart(plotly_line_1_county(), use_container_width=True, config = {'displayModeBar': False})
        col2.plotly_chart(plotly_bar_total_county(), use_container_width=True, config = {'displayModeBar': False})

