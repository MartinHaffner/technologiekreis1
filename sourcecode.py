
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
pd.set_option('display.max_rows', 520)


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[4]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    df_towns = pd.read_table("university_towns.txt", names=["raw"])
    df_towns.loc[df_towns["raw"].str.find("[edit]") > 0, "State"] = df_towns["raw"].str.replace('\[edit\]', '')
#    df_towns.loc[df_towns["State"].isnull(), "RegionName"] = df_towns["raw"].str.replace("(\s\([\w\s,–\-'\&\[\d\]]*\)?(\[\d+\])*)[\w\s]*", '')
    df_towns.loc[df_towns["State"].isnull(), "RegionName"] = df_towns["raw"].str.split('\s\(').str[0]
    df_towns["State"] = df_towns["State"].fillna(method="pad")
    df_towns = df_towns[df_towns["RegionName"].notnull()]
    #df_towns["RegionName"] = df_towns["RegionName"].str.replace("([\w\s]*\,\s)", "")
    return df_towns[["State", "RegionName"]]
get_list_of_university_towns()


# In[5]:


def get_gdp_data():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    xls_src = pd.ExcelFile("gdplev.xls")
    df_gdp = pd.read_excel(xls_src, "Sheet1", skiprows=7, parse_cols="E:G", names=["Year_Quarter", "GDP in billions of current dollars", "GDP"])
    return df_gdp[["Year_Quarter", "GDP"]]
get_gdp_data()


# In[6]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    df_rec = get_gdp_data()
    df_rec = df_rec.loc[df_rec["Year_Quarter"] >= "2000q1"]
    df_rec["delta"] = df_rec["GDP"].diff()
    df_rec["start"] = (df_rec["delta"] < 0) & (df_rec["delta"].shift(-1) < 0) & (df_rec["delta"].shift() >= 0)
    return df_rec.loc[df_rec["start"]]["Year_Quarter"].values[0]

get_recession_start()


# In[7]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    start_value = get_recession_start()
    df_rec = get_gdp_data()
    df_rec = df_rec.loc[df_rec["Year_Quarter"] >= start_value]
    df_rec["delta"] = df_rec["GDP"].diff()
    df_rec["end"] = (df_rec["delta"] >= 0) & (df_rec["delta"].shift() >= 0) & (df_rec["delta"].shift(2) < 0)
    return df_rec.loc[df_rec["end"]]["Year_Quarter"].values[0]
get_recession_end()


# In[10]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    start_value = get_recession_start()
    end_value = get_recession_end()
    df_rec = get_gdp_data()
    df_rec = df_rec.loc[(df_rec["Year_Quarter"] >= start_value) & ((df_rec["Year_Quarter"] <= end_value))]    
    return df_rec.sort_values("GDP").head(1)["Year_Quarter"].values[0]
get_recession_bottom()


# In[8]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df_house = pd.read_csv("City_Zhvi_AllHomes.csv")
    target_list = []
    for year in range(2000, 2017):
        for quarter in range(4):
            if (year==2016) & (quarter==3):
                continue
            if (year==2016) & (quarter==2):
                src_list = ["2016-07", "2016-08"]
            else:
                src_list = []
                for src in range(3):
                    src_list += ["{0}-{1:02d}".format(year, quarter*3+src+1)]
            target_var = "{0}q{1}".format(year, quarter+1)
            df_house[target_var] = df_house[src_list].mean(axis=1)
            target_list += [target_var]
    df_house = df_house[["RegionName", "State"] + target_list]
    df_house = df_house.set_index(["State", "RegionName"])
    return df_house
convert_housing_data_to_quarters()


# In[23]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    df_house = convert_housing_data_to_quarters()
    rec_start = get_recession_start()
    rec_bottom = get_recession_bottom()
    df_house = df_house.loc[:,rec_start:rec_bottom]
    df_house = df_house.reset_index()
    df_house["State_long"] = df_house["State"].apply(lambda x: states[x])
    # df_house = df_house.set_index(["State_long", "RegionName"])
    df_university = get_list_of_university_towns()
    df_university["is_university_town"] = True
    df_university = df_university.set_index(["State", "RegionName"])
    df_house = df_house.join(df_university, how="left", on=(["State_long", "RegionName"]))
    df_house["decline"] = df_house[rec_bottom] / df_house[rec_start]
    # df_university["State2"] = df_university["State"].apply(lambda x: )
    df_house["is_university_town"] = df_house["is_university_town"].fillna(value=False)
    df_house = df_house[["State", "RegionName", "decline", "is_university_town"]]
    df_university = df_house.loc[df_house["is_university_town"]]
    df_non_university = df_house.loc[df_house["is_university_town"] == False]
    from scipy import stats
    ttest_result = stats.ttest_ind(df_university["decline"], df_non_university["decline"], nan_policy='omit')
    result = [None, None, None]
    result[0] = (ttest_result.pvalue < 0.01)
    result[1] = ttest_result.pvalue
    if df_university["decline"].mean() > df_non_university["decline"].mean():
        result[2] = "university town"
    else:
        result[2] = "non-university town"
    return tuple(result)
run_ttest()
#pd.DataFrame.join?


# In[ ]:





# In[ ]:




