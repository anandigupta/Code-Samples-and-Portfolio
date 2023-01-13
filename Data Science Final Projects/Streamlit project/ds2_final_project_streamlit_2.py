### Stream lit main
#import relevant libraries
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import chart_studio.plotly as py
import plotly.offline as po
import plotly.graph_objs as pg
import matplotlib.pyplot as plt
import plotly.express as px



st.title("Climate Change Dashboard: Global Impact")
st.title("Anandi Gupta")

"""
Climate change has been declared the "single biggest health threat facing humanity," according to the World Health Organization ([link](https://www.cbsnews.com/news/climate-change-health-threat-who/)). Increasingly frequent climate disasters such as heat waves, storms and floods, as well as the disruption of food systems, the spread of diseases from animal populations, food- and water-borne illnesses, and related mental health issues pose major threats to human health.

Although climate change is a global crisis, it will disproportionately affect certain regions, in part due to geographic reasons that make them more vulnerable to extreme weather events, as well as because of socio-economic factors such as the reliance on natural resource intensive industries such as agriculture and the lack of strong institutions and coping capacity. This dashboard enables users to explore geographic differences in contributions to climate change as well as the direct and indirect effects of climate change (particularly on health).
"""

### Set url names

#URLs - IMF API
#Surface temp
url1 = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_3_1_Climate_Indicators_Annual_Mean_Global_Surface_Temperature/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"

#Climate related disasters
url2b = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_11_1_Physical_Risks_Climate_related_disasters_frequency/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
url2 = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_11_1_Physical_Risks_Climate_related_disasters_frequency/FeatureServer/0/query?where=1%3D1&outFields=Country,ISO2,ISO3,Indicator,Unit,Source,F2016,F2017,F2018,F2019,F2020,F2021&outSR=4326&f=json"
#inform risk
url3 = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_11_3_Physical_Risks__Index_for_Risk_Management/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"

## URLs - Our world in data
#Emissions
url4 = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"

#URLs - WHO API
#risk of premature death from NCD
url6 = "https://ghoapi.azureedge.net/api/NCDMORT3070"

#Diarrheoa deaths from inadequate water
url7 = "https://ghoapi.azureedge.net/api/WSH_10_WAT"

#Malnutrition - Prevalence of underweight children under 5 years of age   (% weight-for-age <-2 SD) (%)
url8 = "https://ghoapi.azureedge.net/api/NUTRITION_WA_2"


######## Read in data from IMF API

@st.cache
def read_in_imf_api(url):

    r = requests.get(url)
    # 1 Return JSON encoded response (converts JSON to Python dictionary)
    x = r.json()
    # 2 convert to df based on keys
    df = pd.DataFrame.from_dict(r.json()["features"])
    # 3 normalize as output is nested dictionary
    output = pd.json_normalize(df['attributes'])
    final_output = output.copy()
    #return df
    return final_output

df_surf_temp_raw = read_in_imf_api(url1)
df_disasters_raw = read_in_imf_api(url2)
df_disasters_viz_raw = read_in_imf_api(url2b)
df_risk_raw = read_in_imf_api(url3)

df_surf_temp = df_surf_temp_raw.copy()
df_disasters = df_disasters_raw.copy()
df_disasters_viz = df_disasters_viz_raw.copy()
df_risk = df_risk_raw.copy()

## Initial data manipulation
#surface temp data
df_surf_temp = df_surf_temp[['Country', 'ISO3', 'F2016','F2017', 'F2018', 'F2019', 'F2020']]
#calculate five year avgs
df_surf_temp['five_year_avg'] = (df_surf_temp.F2016 + df_surf_temp.F2017 + df_surf_temp.F2018 + df_surf_temp.F2019 + df_surf_temp.F2020)/5

#Disaster data
#keep total disasters
df_disasters = df_disasters[df_disasters['Indicator'] == "Climate related disasters frequency, Number of Disasters: TOTAL"].reset_index()
#missing when no disasters - replace with 0s
df_disasters = df_disasters.replace(np.nan, 0)
#calculate five year averages
df_disasters['five_year_avg'] = (df_disasters.F2016+ df_disasters.F2017 + df_disasters.F2018 + df_disasters.F2019 + df_disasters.F2020)/5

#subset risk data based on indicators
df_inform_risk = df_risk[df_risk['Indicator'] == "Climate-driven INFORM Risk Indicator"].reset_index()
df_hazard= df_risk[df_risk['Indicator'] == "Climate-driven Hazard & Exposure"].reset_index()
df_coping_capacity= df_risk[df_risk['Indicator'] == "Lack of coping capacity"].reset_index()
df_vulnerability= df_risk[df_risk['Indicator'] == "Vulnerability"].reset_index()

#read in our world in data github
@st.cache
def read_in_owid():
    df = pd.read_csv(url4)
    final_output = df.copy()
    #return df
    return final_output


df_emissions_raw = read_in_owid()
df_emissions = df_emissions_raw.copy()

df_emissions = df_emissions[['iso_code', 'country', 'year', 'co2', 'co2_per_capita', 'energy_per_gdp', 'energy_per_capita', 'population']]

######## Read in data from WHO API
@st.cache
def read_in_who_api(url):

    r = requests.get(url)
    # 1 Return JSON encoded response (converts JSON to Python dictionary)
    x = r.json()
    # 2 convert to df based on keys
    df = pd.DataFrame.from_dict(r.json()["value"])
    # 3 normalize as output is nested dictionary
    final_output = df.copy()
    #return df
    return final_output

df_ncd_deaths_raw = read_in_who_api(url6)
df_ncd_deaths = df_ncd_deaths_raw.copy()
#filter by relevant dimensions
df_ncd_deaths = df_ncd_deaths[(df_ncd_deaths['TimeDimensionValue'] == "2019") & (df_ncd_deaths['Dim1'] == "BTSX")]

df_diarrhea_deaths_raw = read_in_who_api(url7)
df_diarrhea_deaths = df_diarrhea_deaths_raw.copy()
#filter by relevant dimensions
df_diarrhea_deaths = df_diarrhea_deaths[(df_diarrhea_deaths['TimeDimensionValue'] == "2016") & (df_diarrhea_deaths['Dim1'] == "BTSX") & (df_diarrhea_deaths['Dim2'] == "YEARSALL")]
#merge on population from OWID data and calculate per capita rates
df_diarrhea_deaths = df_diarrhea_deaths.merge(df_emissions[['iso_code','population']], left_on='SpatialDim', right_on='iso_code')
df_diarrhea_deaths['deaths_per_100k'] = (df_diarrhea_deaths['NumericValue']/df_diarrhea_deaths['population'])*100000

df_malnutrition_raw = read_in_who_api(url8)
df_malnutrition = df_malnutrition_raw.copy()
#filter by relevant dimensions and keep only most recent year
df_malnutrition = df_malnutrition.sort_values(by=['SpatialDim', 'TimeDim'], ascending=False).groupby('SpatialDim').first().reset_index()

#### Create relevant sections and corresponding plots using plotly


if st.sidebar.checkbox("Global Climate Change Trends", key="section1"):
    st.header("Global Climate Change Trends")
    answer0 = st.selectbox(label="Choose indicator",
    options=("CO2 Emissions", "Surface Temperatures", "Climate Disasters"))

    if answer0 == "CO2 Emissions":
        df_emissions_viz = df_emissions[df_emissions['country'] == "World"]
        df_emissions_viz = df_emissions_viz[df_emissions_viz['year'] > 1980].reset_index()
        fig = px.bar(df_emissions_viz, x=df_emissions_viz['year'], y=df_emissions_viz['co2'], labels={'co2':'Global CO2 Emissions', "year": "Year"},
                 title='CO2 Emissions Over Time')
        st.plotly_chart(fig, use_container_width=True)
        st.write("Human emissions of carbon dioxide and other greenhouse gases are a primary driver of climate change, and have been increasing steadily since the 1980s.")

    elif answer0 == "Surface Temperatures":
        df_surf_viz = df_surf_temp_raw[df_surf_temp_raw['Country'] == "World"]
        df_surf_viz = pd.wide_to_long(df_surf_viz, stubnames='F', i=['Indicator'], j='year',
                        sep='', suffix=r'\w+').reset_index()
        df_surf_viz= df_surf_viz.rename(columns = {'F':'Temperature_Change'})
        df_surf_viz = df_surf_viz[df_surf_viz['year'] > 1980]
        fig = px.bar(df_surf_viz, x=df_surf_viz['year'], y=df_surf_viz['Temperature_Change'], labels={'Temperature_Change':'Temperature Change (Degrees Celsius)', "year": "Year"},
                 title='Temperature Changes Over Time (Relative to 1951-1980 Baseline Period)')
        st.plotly_chart(fig, use_container_width=True)
        st.write("Average global surface temperatures have increased by more than 1 degree celsius since the 1951-1980 baseline period. Scientists have declared that a 2 degree celsius increase in global mean temperatures (i.e. surface and ocean temperatures) from pre-industrial levels would result in 'catastropic' impacts and 'would change our climate in ways not seen for the last several hundred thousand years.'")

    elif answer0 == "Climate Disasters":
        df_disasters_viz = df_disasters_viz_raw.groupby(['Indicator']).sum().reset_index()
        df_disasters_viz = pd.wide_to_long(df_disasters_viz, stubnames='F', i=['Indicator'], j='year',
                        sep='', suffix=r'\w+').reset_index()
        df_disasters_viz = df_disasters_viz[df_disasters_viz['Indicator'] != "Climate related disasters frequency, Number of Disasters: TOTAL"]
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Drought"), "disaster_type"] = "Drought"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Flood"), "disaster_type"] = "Flood"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Extreme temperature"), "disaster_type"] = "Extreme temperature"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Landslide"), "disaster_type"] = "Landslide"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Storm"), "disaster_type"] = "Storm"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Wildfire"), "disaster_type"] = "Wildfire"
        fig = px.bar(df_disasters_viz, x=df_disasters_viz['year'], y=df_disasters_viz['F'], color=df_disasters_viz['disaster_type'], labels={'F':'Number of Disasters', 'year': 'Year', 'disaster_type': 'Type of Disaster'},
                 title='Climate Disasters Over Time', width=900, height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.write("The number of climate-related disasters has tripled over the last 40 years, resulting in millions of deaths and massive economic losses ([link](https://www.bbc.com/news/science-environment-58396975)). Rising temperatures due to climate change have driven this increase, as warmer temperatures are associated with longer and hotter heatwaves, more persistent droughts, dry conditions that provide fuel for wildfires, and more extreme rainfall events ([link](https://www.bbc.com/news/science-environment-58073295)).")

if st.sidebar.checkbox("Climate Change Contributions", key="section2"):
    st.header("Climate Change Contributions")

    answer5 = st.selectbox(label="Choose indicator",
    options=("CO2 Emissions Per Capita", "Energy Consumption Per Capita"))
    answer6 = st.slider('Choose time period', 2016, 2020, 2016)
    # answer6 = st.selectbox(label="Choose time period",
    # options=(2016, 2017, 2018, 2019, 2020))

    def cc_causes_maps(var):
        df_emissions2 = df_emissions[df_emissions['year'] == answer6]

        data = dict(type='choropleth',
                locations = df_emissions2['iso_code'],
                z = df_emissions2[var],
                text = df_emissions2['country'])

        layout = dict(title = answer5,
                  geo = dict(showframe = False,
                           projection = {'type':'robinson'},
                           showlakes = True,
                           lakecolor = 'rgb(0,191,255)'))
        x = pg.Figure(data = [data], layout = layout)
        st.plotly_chart(x, use_container_width=True)

    if answer5 == "CO2 Emissions Per Capita":
        cc_causes_maps('co2_per_capita')
        st.write("There exist large inequalities in CO2 per capita emissions across the world. The major oil producing countries in the Middle East (such as Qatar, Kuwait, United Arab Emirates and Saudi Arabia) have some of the largest per capita CO2 emissions in the world. However, these countries have relatively low population sizes, and thus their total annual emissions are low. Among the more populous countries, the United States, Australia, and Canada have the highest per capita emissions and therefore large total annual emissions as well.")

    elif answer5 == "Energy Consumption Per Capita":
        cc_causes_maps('energy_per_capita')
        st.write("Energy consumption per capita varies drastically across the world. Iceland has the highest per capita energy consumption in the world, followed by other Nordic countries with cold climates such as Norway and Finland, and several of the major oil producing countries such as Qatar and Kuwait in the Middle East and Trinidad and Tobago. However, these countries have relatively low population sizes, and thus their total annual energy consumption is relatively low. Among the more populous countries, Canada, the United States, and Australia have the highest per capita energy consumption and are thus are major contributors to total energy consumption as well.")

if st.sidebar.checkbox("Climate-Driven Risks", key="section3"):
    st.header("Climate-Driven Risks")
    answer3 = st.selectbox(label="Choose indicator",
    options=("Climate-driven INFORM Risk Indicator", "Climate-driven Hazard & Exposure", "Lack of coping capacity", "Vulnerability"))

    answer4 = st.selectbox(label="Choose time period",
    options=("F2020", "F2021"))

    def cc_effects(dataset, var):
        data = dict(type='choropleth',
                locations = dataset['ISO3'],
                z = dataset[var],
                text = dataset['Country'])

        layout = dict(title = answer3,
                  geo = dict(showframe = False,
                           projection = {'type':'robinson'},
                           showlakes = True,
                           lakecolor = 'rgb(0,191,255)'))
        x = pg.Figure(data = [data], layout = layout)
        st.plotly_chart(x, use_container_width=True)

    if answer3 == "Climate-driven INFORM Risk Indicator":
        cc_effects(df_inform_risk, answer4)
        st.write("The INFORM Risk Index is a global, open source risk assessment for crises and disasters. The Climate-driven INFORM Risk is an adaptation of the INFORM Risk Index, adjusted by IMF staff to distill and centralize on climate-driven risks. It has three dimensions: climate-driven hazard & exposure, vulnerability, and lack of coping capacity ([link](https://climatedata.imf.org/pages/fi-indicators)). Overall, Somalia has the highest aggregate INFORM Risk Score. Several other African countries, as well as countries in the Indian subcontinent, Southeast Asia, and South America have high climate-driven risk scores.")

    elif answer3 =="Climate-driven Hazard & Exposure":
        cc_effects(df_hazard, answer4)
        st.write("India, China, and Somalia have the highest climate-driven hazard and exposure risks.")

    elif answer3 =="Lack of coping capacity":
        cc_effects(df_coping_capacity, answer4)
        st.write("Several African countries have extremely low coping capacities for mitigating the consequences of climate-change, with Chad, South Sudan, and Somalia being some of the least equipped.")

    elif answer3 =="Vulnerability":
        cc_effects(df_vulnerability, answer4)
        st.write("Several African countries such as Somalia, Central African Republic, and South Sudan, as well as conflict zones such as Syria and Afghanistan, are highly vulnerable to the effects of climate change.")

if st.sidebar.checkbox("Direct Effects of Climate Change", key="section4"):
    st.header("Direct Effects of Climate Change")

    # "### Select box"
    answer1 = st.selectbox(label="Choose indicator",
    options=("Changes in Surface Temperature (relative to 1951-1980 baseline)", "Climate Disasters"))

    answer2 = st.selectbox(label="Choose time period",
    options=("F2016", "F2017", "F2018", "F2019", "F2020", "five_year_avg"))

    def cc_effects(dataset, var):
        data = dict(type='choropleth',
                locations = dataset['ISO3'],
                z = dataset[var],
                text = dataset['Country'])

        layout = dict(title = answer1,
                  geo = dict(showframe = False,
                           projection = {'type':'robinson'},
                           showlakes = True,
                           lakecolor = 'rgb(0,191,255)'))
        x = pg.Figure(data = [data], layout = layout)
        st.plotly_chart(x, use_container_width=True)

    if answer1 == "Changes in Surface Temperature (relative to 1951-1980 baseline)":
        cc_effects(df_surf_temp, answer2)
        st.write("Surface temperatures have risen globally since the baseline period, with Russia, other ex-Soviet Union countries, and Nordic countries such as Sweden and Finland seeing five-year average temperatures for 2016-2020 rise by more than 2 degrees celsius since the baseline period.")

    elif answer1 =="Climate Disasters":
        cc_effects(df_disasters, answer2)
        st.write("USA, India, and China have recorded the highest number of climate related disasters in recent years.")

if st.sidebar.checkbox("Indirect Effects of Climate Change: Health Outcomes", key="section5"):
    st.header("Indirect Effects of Climate Change: Health Outcomes")

    # "### Select box"
    answer7 = st.selectbox(label="Choose indicator",
    options=("Probability of dying between age 30-70 from cardiovascular disease, cancer, diabetes, or chronic respiratory disease", "Malnutrition - Prevalence of underweight children under 5 years of age (% weight-for-age <-2 SD) (%)", "Diarrhea Deaths Per 100,000 Population from Inadequate Water"))

    def cc_health(dataset, var):
        data = dict(type='choropleth',
                locations = dataset['SpatialDim'],
                z = dataset[var],
                text = dataset['SpatialDim'])

        layout = dict(title = answer7,
                  geo = dict(showframe = False,
                           projection = {'type':'robinson'},
                           showlakes = True,
                           lakecolor = 'rgb(0,191,255)'))
        x = pg.Figure(data = [data], layout = layout)
        st.plotly_chart(x, use_container_width=True)


    if answer7 == "Probability of dying between age 30-70 from cardiovascular disease, cancer, diabetes, or chronic respiratory disease":
        cc_health(df_ncd_deaths, 'NumericValue')
        st.write("Frequent heat waves, higher air pollution, and changes to food production due to climate change have exacerbated mortality due to non-communicable diseases. Countries in Africa, the Indian subcontinent, and Southeast Asia have some of the highest rates of premature deaths due to NCDs.")

    elif answer7 =="Malnutrition - Prevalence of underweight children under 5 years of age (% weight-for-age <-2 SD) (%)":
        cc_health(df_malnutrition, 'NumericValue')
        st.write("Changes in temperature and precipitation are associated with disruptions to crop yields and food systems pose, which pose challenges to food security and nutrition. The World Food Programme states that by 2050, the risk of hunger and malnutrition could rise by 20 percent if the global community fails to act now to mitigate and prevent the adverse effects of climate change ([link](https://www.wfp.org/publications/climate-crisis-and-malnutrition-case-acting-now#:~:text=Climate%20change%20is%20a%20long,adverse%20effects%20of%20climate%20change.)). Developing countries in Africa, the Indian subcontinent, and Southeast Asia already have high rates of malnutrition, and will be most impacted by changes to crop yields and food production.")

    elif answer7 =="Diarrhea Deaths Per 100,000 Population from Inadequate Water":
        cc_health(df_diarrhea_deaths, 'deaths_per_100k')
        st.write("Research shows that changes in climate that lead to an increase in temperature and a decrease in precipitation are associated with an increase in diarrheal disease ([link](https://jamanetwork.com/journals/jama/article-abstract/1687591)). Countries in Africa countries have some of the highest death rates from diarrhea, and these will likely be exacerbated by climate change.")

if st.sidebar.checkbox("Policy Implications", key="section6"):
    st.header("Policy Implications")
    """
    Climate change is unequivocally exacerbating global inequalities. Wealthier countries have historically contributed to the majority of global emissions, and reaped the direct economic benefits associated with fossil fuel use. However, research shows that for most poor countries (which are overwhelmingly located in hotter areas such as Africa, the Indian Subcontinent, and Southeast Asia, and rely highly on the agriculture sector), there is >90% likelihood that per capita GDP is lower today than if global warming had not occurred ([link](https://www.pnas.org/doi/10.1073/pnas.1816020116)). These countries additionally have limited coping capacity for mitigating the impacts of extreme weather events, which puts their populations at extreme risk for premature deaths and poor health outcomes. Within these countries, climate change will again have unequal impacts, such that the poorest will suffer the most.

    Progressive policies are thus imperative for addressing the unequal distribution of climate change impacts. Potential policy tools include:
    1) Stricter emissions targets for wealthier countries
    2) Relief packages for poorer countries facing climate disasters and provision of asylum to climate refugees
    3) Reduction of fossil fuel subsidies and a reallocation of budgets to progressive welfare distribution within countries
    4) Carbon pricing and reinvestment of revenues into healthcare and other essential infrastructure

    This list is not exhaustive, and there remains an urgent need for the development of new and innovative policy tools to combat the unequal global impacts of climate change.

    Suggested additional resources for users:

    1) [G20 Insights - Policy options for a socially balanced climate policy](https://www.g20-insights.org/policy_briefs/policy-options-socially-balanced-climate-policy/)
    2) [U.S. EPA - Tools for Climate Change Adaption](https://www.epa.gov/arc-x/tools-climate-change-adaptation)
    3) [IPCC Special Report: Global Warming of 1.5 Degrees Celsius](https://www.ipcc.ch/sr15/chapter/spm/)
    """
