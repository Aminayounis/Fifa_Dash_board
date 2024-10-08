#predefined packages
import streamlit as st
import pandas as pd 
import plotly.express as px 
import base64


### defined functions 
def get_img_base64(file):
    with open(file,"rb") as f:
        data=f.read()
    return base64.b64encode(data).decode()

@st.cache_data
def load_data():
    dta= pd.read_csv("fifa_eda.csv")
    dta.dropna(inplace=True)
    dta['Year']=pd.to_datetime(dta['Contract Valid Until']).dt.strftime('%Y')
    dta['duration']=dta['Year'].astype('int')-dta['Joined']
    c_vall=pd.DataFrame(dta.groupby('Club')['Value'].mean())
    c_vall.reset_index(inplace=True)
    c_vall=c_vall.merge(pd.DataFrame(dta.groupby('Club')['Age'].max() - dta.groupby('Club')['Age'].min()).reset_index(),on='Club')
    c_vall=c_vall.merge(pd.DataFrame(dta.groupby('Club')['duration'].mean()),on='Club')
    return dta,c_vall



### defined variables 
df,c_val=load_data()
clubs=df['Club'].unique()
sidebar_imgs={
    "FC Barcelona":"clubs_img/barca.png",
    "Juventus":"clubs_img/juven.png",
    "Paris Saint-Germain":"clubs_img/parisst.png",
    "Manchester United":"clubs_img/manchunit.png",
    "Manchester City":"clubs_img/manchester.png"
}
defalt_sidebar="clubs_img/fifa.png"
img=get_img_base64("background.png")
background_image=f"""
<style>
[data-testid="stAppViewContainer"]{{
    background-image:url("data:img/png;base64,{img}");
    background-size:cover;
}}

[data-testid="stSidebar"]>div:first-child{{
    background-color: #873b04;
}}

</style>
"""


###dashboard  

#main board
st.markdown(background_image,unsafe_allow_html=True)
st.header("Top reasons (to/not to) be a soccer in this club")
st.write('**check if you can take a part in your prefered club in three steps:**')

#sidebar
st.sidebar.header("Club Analysis")
selected_club=st.sidebar.selectbox("Select your prefered club:",clubs,index=None,placeholder="Select your prefered club...")
if selected_club is not None:
    st.sidebar.image(defalt_sidebar if (selected_club not in sidebar_imgs) else sidebar_imgs[selected_club])
else:
    st.warning('Please select an option.')

#tabs
tab1,tab2,tab3=st.tabs([f'about \"{selected_club if selected_club != None else ""}\"->','compare it with other clubs->',f'check if  you can be a soccer in \"{selected_club if selected_club != None else ""}\"'])

#tab1
with tab1:
    if selected_club != None:
        st.write(f"{selected_club} top 3 players")
        st.write((df[df['Club']==selected_club].sort_values('Overall'))[['Name','Overall','Skill Moves','Potential']].head(3))
        st.plotly_chart(px.histogram(df[df['Club']==selected_club]['Value'],title="players value distribution"))
        c1,c2=st.columns(2)
        c1.plotly_chart(px.histogram(df[df['Club']==selected_club]['Age'],title="players age distribution"))
        c2.plotly_chart(px.histogram(df[df['Club']==selected_club]['duration'],title="players duration to be in the club distribution"))
    else:
        st.write("no clubs have been selected")


#tab2
with tab2:
    selected_clubs=st.multiselect("Select some clubs to compare:",clubs)
    if selected_club != None:
        sl_clbs=[]
        if len(selected_clubs)>0:
            sl_clbs=selected_clubs
            sl_clbs.append(selected_club)
        st.write("Top 10 players among selected clubs:")
        st.write(df[df['Club'].isin(sl_clbs)].nlargest(10,'Overall')[['Name','Club','Overall','Skill Moves','Potential']])
        st.write("your prefered club will be represented in red color in the following graphs")
        st.plotly_chart(px.bar(c_val[c_val['Club'].isin(sl_clbs)],x='Club',y='Value',color=['red' if val == selected_club else 'blue' for val in c_val[c_val['Club'].isin(sl_clbs)]['Club']],color_discrete_map="identity",title="value distribution") )
        st.plotly_chart(px.histogram(c_val[c_val['Club'].isin(sl_clbs)],x='Club',y='Age',color=['red' if val == selected_club else 'blue' for val in c_val[c_val['Club'].isin(sl_clbs)]['Club']],color_discrete_map="identity",title="Age distribution") )
        st.plotly_chart(px.bar(c_val[c_val['Club'].isin(sl_clbs)],x='Club',y='duration',color=['red' if val == selected_club else 'blue' for val in c_val[c_val['Club'].isin(sl_clbs)]['Club']],color_discrete_map="identity",title="players joining duration distribution") )
    else:
        st.write("Top 10 players among selected clubs")
        st.write(df[df['Club'].isin(selected_clubs)].nlargest(10,'Overall')[['Name','Club','Overall','Skill Moves','Potential']])
        st.plotly_chart(px.bar(c_val[c_val['Club'].isin(selected_clubs)],x='Club',y='Value',title="average value distribution among selected clubs"))
        st.plotly_chart(px.histogram(c_val[c_val['Club'].isin(selected_clubs)],x='Club',y='Age',title="average age distribution among selected clubs"))
        st.plotly_chart(px.bar(c_val[c_val['Club'].isin(selected_clubs)],x='Club',y='duration',title="average players joining duration distribution among selected clubs"))


#tab3
with tab3:
    if selected_club != None:
        st.write(df[df['Club']=='Paris Saint-Germain'][['Height','Weight','Skill Moves','Potential']].describe().drop('count'))
        st.write("Key words: \n- mean->(average value) \n- std->(average variation between players and mean value) \n- min->(minimum value) \n- max->(maximum value) \n- [25% , 50% , 75%](average of percent of values).")
    else:
        st.write("no clubs have been selected")