import base64
from datetime import datetime
from pathlib import Path

import streamlit as st
import weaviate
import weaviate.classes as wvc


class WeaviateApp:
    def __init__(self):
        self.client = weaviate.connect_to_local()
        self.logo_path = Path("assets/weaviate-logo-light-transparent-200.png")
        self.big_response_list = []

    def display_title(self):
        title_cols = st.columns([0.15, 0.85])
        with title_cols[0]:
            st.write("")
            st.image(self.logo_path.read_bytes(), width=75)
        with title_cols[1]:
            st.title("Multi-Modality with Weaviate")

    def display_instructions(self):
        st.subheader("Instructions")
        st.write(
            """
            Search the dataset by uploading an image or entering free text.
            The model is multi-lingual as well - try searching in different languages!

            (Note: If you enter both, only the image will be used.)
            """
        )

    def get_search_inputs(self):
        st.subheader("Search the dataset")
        srch_cols = st.columns(2)
        with srch_cols[0]:
            search_text = st.text_area(label="Search by text")
        with srch_cols[1]:
            img = st.file_uploader(label="Search by image")
        return search_text, img

    def get_sort_filter_inputs(self):
        sort_by = st.selectbox('Sort by', ['Relevance', 'Date'])
        filter_by_relevance = st.checkbox('Filter by Relevance')
        relevance_threshold = st.number_input('Relevance Threshold', value=0.0) if filter_by_relevance else None
        filter_by_date = st.checkbox('Filter by Date')
        date_before = st.text_input('Before Date (YYYY-MM-DD)') if filter_by_date else None
        date_after = st.text_input('After Date (YYYY-MM-DD)') if filter_by_date else None
        return sort_by, filter_by_relevance, relevance_threshold, filter_by_date, date_before, date_after

    def search_by_image(self, img):
        img_collection = self.client.collections.get('images')
        imgb64 = base64.b64encode(img.read()).decode()
        response = img_collection.query.near_image(
            near_image=imgb64,
            return_properties=["filename"],
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=6,
        )
        self.big_response_list.extend(response.objects)

    def search_by_text(self, search_text):
        collections = ['images', 'WineReviews', 'pdf']
        for collection in collections:
            collection_obj = self.client.collections.get(collection)
            response = collection_obj.query.near_text(
                query=search_text,
                return_properties=["filename"],
                return_metadata=wvc.query.MetadataQuery(distance=True),
                limit=6,
            )
            self.big_response_list.extend(response.objects)

    def sort_and_filter_results(self, sort_by, filter_by_relevance, relevance_threshold, filter_by_date, date_before, date_after):
        if sort_by == 'Relevance':
            self.big_response_list.sort(key=lambda x: x.metadata.distance, reverse=True)
        elif sort_by == 'Date':
            self.big_response_list.sort(key=lambda x: x.metadata.creation_time, reverse=True)

        if filter_by_relevance:
            self.big_response_list = [r for r in self.big_response_list if r.metadata.distance >= relevance_threshold]
        if filter_by_date:
            if date_before:
                date_before = datetime.strptime(date_before, '%Y-%m-%d')
                self.big_response_list = [r for r in self.big_response_list if r.metadata.creation_time <= date_before]
            if date_after:
                date_after = datetime.strptime(date_after, '%Y-%m-%d')
                self.big_response_list = [r for r in self.big_response_list if r.metadata.creation_time >= date_after]

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
                    pass

                st.write(f"Properties: {r.properties}")
                st.write(f"Metadata: {r.metadata}")

    def run(self):
        self.display_title()
        self.display_instructions()
        search_text, img = self.get_search_inputs()
        sort_by, filter_by_relevance, relevance_threshold, filter_by_date, date_before, date_after = self.get_sort_filter_inputs()

        if search_text != "" or img is not None:
            if img is not None:
                st.image(img, caption="Uploaded Image", use_column_width=True)
                self.search_by_image(img)
            else:
                self.search_by_text(search_text)

            self.sort_and_filter_results(sort_by, filter_by_relevance, relevance_threshold, filter_by_date, date_before, date_after)
            self.display_results()


if __name__ == "__main__":
    app = WeaviateApp()
    app.run()
