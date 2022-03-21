# Imports
import time
# import emoji
# import string
# import logging
# import calendar
# import operator
import pandas as pd
import streamlit as st
import plotly.express as px
# from collections import Counter 
# import matplotlib.style as style
# from collections import OrderedDict
# from matplotlib import pyplot as plt
from datetime import datetime, timedelta
# from wordcloud import WordCloud, STOPWORDS 



@st.cache
def prepare_df_and_parse_date_and_time(chatc):
    text_df, error_count, error_list = pd.DataFrame(), 0, list()
    for i in range(len(chatc)):
        print("\n\nProcessing ", i, "of ", len(chatc), "...")
        try:
            x = chatc[i].split(' - ')
            print("x: ",x)
            
            y0, y1 = x[0].split(', '), x[1].split(': ')
            
            y00 = datetime.strptime(y0[0], '%d/%m/%y').date()
            y01 = datetime.strptime(y0[1], '%H:%M').time()

            min =  y01.minute
            if min >= 30:
                if(y01.hour == 23):
                    y01 = y01.replace(00, 00)
                else:
                    y01 = y01.replace(y01.hour + 1, 00)
            else:
                y01 = y01.replace(y01.hour, 00)
                
            text_df = text_df.append([[y00, y01, y1[0], y1[1]]])
            
        except:
            error_count += 1 ## x0 doesn't have required object
            #continue                                                            ## TODO: Handle this later by appending the new line to the previous line 
        
    #     # Update the streamlit progress bar
    #     percent_complete = i/len(chatc)
    #     progress_bar.progress(percent_complete)
    # percent_complete = (i+1)/len(chatc)
    # progress_bar.progress(percent_complete)
    
    try:
        col4 = text_df[4]
        text_df.drop([4], axis=1, inplace=True)
    except:
        col4 = None
    text_df.columns = ['Date', 'Time', 'Sender', 'Text']
    text_df = text_df.reset_index(drop=True)
    return text_df, error_count, error_list, col4

def total_chat_distribution(text_df):

    # contact_list = text_df.Sender.unique().tolist()
    x = text_df.groupby('Sender').count()
    
    # no_of_text = list()
    # for i in range(len(x)):
    #     # print(x, f"i: {i}\nx.iloc[1][0]: {x.iloc[1][0]}")
    #     no_of_text.append(x.iloc[i][0])

    # return contact_list, no_of_text
    return x

def weekly_chat_distribution(text_df):
    
    ## Mon=0, Tue=1, Wed=2, ... , Sun=6
    weekly_freq = [0, 0, 0, 0, 0, 0, 0] 
    for index, row in text_df.iterrows():
        day = row['Date'].weekday()
        weekly_freq[day] += 1
    weekly_freq = pd.DataFrame(weekly_freq,
                              index=["Monday",
                                     "Tuesday",
                                     "Wednesday",
                                     "Thursday",
                                     "Friday",
                                     "Saturday",
                                     "Sunday"],
                              columns=["Texts sent"])
    return weekly_freq

def hourly_chat_distribution(text_df):
    hourly_freq = [0 for i in range(24)] ## 24 0's each for 1 hour
    for index, row in text_df.iterrows():
        hour = row['Time'].hour
        hourly_freq[hour] += 1
    hourly_freq = pd.DataFrame(hourly_freq, columns=["Texts sent"])
        
    return hourly_freq




## MAIN
st.set_page_config(
     page_title="WA Chat Analyser",
     page_icon=":speech_balloon:",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

st.write("# WhatsApp Text Analyser \n###### (v2.5.45 beta)")
text_df = None

uploaded_file = st.file_uploader("Choose a file", type=[".txt"],
                                 help="Choose the exported text file")
# This blocks executes only when a file is uploaded, else not
if uploaded_file is not None:
    chat = [line.decode("utf-8") for line in uploaded_file]
    
    start_time = time.time()
    placeholder = st.empty()
    placeholder.write("Processing. Please wait...")
    
    text_df, error_count, error_list, col4 = prepare_df_and_parse_date_and_time(chat)
    placeholder.empty()
    
    st.success(f"Chat sucessfully processed! {error_count} error(s) occured while processing!")
    st.write("--- %s seconds elapsed ---" % (time.time() - start_time))


view = st.sidebar.selectbox("Choose view:", 
                 ("Home", "Total texts", "Weekly trend", "Hourly trend", "Phrase search trend"))

if view == "Total texts":
    if text_df is not None: 
        # Execute only if there's data in the dataframe
        chat_distribution_df = total_chat_distribution(text_df)
        chat_distribution_df.sort_values(by="Text", inplace=True)
        
        chat_distribution_fig = px.bar(chat_distribution_df, 
                                    title="Total texts sent",
                                    x=chat_distribution_df.index, 
                                    y="Text",
                                    text="Text",
                                    color="Text",
                                    #  color_continuous_scale="Bluered",
                                    #  color_continuous_scale="aggrnyl",
                                    color_continuous_scale="Turbo",
                                        )
        chat_distribution_fig.update_layout(xaxis=dict(showgrid=False),
                                            yaxis=dict(showgrid=False)
                                            )
        
        st.plotly_chart(chat_distribution_fig, use_container_width=True)
        st.write("--- %s seconds elapsed ---" % (time.time() - start_time))

elif view == "Weekly trend":
    if text_df is not None: 
        weekly_freq = weekly_chat_distribution(text_df)
        # st.write(weekly_freq)
        weekly_freq_fig = px.line(weekly_freq, 
                                  y="Texts sent",
                                  title="Weekly chat trends",
                                  text="Texts sent",
                                  labels=dict(index="Day of the week"))
        weekly_freq_fig.update_layout(xaxis=dict(showgrid=False),
                                      yaxis=dict(showgrid=False)
                                      )
        weekly_freq_fig.update_traces(textposition="top center")
        # TODO: Make the hover label more appealing
        st.plotly_chart(weekly_freq_fig)
        st.write("--- %s seconds elapsed ---" % (time.time() - start_time))

elif view == "Hourly trend":    
    if text_df is not None: 
        hourly_freq = hourly_chat_distribution(text_df)
        # st.write(hourly_freq)
        hourly_freq_fig = px.line(hourly_freq, 
                                  y="Texts sent",
                                  text="Texts sent",
                                  title="Hourly chat trends",
                                  labels=dict(index="Hour of the day"))
        hourly_freq_fig.update_layout(xaxis=dict(showgrid=False),
                                    yaxis=dict(showgrid=False),
                                    showlegend=False
                                    )
        hourly_freq_fig.update_traces(textposition="top center")
        # TODO: Make the hover label more appealing
        st.plotly_chart(hourly_freq_fig)
        st.write("--- %s seconds elapsed ---" % (time.time() - start_time))

elif view == "Phrase search trend":
    if text_df is not None:
        search_phrase = ""
        search_phrase = st.text_input("Enter search phrase")
        
        search_phrase_df = text_df.loc[text_df["Text"].str.lower().str.contains(search_phrase.lower())]
        search_phrase_gbdf = search_phrase_df.groupby("Sender").count()
        search_phrase_gbdf.sort_values(by="Text", inplace=True)
        result = search_phrase_gbdf.count()["Date"]
        
        if result > 0 and search_phrase != "":
            st.write("Searching for phrase: " + search_phrase)
            phrase_search_fig = px.bar(search_phrase_gbdf,
                                       x=search_phrase_gbdf.index,
                                       y="Text",
                                       title="Phrase sent by each user",
                                       text="Text",
                                       color="Text",
                                       #  color_continuous_scale="Bluered",
                                       #  color_continuous_scale="aggrnyl",
                                       color_continuous_scale="Turbo",
                                       labels=dict(Text="No. of Times Sent"))
            phrase_search_fig.update_layout(xaxis=dict(showgrid=False),
                                            yaxis=dict(showgrid=False),
                                            showlegend=False
                                            )
            st.plotly_chart(phrase_search_fig)
        else: st.write("Please enter a search phrase above")
        st.write("--- %s seconds elapsed ---" % (time.time() - start_time))
        