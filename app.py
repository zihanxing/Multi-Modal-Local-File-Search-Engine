# Import necessary libraries
import base64
from datetime import datetime
from pathlib import Path

import streamlit as st
import weaviate
import weaviate.classes as wvc
from session_state import *

from datetime import datetime, timezone
import os
from streamlit import session_state as ss
from streamlit_pdf_viewer import pdf_viewer


debug = True

# Define the main application class
class WeaviateApp:
    def __init__(self):
        # Connect to the local Weaviate client
        self.client = weaviate.connect_to_local()
        # Define the path to the logo
        self.logo_path = Path("assets/logo.jpeg")
        # Initialize an empty list to store the search results
        self.big_response_list = []

        self.sort_by = None
        self.filter_by_relevance = None
        self.relevance_threshold = None
        self.filter_by_date = None
        self.date_before = None
        self.date_after = None


    # Function to display the title of the application
    def display_title(self):
        # Create columns for the title
        title_cols = st.columns([0.15, 0.85])
        with title_cols[0]:
            # Display the logo
            st.write("")
            st.image(self.logo_path.read_bytes(), width=75)
        with title_cols[1]:
            # Display the title
            st.title("Enhanced Local File Search")

    # Function to display the instructions for using the application
    def display_instructions(self):
        st.subheader("Instructions")
        st.write(
            """
            Search through all your ingested data to find the most relevant results across text, documents, video and audio!
            (Note: If you enter both, only the image will be used.)
            """
        )

    # Function to get the search inputs from the user
    def get_search_inputs(self):
        st.subheader("Search")
        srch_cols = st.columns(2)
        with srch_cols[0]:
            # Get the text input from the user
            search_text = st.text_area(label="Search by text")
        with srch_cols[1]:
            # Get the image input from the user
            img = st.file_uploader(label="Search by image")
        return search_text, img

    # Function to get the sort and filter inputs from the user
    def get_sort_filter_inputs(self):
        # Get the sort option from the user
        sort_by = st.selectbox('Sort by', ['Relevance', 'Date'])
        # Get the relevance filter option from the user
        filter_by_relevance = st.checkbox('Filter by Relevance')
        # Get the relevance threshold from the user
        relevance_threshold = st.number_input('Relevance Threshold', value=0.0) if filter_by_relevance else None
        # Get the date filter option from the user
        filter_by_date = st.checkbox('Filter by Date')
        # Get the before date from the user
        date_before = st.text_input('Before Date (YYYY-MM-DD)') if filter_by_date else None
        # Get the after date from the user
        date_after = st.text_input('After Date (YYYY-MM-DD)') if filter_by_date else None
        return sort_by, filter_by_relevance, relevance_threshold, filter_by_date, date_before, date_after

    # Function to search by image
    def search_by_image(self, img):
        # Get the image collection from the client
        img_collection = self.client.collections.get('images')
        # Convert the image to base64
        imgb64 = base64.b64encode(img.read()).decode()
        # Query the image collection with the image
        response = img_collection.query.near_image(
            near_image=imgb64,
            return_properties=["filename"],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
        )
        # Extend the big response list with the response objects
        self.big_response_list.extend(response.objects)

    # Function to search by text
    def search_by_text(self, search_text,llm_model):
        # Define the collections to search in
        collections = ['images', 'pdf','videos']
        # collections = ['pdf']

        if llm_model == 'TinyLlamma':
                from get_llama_inference import get_llama_inference
                result = get_llama_inference(search_text)

        for collection in collections:
            # Get the collection object from the client
            collection_obj = self.client.collections.get(collection)
            # Query the collection with the search text
            
            if llm_model == 'TinyLlamma':
                response = collection_obj.query.near_text(
                    query=result['file content'],
                    # return_properties=["filename"],                           # enable if required
                    return_metadata=wvc.query.MetadataQuery(distance=True),
                    limit=6,
                )
                print(result)
                if result['day'] == [0, 0] and result['month'] == [0, 0] and result['year'] == [2024, 2024]:
                    self.sort_by = 'Date'


            elif llm_model == 'BM25':
                response = collection_obj.query.bm25(
                    query=search_text,
                    # return_properties=["filename"],                           # enable if required
                    # return_metadata=wvc.query.MetadataQuery(distance=True),   # enable if required
                    limit=6,
                )
            elif llm_model == 'Vanilla':
                response = collection_obj.query.near_text(
                    query=search_text,
                    # return_properties=["filename"],                           # enable if required
                    # return_metadata=wvc.query.MetadataQuery(distance=True),   # enable if required
                    limit=6,
                )

            # Extend the big response list with the response objects
            self.big_response_list.extend(response.objects)


    # Function to sort and filter the results
    def sort_and_filter_results(self, sort_by, filter_by_relevance, relevance_threshold, filter_by_date, date_before, date_after):
        default_date = datetime.min.replace(tzinfo=timezone.utc)
        
        # Sort the results by relevance or date
        if sort_by == 'Relevance':
            try:
                self.big_response_list.sort(key=lambda x: x.metadata.distance)
            except:
                pass
        elif sort_by == 'Date':
            # Use a default date for items without a 'date_modified' property
            default_date = datetime.min.replace(tzinfo=timezone.utc)
            self.big_response_list.sort(key=lambda x: x.properties.get('date_modified', default_date))

        # Filter the results by relevance or date
        if filter_by_relevance:
            self.big_response_list = [r for r in self.big_response_list if r.metadata.distance <= relevance_threshold]
        if filter_by_date:
            if date_before:
                date_before = datetime.strptime(date_before, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                self.big_response_list = [r for r in self.big_response_list if r.properties.get('date_modified', default_date) <= date_before]
            if date_after:
                date_after = datetime.strptime(date_after, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                self.big_response_list = [r for r in self.big_response_list if r.properties.get('date_modified', default_date) >= date_after]



    # Function to display the results
    def display_results(self):
        st.subheader("Results found:")
        for i, r in enumerate(self.big_response_list):
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
                    try:
                        vidpath = Path("data/videos") / r.properties["filename"]
                        vid = vidpath.read_bytes()
                        st.video(vid)
                        st.write(f"Relevance: {r.metadata.distance:.3f}")
                    except:
                        pass

                    try:
                        binary_data = Path("data/pdf") / r.properties["filename"]
                        binary_data = binary_data.read_bytes()
                        # binary_data = ss.pdf_ref.getvalue()
                        pdf_viewer(input=binary_data, width=250,height=250,pages_to_render=[1,2])

                    except:
                        pass

                    if r.metadata.distance:
                        st.write(f"Relevance: {r.metadata.distance:.3f}")
                    pass
                    
                if debug==True:
                    st.write(f"date_created: {r.properties['date_modified']}")
                    st.write(f"date_modified: {r.properties['date_created']}")
                    # st.write(f"Metadata: {r.metadata}")


    # Function to display the data ingestion page
    def data_ingestion_page(self, state):
        self.display_title()
        st.title("Data Ingestion Page")

        state.data_dir = st.text_input("Enter the directory of your data", state.data_dir if hasattr(state, 'data_dir') else './data')
        if st.button("Ingest & Process Data"):
            st.write("Ingesting and processing data...")
            os.system(f"python add_data.py --data-dir {state.data_dir}")
            st.write("Data ingestion completed!")

    # Function to run the application
    def run(self):
        state = get_state()

        st.sidebar.title("Navigation")
        app_mode = st.sidebar.selectbox("Choose the page", ["Data Ingestion Page", "Search Page"])

        if app_mode == "Data Ingestion Page":
            self.data_ingestion_page(state)
        elif app_mode == "Search Page":
            self.display_title()
            self.display_instructions()
            search_text, img = self.get_search_inputs()

            self.sort_by, self.filter_by_relevance, self.relevance_threshold, self.filter_by_date, self.date_before, self.date_after = self.get_sort_filter_inputs()

            # Add a toggle for the LLM model
            llm_model = st.selectbox('LLM Model', ['BM25', 'TinyLlamma','Vanilla'])

            # Add a search button
            if st.button('Search'):
                if search_text != "" or img is not None:
                    if img is not None:
                        st.image(img, caption="Uploaded Image", use_column_width=True)
                        self.search_by_image(img)
                    else:
                        self.search_by_text(search_text,llm_model)

                    self.sort_and_filter_results(self.sort_by, self.filter_by_relevance, self.relevance_threshold, self.filter_by_date, self.date_before, self.date_after)
                    
                    self.display_results()

                # Display the selected sort and filter options
                st.subheader("Selected Options")
                st.write(f"Sort by: {self.sort_by}")
                st.write(f"Filter by Relevance: {self.filter_by_relevance}")
                if self.filter_by_relevance:
                    st.write(f"Relevance Threshold: {self.relevance_threshold}")
                st.write(f"Filter by Date: {self.filter_by_date}")
                if self.filter_by_date:
                    st.write(f"Before Date: {self.date_before}")
                    st.write(f"After Date: {self.date_after}")
                st.write(f"LLM Model: {llm_model}")
                self.sort_by = 'Relevance'

# Run the application
if __name__ == "__main__":
    app = WeaviateApp()
    app.run()
