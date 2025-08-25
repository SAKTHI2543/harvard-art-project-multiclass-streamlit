import streamlit as st
import pandas as pd
import mysql.connector
import time
import requests

#-----------------------------------------TIDB connection--------------------------- 

def get_connection():
    connection = mysql.connector.connect(
       host='gateway01.ap-southeast-1.prod.aws.tidbcloud.com',
        port=4000,
        user='EnD345nfx9wxmnG.root',
        password='Q4KKSkNgKxF3JIPn',
        database='HARVARD'
    )
    return connection

conn = get_connection()
cursor = conn.cursor(buffered=True)   

API_KEY = "49dcb8ef-cc75-4e72-b607-4d4873b0572f"                       
BASE_URL = "https://api.harvardartmuseums.org/object"    

# ----------------------------------------------------------Data Collection per class-------------------------------------------------------


def total_records(API_KEY,classification):    
                 
     all_records = []                                                        
     records_needed = 2500                                                   
     page = 1                                                                
     while len(all_records) < records_needed:                                
        params = {                                                         
        "apikey": API_KEY,                                              
        "classification": classification,                               
        "size": 100,                                                    
        "page": page,                                                   
        "hasimage": 1                                                   
    }
        response = requests.get(BASE_URL, params=params)                    
        data = response.json()  
        
        all_records.extend(data["records"])  
        
        if data["info"]["next"] is None:                                   
         break                                                           

        page += 1                                                          
        time.sleep(1) 
     return all_records
     
# Collecting metadata, media and color details
    
def artifacts_details(records):
    
    artifacts = []
    media = []
    colors = []

    for i in records:
          artifacts.append(dict(
              id = i['id'],
              title = i['title'],
              culture = i['culture'],
              period = i.get('period'),
              century = i['century'],
              medium = i.get('medium'),
              dimensions = i.get("dimensions"),
              dept = i.get("department"),
              desc = i.get('description'),
              classf = i['classification'],
              acc_yr = i['accessionyear'],
              methd = i['accessionmethod']
                          ))

          media.append(dict(
              objid = i['objectid'],
              imgcnt = i['imagecount'],
              medcnt = i['mediacount'],
              colcnt = i['colorcount'],
              rank = i['rank'],
              begin = i['datebegin'],
              dateend = i['dateend']

          ))

          sub_list = i.get('colors',[])
          for j in sub_list:
              colors.append(dict(
                  objid = i['objectid'],
                  color = j.get('color'),
                  spec= j.get('spectrum'),
                  hue = j['hue'],
                  percent = j['percent'],
                  css = j['css3']

              ))
    return artifacts,media,colors
  
# Data insertation into the already created SQl tables 

def batch_insert(cursor, query, values, batch_size=100):
    for i in range(0, len(values), batch_size):
        batch = values[i:i+batch_size]
        try:
            cursor.executemany(query, batch)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Batch insert failed: {e}")

def insert_values(arti, med, col):
    insert_meta = """
    INSERT INTO artifact_metadata
    (id, title, culture, period, century, medium, dimensions, department, description, classification, accessionyear, accessionmethod)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    insert_media = """
    INSERT INTO artifact_media
    (objectid, imagecount, mediacount, colorcount, `rank`, datebegin, dateend)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    insert_col = """
    INSERT INTO artifact_colors
    (objectid, color, spectrum, hue, percent, css3)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    meta_values = [
        (i['id'], i['title'], i['culture'], i['period'], i['century'],
         i['medium'], i['dimensions'], i['dept'], i['desc'], i['classf'],
         i['acc_yr'], i['methd']) for i in arti
    ]
    media_values = [
        (i['objid'], i['imgcnt'], i['medcnt'], i['colcnt'],
         i['rank'], i['begin'], i['dateend']) for i in med
    ]
    col_values = [
        (i['objid'], i['color'], i['spec'], i['hue'], i['percent'], i['css']) for i in col
    ]

    batch_insert(cursor, insert_meta, meta_values, batch_size=100)
    batch_insert(cursor, insert_media, media_values, batch_size=100)
    batch_insert(cursor, insert_col, col_values, batch_size=100)


#-----------------------------------------streamlit UI creations--------------------------    
    
st.set_page_config(layout="wide")

st.markdown("<h3 style='color: black;'>🖼️ Harvard Artifacts Collections</h3>", unsafe_allow_html=True)    

classification = st.selectbox(
    "Select the classification",
    ("Paintings", "Coins", "Vessels","Photographs","Drawings"),
    index=None,
    placeholder="Select a classification",
)                           
    
menu = st.radio("Choose a mode:", ["Classification Search", "Insert SQL","SQL Queries" ], horizontal=True)

if menu == "Classification Search":
    st.subheader("🔎 Search by Classification (Ex: Coins, Paintings, ...)")
                                            
    
    all_records=total_records(API_KEY,classification)
        
    
    meta,media,colors=artifacts_details(all_records)
   
    c1,c2,c3=st.columns(3)
    with c1:
        st.json(meta) 
    with c2:
        st.json(media)
    with c3:
        st.json(colors)     
        
    
if menu == 'Insert SQL':

        cursor.execute("select distinct(classification) from artifact_metadata")
        result = cursor.fetchall()
        classes_list = [i[0] for i in result]
        
       
        st.subheader("Insert the collected data")
        if st.button("Insert",key=1):
          if classification not in classes_list:

                records = total_records(API_KEY,classification)
                arti,med,col = artifacts_details(records)
                insert_values(arti,med,col)
                st.success("Data Inserted successfully")

                st.header("Inserted Data:")
                st.divider()

                st.subheader("Artifacts Metadata")
                cursor.execute("select * from artifact_metadata")
                result1 = cursor.fetchall()
                columns = [i[0] for i in cursor.description]
                df1 = pd.DataFrame(result1,columns=columns)
                st.dataframe(df1)

                st.subheader("Artifacts Media")
                cursor.execute("select * from artifact_media")
                result2 = cursor.fetchall()
                columns = [i[0] for i in cursor.description]
                df2 = pd.DataFrame(result2,columns=columns)
                st.dataframe(df2)

                st.subheader("Artifacts Colors")
                cursor.execute("select * from artifact_colors")
                result3 = cursor.fetchall()
                columns = [i[0] for i in cursor.description]
                df3 = pd.DataFrame(result3,columns=columns)
                st.dataframe(df3)
          else:
            st.error("Classification already exists!! Kindly try a different class ! ")   

    

elif menu == "SQL Queries":
    st.subheader("📄 Run PRD/Custom SQL Queries")
    query_dict = {
        "List all artifacts from 14th century belonging to Japanese culture":
            "SELECT * FROM artifact_metadata WHERE century = '14th century' AND culture = 'Japnaese'",
        "What are the unique cultures represented in the artifacts?":
            "SELECT DISTINCT culture FROM artifact_metadata WHERE culture IS NOT NULL AND culture <> ''",
        "List all artifacts from the British Period":
            "SELECT * FROM artifact_metadata WHERE period = 'Brititsh Period'",
        "List artifact titles ordered by accession year (descending)":
            "SELECT title, accessionyear FROM artifact_metadata ORDER BY accessionyear DESC",
        "How many artifacts are there per department?":
            "SELECT department, COUNT(*) AS artifact_count FROM artifact_metadata GROUP BY department ORDER BY artifact_count DESC",
        "Which artifacts have more than 1 image?":
            "SELECT m.id, m.title,a.imagecount FROM artifact_metadata m JOIN artifact_media a ON m.id = a.objectid WHERE a.imagecount > 1",
        "What is the average rank of all artifacts?":  
            "SELECT AVG(rank_num) AS average_rank FROM artifact_media",
        "Which artifacts have a higher mediacount than colorcount?":    
            "SELECT m.id, m.title, a.mediacount, a.colorcount FROM artifact_metadata m JOIN artifact_media a ON  m.id = a.objectid WHERE a.colorcount > a.mediacount",
        " List all artifacts created between 1500 and 1600":
            "SELECT * FROM artifact_media WHERE datebegin >= 1500 AND dateend <= 1600",
        "How many artifacts have no media files?":
            "SELECT COUNT(*) AS no_media_count FROM artifact_media WHERE mediacount = 0",
        "What are all the distinct hues used in the dataset?":
            "SELECT DISTINCT hue FROM artifact_colors", 
        "What are the top 5 most used colors by frequency?":
            "SELECT color, COUNT(*) AS frequency FROM artifact_colors GROUP BY color ORDER BY frequency DESC limit 5",
        "What is the average coverage percentage for each hue":
            "SELECT hue,AVG(percent) AS avg_coverage FROM artifact_colors GROUP BY hue ORDER BY avg_coverage DESC",
        "List all colors used for a given artifact ID":
            "SELECT color FROM artifact_colors WHERE objectid = '1429'",
        "What is the total number of color entries in the dataset?":
            "SELECT COUNT(*) AS total_color_entries FROM artifact_colors",
        "List artifact titles and hues for all artifacts belonging to the Byzantine culture":
            "SELECT m.title, c.hue FROM artifact_metadata m JOIN artifact_colors c ON m.id = c.objectid WHERE m.culture = 'Byzantine'",
        "List each artifact title with its associated hues":
            "SELECT m.title, GROUP_CONCAT(DISTINCT c.hue) AS hues FROM artifact_metadata m JOIN artifact_colors c ON m.id = c.objectid GROUP BY m.title",
        "Get artifact titles, cultures, and media ranks where the period is not null":
            "SELECT m.title, m.culture, a.rank FROM artifact_metadata m JOIN artifact_media a ON m.id = objectid WHERE m.period IS NOT NULL",
        "Find artifact titles ranked in the top 10 that include the color hue Grey":    
            "SELECT DISTINCT (m.title),a.rank_num FROM artifact_metadata m JOIN artifact_media a ON m.id = a.objectid JOIN artifact_colors c ON m.id = c.objectid WHERE c.hue = 'Grey' ORDER BY a.rank_num LIMIT 10",       
        "How many artifacts exist per classification, and what is the average media count for each?":
            "SELECT m.classification, COUNT(*) AS artifact_count, AVG(a.mediacount) AS avg_media_count FROM artifact_metadata m JOIN artifact_media a ON m.id = a.objectid GROUP BY m.classification ORDER BY artifact_count DESC",
        "Find all artifacts first accessioned before the year 1900?":
            "SELECT id, title, accessionyear FROM artifact_metadata WHERE accessionyear < 1900 ORDER BY accessionyear",
        "Show all artifact titles created in the 20th century?":
            "SELECT title FROM artifact_metadata WHERE century = '20th century'",
        " Find all artifacts that have “Gold” in their medium?":    
            "SELECT id, title, medium FROM artifact_metadata WHERE medium LIKE '%Gold%'",
        "Count how many artifacts were made by the culture Chinese ?":
            "SELECT COUNT(*) FROM artifact_metadata WHERE culture = 'Chinese'",
        "List all artifacts whose title contains the word portrait (case-insensitive) ?":
            "SELECT id, title FROM artifact_metadata WHERE LOWER(title) LIKE '%portrait%'"                                              
    }
    option = st.selectbox(
        "Choose a prewritten SQL query:",
        list(query_dict.keys())
    )
    default_sql = query_dict[option]
    user_sql = st.text_area("SQL to run:", value=default_sql, height=100)


    if st.button("Run Query"):
        try:
            cursor.execute(user_sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            if df.empty:
                st.info("No data found for this query.")
            else:
                st.dataframe(df)
        except Exception as e:
            st.error(f"SQL Error: {e}")

cursor.close()
conn.close() 