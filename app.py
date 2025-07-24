# =======================================================================================================================
# Script Purpose:
# This Streamlit dashboard is designed to analyze and visualize ticket data from CSV files,
# specifically focusing on two datasets: "sc_task.csv" and "incident.csv".
# It allowss users to:
# - Upload multiple CSV files.
# - Filter data by assigned agent and date.
# - View metrics like total tickets, closed/completed tickets, and ticket statuses.
# - Display charts and graphs for insights into ticket volume, agent performance, priority levels, categories, and daily tickets trends.
# The dashboard supports both summary and detailed data views to assists in performance monitoring and decision-making.
# ----------------------------------------------------------------------------------------------------------------------
#
# Author: Thanh Nguyen
# Last revised: 6/5/25 - Thanh Nguyen
# Contact: bnguyen@fhlbdm.com
#
#
# This Streamlit dashboard was developed by Thanh Nguyen to support data-driven decision
# making in IT service management. It is designed to help IT operations teams, service desk
# managers quickly assess ticket trends, agent performance, and incident/ task metrics
# from CSV exports.
#====================== Import Necessary Libraries =======================

import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
import time
from streamlit_option_menu import option_menu
from datetime import datetime


# ======================= Streamlit Page Configuration==========================
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Report page!!", page_icon="chart_with_upwards_trend",layout="wide")
st.title(":chart_with_upwards_trend: Report Dashboard")

# reduce the space top of the page
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)



# ====================== File Uploader ==========================
path = st.file_uploader("Choose a CSV file", accept_multiple_files = True)

# Loop through all uploaded files
for i in range(len(path)):
        df = pd.read_csv(path[i])        
        df = pd.DataFrame(df)
       #st.write(df, use_container_width = True)


        # Convert datetime to just date (MM/DD/YYYY)
#        df['opened_at'] = df['opened_at'].apply(
#            lambda x: time.strftime('%m/%d/%Y', time.strptime(x, '%m/%d/%Y %H:%M:%S %p'))
#        )


        # =============== Logic for sc_task.csv =================
        if path[i].name == "sc_task.csv":
            # Sidebar filter: Agent
            person =  st.sidebar.multiselect(
                "SELECT AGENT:",
                options = df["assigned_to"].unique(),
                default = df["assigned_to"].unique(),      
            )
    
            # Sidebar filter: Date
            date = st.sidebar.multiselect(
                "SELECT DATE:",
                options = df['opened_at'].unique(),
                default = df['opened_at'].unique(),
            )
    
            # Filter the dataframe
            df_selection = df.query(
                "assigned_to==@person & opened_at==@date"

            )
 
            # Count tickets per agent    
            new_df = df_selection[['assigned_to']]
            value_counts = new_df['assigned_to'].value_counts()
            value_counts_df = pd.DataFrame(value_counts).reset_index()
            value_counts_df.columns = ['agent_name', 'ticket_number']
            value_counts_df2 = value_counts_df


            # Count tickets by priority
            priority_count = df_selection.groupby(by =['priority']).count()[["assigned_to"]].sort_values(by="assigned_to")
            priority_df = pd.DataFrame(priority_count).reset_index()
            priority_df.columns = ['priority_level', 'number']

            
            # Count tickets by date
            df_name = df_selection['assignment_group']           
            df_time = df_selection['opened_at']    
            df_time= pd.to_datetime(df_time)                                  
            df_time = df_time.dt.date   
            df_time_concated = pd.concat([df_name,df_time],axis = 1)
            df_time_count = df_time_concated.groupby(by =['opened_at']).count()[["assignment_group"]].sort_values(by="assignment_group")
            df_time_count = pd.DataFrame(df_time_count).reset_index()
            df_time_count.columns = ['Day','Number']    
            df_time_count = df_time_count.sort_values(by=['Day'])

            # ========================= Home Dashboard =============================
            def Home():
                with st.expander("View Excel Dataset"):
                    showdata = st.multiselect(
                        "Filter: ", 
                        df_selection.columns, 
                        default = ["number","priority","state","short_description","assignment_group","assigned_to","opened_at"]
                    )
                    st.dataframe(df_selection[showdata],use_container_width= True)


                
                # Summary Metrics
                total_ticket = int(pd.Series(df_selection['priority']).count())
                total_ticket_CC = int(pd.Series((df_selection['state'] == 'Closed Complete')).sum())
                total_ticket_CK = int(pd.Series((df_selection['state'] == 'Closed Skipped')).sum())
                first_date_in_data = min(df_selection['opened_at'])
                last_date_in_data = max(df_selection['opened_at'])


                col1, col2 = st.columns(2,gap = 'small')
                with col1:
                    st.info('From:')
                    st.metric(label= "Date",value=first_date_in_data)
                with col2:
                    st.info('To:')
                    st.metric(label= "Date", value=last_date_in_data)


                col1,col2,col3= st.columns(3,gap='small')
                with col1:
                    st.info('Total Ticket')
                    st.metric(label="Total", value =f"{total_ticket:,.0f}")       
                with col2:
                    st.info('Total Closed Completed Ticket')
                    st.metric(label= "Total", value = f"{total_ticket_CC:,.0f}")
                with col3:
                    st.info('Total Closed Skipped Ticket')
                    st.metric(label = 'Total', value = f"{total_ticket_CK:,.0f}")


            # ============================ Ticket Visualization Graphs ==============================
            def graphs():
                # Bar chart of tickets per agent
                df_selection["number_of_ticket"] = df_selection["assignment_group"]
                ticket_by_agent =(
                    df_selection.groupby(by =['assigned_to']).count()[["number_of_ticket"]].sort_values(by="number_of_ticket")
                )
                fig_ta = px.bar(
                    ticket_by_agent,
                    x ="number_of_ticket",
                    y =ticket_by_agent.index,
                    orientation="h",
                    title = "<b> Ticket Taken by Agent </b>",
                    color_discrete_sequence = ['#0083B8']*len(ticket_by_agent)          
                )
                fig_ta.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="black"),
                    yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show y-axis grid and set its color  
                    paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
                    xaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Show x-axis grid and set its color                                 
                )

      
                # Line chart of ticket numbers
                fig_tic =px.line(
                    value_counts_df,
                    x = "agent_name",
                    y = "ticket_number",
                    orientation = "v",
                    title= "<b> Tickets Taken by Agent </b>",        
                )
                fig_tic.update_layout(
                    xaxis=dict(tickmode="linear"),
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=(dict(showgrid=False))
                )
 
                # Show charts
                left,right,center=st.columns(3)
                left.plotly_chart(fig_ta,use_container_width = True)
                right.plotly_chart(fig_tic, use_container_width = True)

                # Pie chart of ticket share
                with center:
                    fig = px.pie(value_counts_df, values = 'ticket_number', names = 'agent_name', title = 'Percentage Of Tickets Taken'  )                                         
                    fig.update_layout(legend_title = 'agent_name', legend_y= 0.9)
                    fig.update_traces(textinfo = 'percent+label', textposition = 'inside')
                    st.plotly_chart(fig, use_container_width = True, theme = None)


            # ===================== Priority and Daily Count Graphs =======================
            def graphs2():
                # Bar chart for priority
                fig_test = px.bar(
                       priority_df,
                        x ="priority_level",
                        y ="number",
                        color = "priority_level",
                        pattern_shape ="priority_level",
                        pattern_shape_sequence = [".","x","+"]
                )

                # Line chart for tickets by day
                fig_2 = px.line(
                        df_time_count,
                        x = 'Day',
                        y = 'Number',
                        orientation = "v",
                        title = "<b> Number Of Tickets by Day",                 
                )         
                fig_2.update_layout(
                        xaxis=dict(tickmode="linear"),
                        plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=(dict(showgrid=False))
                )


                # Show charts
                left,right,center=st.columns(3)
                left.plotly_chart(fig_test,use_container_width = True)
                right.plotly_chart(fig_2,use_container_width = True) 

                # Pie chart for priority distribution    
                with center:
                    fig = px.pie(priority_df, values = 'number', names = 'priority_level', title = 'Percentage Of Ticket Priority'  )                                         
                    fig.update_layout(legend_title = 'priority_level', legend_y= 0.9)
                    fig.update_traces(textinfo = 'percent+label', textposition = 'inside')
                    st.plotly_chart(fig, use_container_width = True, theme = None)  
            

            # ================ Sidebar Navigation ====================
            def sideBar():
                    with st.sidebar:
                        selected = option_menu(                
                            menu_title = "Main menu",
                            options = ["Home"],
                            icons = ["house"],
                            menu_icon = "cast",
                            default_index = 0                
                        )
                    if selected == "Home":
                        #st.subheader("fPage: {selected}")
                        Home()
                        graphs()
                        graphs2()                   
            sideBar()

        # ===================== Logic for incident.csv ==========================    
        if path[i].name == "incident.csv":

            # Sidebar filter
             person =  st.sidebar.multiselect(
             "SELECT AGENT:",
             options = df["assigned_to"].unique(),
             default = df["assigned_to"].unique(),      
             )
             date = st.sidebar.multiselect(
                "SELECT DATE:",
                options = df['opened_at'].unique(),
                default = df['opened_at'].unique(),
                )
             df_selection = df.query(
                "assigned_to==@person & opened_at==@date"
             )

             with st.expander("View Excel Dataset"):
                    showdata = st.multiselect(
                        "Filter: ", 
                        df_selection.columns, 
                        default = ["number","opened_at","short_description","caller_id","priority","state","category","assignment_group","assigned_to","sys_updated_on","sys_updated_by"]
                    )
                    st.dataframe(df_selection[showdata],use_container_width= True)


             # Prepare and group data
             df_name = df_selection['assignment_group']           
             df_time = df_selection['opened_at']    
             df_time= pd.to_datetime(df_time)                                                                    
             df_time = df_time.dt.date
             df_time_concated = pd.concat([df_name,df_time],axis = 1)
             df_time_count = df_time_concated.groupby(by =['opened_at']).count()[["assignment_group"]].sort_values(by="assignment_group")
             df_time_count = pd.DataFrame(df_time_count).reset_index()
             df_time_count.columns = ['Day','Number']

        
             state_counts = df_selection.groupby(by =['state']).count()[["assigned_to"]].sort_values(by="assigned_to")
             state_counts_df = pd.DataFrame(state_counts).reset_index()
             state_counts_df.columns = ['State', 'Total']


             category_count_df = df_selection.groupby(by =['category']).count()[["assignment_group"]].sort_values(by="assignment_group")
             category_count_df = pd.DataFrame(category_count_df).reset_index()
             category_count_df.columns = ['Category','Total']


             aggregated_data_category = df_selection.groupby(['assigned_to', 'category']).agg(
                 category_count = ('category','count')         
             )
             aggregated_data_category = pd.DataFrame(aggregated_data_category).reset_index()
        

             priority_count_df = df_selection.groupby(by =['priority']).count()[["assignment_group"]].sort_values(by="assignment_group")
             priority_count_df = pd.DataFrame(priority_count_df).reset_index()
             priority_count_df.columns = ['Priority','Total']



             aggregated_data = df_selection.groupby(['assigned_to', 'priority']).agg(
                priority_count=('priority', 'count'),               
             )
             aggregated_data = pd.DataFrame(aggregated_data).reset_index()



             # Date metrics
             first_date_in_data = min(df_selection['opened_at'])
             last_date_in_data = max(df_selection['opened_at'])
             col1, col2 = st.columns(2,gap = 'small')
             with col1:
                    st.info('From:')
                    st.metric(label= "Date",value=first_date_in_data)
             with col2:
                    st.info('To:')
                    st.metric(label= "Date", value=last_date_in_data)



             # Count ticket states
             if 'On Hold' in state_counts_df.values :         
                 total_on_hold = state_counts.at['On Hold','assigned_to']
             else:
                 total_on_hold = 0

             if 'In Progress' in state_counts_df.values :
                total_in_progress = state_counts.at['In Progress','assigned_to']
             else:
                 total_in_progress = 0

             if 'Resolved' in state_counts_df.values :
                 total_resolved = state_counts.at['Resolved','assigned_to']
             else:
                 total_resolved = 0

             if 'Closed' in state_counts_df.values:   
                 total_closed = state_counts.at['Closed', 'assigned_to']
             else:
                 total_closed = 0

             total_number_ticket = total_on_hold+total_in_progress+total_resolved+total_closed


             # Show ticket metrics
             col1,col2,col3,col4,col5 = st.columns(5,gap='small')
             with col1:
                 st.info("Number of tickets")
                 st.metric(label = "Total", value = f"{total_number_ticket:,.0f}")
             with col2:
                 st.info('Tickets on hold')
                 st.metric(label = "Total", value = f"{total_on_hold:,.0f}")
             with col3:
                 st.info('Tickets In Progress')
                 st.metric(label = "Total", value = f"{total_in_progress:,.0f}")
             with col4:
                 st.info('Tickets Resolved')
                 st.metric(label = "Total", value = f"{total_resolved:,.0f}")
             with col5:
                 st.info('Tickets Closed')
                 st.metric(label = "Total", value = f"{total_closed:,.0f}")


             # Sort the dataframe to fit the px.line graph function
             df_time_count = df_time_count.sort_values(by=['Day'])


             # Create visualizations
             fig_1 = px.line(
                df_time_count,
                x = 'Day',
                y = 'Number',
                orientation = "v",
                title = "<b> Number Of Tickets by Day",              
             )             
             fig_1.update_layout(
                xaxis=dict(tickmode="linear"),
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=(dict(showgrid=False))
             )

             fig_2 = px.bar(
                aggregated_data,
                x = 'assigned_to',
                y = 'priority_count',
                color = 'priority',
                pattern_shape="priority", 
                pattern_shape_sequence=[".", "x", "+"]             
             )

             fig_3 = px.bar(
                    aggregated_data_category,
                    x= 'assigned_to',
                    y= 'category_count',
                    color = 'category',
                    pattern_shape='category',
                    pattern_shape_sequence=['.','x','+']                     
                 )

             # Display charts
             left,right,center = st.columns(3)
             left.plotly_chart(fig_1,use_container_width = True)
             right.plotly_chart(fig_2,use_container_width = True)
             center.plotly_chart(fig_3,use_containter_width = True)

             # Create visualizations
             fig_4 = px.pie(category_count_df, values = 'Total', names = 'Category',title = 'Category Percentage')
             fig_4.update_layout(legend_title = 'Category', legend_y= 0.9)
             fig_4.update_traces(textinfo = 'percent+label', textposition = 'inside')


             fig_5 = px.pie(priority_count_df, values = 'Total', names = 'Priority',title = 'Priority Percentage')
             fig_5.update_layout(legend_title = 'Priority', legend_y= 0.9)
             fig_5.update_traces(textinfo = 'percent+label', textposition = 'inside')


             fig_6 = px.pie(state_counts_df, values = 'Total', names = 'State',title = 'State Percentage')
             fig_6.update_layout(legend_title = 'State', legend_y= 0.9)
             fig_6.update_traces(textinfo = 'percent+label', textposition = 'inside')

             # Display charts
             left,right,center = st.columns(3)
             left.plotly_chart(fig_4,use_container_width = True)
             right.plotly_chart(fig_5,use_container_width= True)
             center.plotly_chart(fig_6, use_container_width= True)

