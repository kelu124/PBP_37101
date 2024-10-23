import streamlit as st
import pandas as pd
import hashlib
import glob
import random
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.category import UnitData
from matplotlib.markers import MarkerStyle

matplotlib.rcParams['font.sans-serif'] = ["Arial Bold", 'Tahoma', 'DejaVu Sans', 'Lucida Grande', 'Verdana']
matplotlib.rcParams['font.family'] = ['sans-serif']

st.set_page_config(layout="wide")

df = pd.read_parquet("data/dataset_v2.parquet.gzip")
df = df[df.Place == "Paris"].reset_index(drop=True)
df["Source_Title"] = df["Source_Title"].apply(lambda x: str(x).replace("\n"," "))
print(len(df.Source.unique()))

def getXY(PATH="content.md"):
    file1 = open(PATH, 'r')
    Lines = file1.readlines()
    terms = {}
    X = []
    Y = []
    # Strips the newline character
    for line in Lines:
        TXT = line.strip()
        if TXT.startswith("## A") or TXT.startswith("## B"):
            P = TXT.split(" ")
            #print(P[1], " ".join(P[2:]))
            terms[P[1]] = " ".join(P[2:]).strip()
            if TXT.startswith("## A"):
                X.append(" ".join(P[2:]).strip())
            else:
                Y.append(" ".join(P[2:]).strip())
    return X, Y, terms



def createImg(df,dfRef=pd.DataFrame(),title="Placeholder"):


    X, Y, terms = getXY(PATH="doc/definitions/content.md")

    x = "Purpose"
    y = "Issue"
    h = "Scale"

    bin_dic = {0: "Building", 1: "Neighbourhood"}

    #counting the X-Y-H category entries
    plt_df = df.groupby([x, y, h]).size().to_frame(name="vals").reset_index()
    M = plt_df.vals.max()

    if len(dfRef):
        plt_dfRef = dfRef.groupby([x, y, h]).size().to_frame(name="vals").reset_index()
        MdfRef = plt_dfRef.vals.max()
    #figure preparation with grid and scaling
    fig, ax = plt.subplots(figsize=(12, 10))
    plt.title(title)
    if True:
        ax.set_ylim(11 + 0.15 + 0.5, -0.9)
        ax.set_xlim(-1.15+0.5, 6+0.15-0.5)
    ax.grid(ls="--")

    #upscale factor for scatter marker size
    scale=1500/plt_df.vals.max()
    #left marker for category 0
    ax.scatter(plt_df[plt_df[h]==bin_dic[0]][x], 
            plt_df[plt_df[h]==bin_dic[0]][y], 
            s=plt_df[plt_df[h]==bin_dic[0]].vals*scale, 
            c=[(0, 0, 1, 0.5)], edgecolor="black", marker=MarkerStyle("o", fillstyle="left"), 
            label=bin_dic[0], xunits=UnitData(X), yunits=UnitData(Y))
    #right marker for category 1
    ax.scatter(plt_df[plt_df[h]==bin_dic[1]][x], 
            plt_df[plt_df[h]==bin_dic[1]][y], 
            s=plt_df[plt_df[h]==bin_dic[1]].vals*scale, 
            c=[(1, 0, 0, 0.5)], edgecolor="black", marker=MarkerStyle("o", fillstyle="right"), 
            label=bin_dic[1])
    l=ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),
            fancybox=True, shadow=False, ncol=1)
    l.legendHandles[0]._sizes = l.legendHandles[1]._sizes = [800]

    if len(dfRef):

        scale=1500/MdfRef
        #left marker for category 0
        ax.scatter(plt_dfRef[plt_dfRef[h]==bin_dic[0]][x], 
                plt_dfRef[plt_dfRef[h]==bin_dic[0]][y], 
                s=plt_dfRef[plt_dfRef[h]==bin_dic[0]].vals*scale, 
                c=[(1, 1, 0, 0.8)], edgecolor="black", marker=MarkerStyle("*", fillstyle="left"), 
                label=bin_dic[0], xunits=UnitData(X), yunits=UnitData(Y))
        #right marker for category 1
        ax.scatter(plt_dfRef[plt_dfRef[h]==bin_dic[1]][x], 
                plt_dfRef[plt_dfRef[h]==bin_dic[1]][y], 
                s=plt_dfRef[plt_dfRef[h]==bin_dic[1]].vals*scale, 
                c=[(1, 1, 0, 0.8)], edgecolor="black", marker=MarkerStyle("*", fillstyle="right"), 
                label=bin_dic[1])
        
    ax.xaxis.set_ticks_position('top')
    plt.xticks(rotation=90)
    plt.xticks(rotation=-20, ha='right')

    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(16)
    ax.title.set_fontsize(20)

    labels = ['Attractiveness',
    'Preservation and improvement\nof environment',
    'Resilience',
    'Responsible resource use',
    'Social cohesion',
    'Well-being']
    ax.set_xticklabels(labels)

    labels = ['Governance, empowerment\nand engagement',
        'Education and\ncapacity building',
        'Innovation, creativity\nand research',
        'Health and care\nin the community',
        'Culture and\ncommunity identity',
        'Living together,\ninterdependence and mutuality',
        'Economy and sustainable\nproduction and consumption',
        'Living and\nworking environment',
        'Safety and security',
        'Biodiversity and \necosystem services',
        'Community smart\ninfrastructures',
        'Mobility']
    ax.set_yticklabels(labels)


    #plt.savefig(FILE+"_review.pdf",format="pdf", bbox_inches='tight')
    #if OUTPUT:
    #    plt.savefig(OUTPUT,format=ext, bbox_inches='tight')
    return fig, ax

lstEDITIONS = df.Edition.unique()
lstTHEMES = df.Thématique.unique()
lstARROND = df["Arrondissement du projet lauréat"].unique()
lstSTATE = df["Avancement du projet"].unique()

lstPURPOSE = df["Purpose"].unique()
lstISSUE = df["Issue"].unique()


themes = st.sidebar.multiselect(
    "Themes to consider",
    options=lstTHEMES,
    default=[])

purposes = st.sidebar.multiselect(
    "Purposes to consider",
    options=lstPURPOSE,
    default=[])

issues = st.sidebar.multiselect(
    "Issues to consider",
    options=lstISSUE,
    default=[])



DF = df.copy()
if len(themes):
    DF = DF[DF.Thématique.isin(themes)]
if len(purposes):
    DF = DF[DF.Purpose.isin(purposes)]
if len(issues):
    DF = DF[DF.Issue.isin(issues)]

ListActions = DF.Source.unique()
df = df[df.Source.isin(ListActions)]

optionActivity = st.selectbox(
   "Would you like to zoom in on an activity?",
   ["All"]+list(df["Source_Title"].unique())
)

overLimit = False
if optionActivity == "All":
    items = []
    X = df.drop_duplicates(subset=["Source"]).reset_index(drop=True)

    if len(X) > 50:
        overLimit = True
        X = X.sample(frac=1).reset_index(drop=True).head(50)

    fig, ax = createImg(df, dfRef=pd.DataFrame(), title="Mapping of Paris participatory budget initiatives")
else:
    X =df[df["Source_Title"] == optionActivity].reset_index(drop=True)

    st.write("# Overview of initiatives map")

    if optionActivity:
        st.write(optionActivity)

    fig, ax = createImg(X, dfRef=pd.DataFrame(), title="Mapping of Paris participatory budget initiatives")



if overLimit:
    st.warning("#### __Beware__ - there are more than 50 initiatives, we'll pick randomly 50 of them")

st.pyplot(fig)




if optionActivity == "All":
    st.write("# Initiatives map with "+str(len(X))+" items")
    for ix, row in X.iterrows():
        st.write("### "+str(ix+1)+". "+row["Source_Title"].replace("\n"," "))
        st.write("__Link to the initiative__:",row["Lien URL vers le projet lauréat"])
        st.write("__Theme__:",row["Thématique"])
        st.write("__Status__:",row["Avancement du projet"])
        st.write("__Budget__:",row["Budget global du projet lauréat"],"€")
        st.write("__Summary__\n",row["Summary"])
        st.write("__Original__\n",row["Source"])

else:
    row = X.iloc[0]
    st.write("#  "+row["Source_Title"].replace("\n"," "))

    st.write("## __Summary__\n",row["Summary"])
    st.write("## __Longer summary__\n",row["Paragraph"])

    st.write("__Link to the initiative__:",row["Lien URL vers le projet lauréat"])
    st.write("__Theme__:",row["Thématique"])
    st.write("__Status__:",row["Avancement du projet"])
    st.write("__Budget__:",row["Budget global du projet lauréat"],"€")
    
    
    st.write("# __Indicators__\n",row["Summary"])
    for ix,row in X.iterrows():
        st.write("#### "+row["Purpose"]+" x " + row["Issue"]+ " (Assessment: " +row["Scale"]+": "+str(row["Score"])+")")
        st.write(row["Justification"])
    st.write("# __Original text__\n",row["Source"])
    st.write(df)