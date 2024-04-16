from pathlib import Path
import weaviate
import weaviate.classes as wvc
import streamlit as st
import base64
from datetime import datetime

client = weaviate.connect_to_local()

logo_path = Path("assets/weaviate-logo-light-transparent-200.png")
title_cols = st.columns([0.15, 0.85])
with title_cols[0]:
    st.write("")
    st.image(logo_path.read_bytes(), width=75)
with title_cols[1]:
    st.title("Multi-Modality with Weaviate")

st.subheader("Instructions")
st.write(
    """
    Search the dataset by uploading an image or entering free text.
    The model is multi-lingual as well - try searching in different languages!

    (Note: If you enter both, only the image will be used.)
    """
)

st.subheader("Search the dataset")

srch_cols = st.columns(2)
with srch_cols[0]:
    search_text = st.text_area(label="Search by text")
with srch_cols[1]:
    img = st.file_uploader(label="Search by image")

sort_by = st.selectbox('Sort by', ['Relevance', 'Date'])
filter_by_relevance = st.checkbox('Filter by Relevance')
relevance_threshold = st.number_input('Relevance Threshold', value=0.0) if filter_by_relevance else None
filter_by_date = st.checkbox('Filter by Date')
date_before = st.text_input('Before Date (YYYY-MM-DD)') if filter_by_date else None
date_after = st.text_input('After Date (YYYY-MM-DD)') if filter_by_date else None

if search_text != "" or img is not None:
    
    big_reponse_list = []
    img_collection = client.collections.get('images')
    wine_reviws_collection = client.collections.get('WineReviews')
    pdf_collection = client.collections.get('pdf')
    
    if img is not None:
        st.image(img, caption="Uploaded Image", use_column_width=True)
        imgb64 = base64.b64encode(img.read()).decode()

        response = img_collection.query.near_image(
            near_image=imgb64,
            return_properties=[
                "filename",
            ],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
        )
        big_reponse_list.extend(response.objects)

    

    else:

        DISTANCE = 0.8
        big_reponse_list = []
        img_collection = client.collections.get('images')
        wine_reviws_collection = client.collections.get('WineReviews')
        pdf_collection = client.collections.get('pdf')
        video_collection = client.collections.get('videos')
       
        response = img_collection.query.near_text(
            query=search_text,
            return_properties=[
                "filename",
            ],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
            distance=DISTANCE
        )
        
        big_reponse_list.extend(response.objects)

        response = wine_reviws_collection.query.near_text(
            query=search_text,
            return_properties=[
                "filename",
            ],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
            distance=DISTANCE
        )

        big_reponse_list.extend(response.objects)

        response = pdf_collection.query.near_text(
            query=search_text,
            return_properties=[
                "filename",
            ],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
            distance=DISTANCE
        )
        
        big_reponse_list.extend(response.objects)


        response = video_collection.query.near_text(
            query=search_text,
            return_properties=[
                "filename",
                # "image"  # TODO - return blob when implemented to client
            ],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
            distance=DISTANCE
        )
        big_reponse_list.extend(response.objects)

    if sort_by == 'Relevance':
        big_reponse_list.sort(key=lambda x: x.metadata.distance, reverse=True)
    elif sort_by == 'Date':
        big_reponse_list.sort(key=lambda x: x.metadata.creation_time, reverse=True)

    if filter_by_relevance:
        big_reponse_list = [r for r in big_reponse_list if r.metadata.distance >= relevance_threshold]
    if filter_by_date:
        if date_before:
            date_before = datetime.strptime(date_before, '%Y-%m-%d')
            big_reponse_list = [r for r in big_reponse_list if r.metadata.creation_time <= date_before]
        if date_after:
            date_after = datetime.strptime(date_after, '%Y-%m-%d')
            big_reponse_list = [r for r in big_reponse_list if r.metadata.creation_time >= date_after]

    st.subheader("Results found:")
    for i, r in enumerate(big_reponse_list):
        if i % 3 == 0:
            with st.container():
                columns = st.columns(3)
                st.divider()
        with columns[i % 3]:

            try:
                st.write(r.properties["filename"])
            except:
                st.write(r.properties["title"])

            try:
                imgpath = Path("data/images") / r.properties["filename"]
                img = imgpath.read_bytes()
                st.image(img)

                st.write(f"Relevance: {r.metadata.distance:.3f}")
            except:
                pass

            st.write(f"Properties: {r.properties}")
            st.write(f"Metadata: {r.metadata}")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
