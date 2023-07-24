import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import pandas as pd


def read_shapefile(file_path):
    gdf = gpd.read_file(file_path)
    gdf = gdf.to_crs(epsg=4326)
    return gdf

def calculate_percentage_risk():
    file_path = "f:/earth_insight/risk_peatlands.gpkg"
    gdf = read_shapefile(file_path)
    
    gdf['area_2'] = pd.to_numeric(gdf['area_2'], errors='coerce')
    total_area = gdf['area_2'].fillna(0).sum()
    low_risk_area = gdf[gdf['risk'] == 'low']['area_2'].fillna(0).sum()
    medium_risk_area = gdf[gdf['risk'] == 'medium']['area_2'].fillna(0).sum()
    high_risk_area = gdf[gdf['risk'] == 'high']['area_2'].fillna(0).sum()

    if total_area == 0:
        percent_low, percent_medium, percent_high = 0, 0, 0
    else:
        percent_low = (low_risk_area / total_area) * 100
        percent_medium = (medium_risk_area / total_area) * 100
        percent_high = (high_risk_area / total_area) * 100

    return percent_low, percent_medium, percent_high

def main():
    # Set the background color and allow sidebar to be wider
    st.markdown(
        """
        <style>
        body {
            background-color: #0d0b0b;
            color: black;
        }
        .stApp {
            display: flex;
            flex-direction: row;
        }
        .stApp > div:first-child {
            margin-right: 2rem;
        }
         .sidebar .sidebar-content {
            max-width: 800px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    map_loading = st.empty()
    map_loading.progress(0)

    st.title("Tropical Peatlands in Peril")
    st.write("Shown below, tropical peatlands have been identified as at risk of peril based on their proximity "
             "to Oil & Gas infrastructure or basins within 10 miles. The level of risk increases as the number "
             "of O&G infrastructure near that peatland increases.")
    # peatlands risk file
    peatlands_file = "f:/earth_insight/risk_peatlands.gpkg"

    if peatlands_file is not None:
        peatlands_gdf = read_shapefile(peatlands_file)

        # Calculate the percentage of land at risk
        percent_low, percent_medium, percent_high = calculate_percentage_risk()

        # sidebar title
        st.sidebar.title("Why are oil and gas activities disproportionately common on peatlands?")
        st.sidebar.write("Peat accumulates in subsiding geological basins [1] (where the earths crust has sunken over geologic time and sediment has accumulated).")

        # Peatland facts
        st.sidebar.subheader("Immense Carbon Storage Capability:")
        st.sidebar.write("Peatlands make up only 3% of the Earth's land surface "
                         "but store more carbon than trees [2]. To avoid the worst impacts of climate change, "
                         "carbon here must remain undisturbed, as destruction of peatlands for oil & gas "
                         "releases carbon into the atmosphere and threatens the livelihoods of people "
                         "who depend on paludiculture (wet agriculture).")

        st.sidebar.subheader("Endangered Species:")
        st.sidebar.write("45% of the world's endangered mammal species are found in tropical peatlands, "
                         "as well as 33% of the world's endangered bird species [3].")

        st.sidebar.subheader("Importance of Protection and Restoration:")
        st.sidebar.write("Almost a quarter of peatlands have been disturbed globally by dry land agriculture, "
                         "livestock, mining, and other degradation [4]. More attention paid to protecting "
                         "peatlands is needed, as funding in peatland protection has lagged compared to other investments [4].")

        # pie chart colors
        colors = ['#440154',  # Low
                  '#21908d',  # Medium
                  '#fde725']  # High

        # Put the pie chart in the sidebar
        with st.sidebar:
            plt.figure(figsize=(6, 6))
            plt.pie([percent_low, percent_medium, percent_high], labels=['Low Risk', 'Medium Risk', 'High Risk'],
                    colors=colors, autopct='%1f%%')
            plt.axis('equal')
            st.pyplot(plt)

            # Citations
            st.subheader("Citations:")
            st.write("[1] SageJournals: https://journals.sagepub.com/doi/10.1177/27539687221124046")
            st.write("[2] Nature: https://www.nature.com/articles/s41598-021-82004-x")
            st.write("[3] Bioscience: https://academic.oup.com/bioscience/article/61/1/49/304606")
            st.write("[4] UNEP: https://www.unep.org/news-and-stories/press-release/conserve-and-restore-peatlands-slash-global-emissions-new-report")

            st.subheader("Oil/Gas Geologic & Infrastructure Data")
        # Create a Folium map
        map_center = [peatlands_gdf.geometry.centroid.y.mean(), peatlands_gdf.geometry.centroid.x.mean()]
        map_osm = folium.Map(location=map_center, zoom_start=5)

        # Add peatland risk analysis to the map
        folium.GeoJson(
            peatlands_gdf,
            name="Peat Risk",
            style_function=lambda feature: {
                'fillColor': colors[2] if feature['properties']['risk'] == 'high' else
                             colors[1] if feature['properties']['risk'] == 'medium' else
                             colors[0],
                'fillOpacity': .75,
                'color': 'black',
                'weight': .5
            },
            tooltip=folium.GeoJsonTooltip(fields=["area", "risk"],
                                          aliases=["Total Area at Risk (sq mi)", "Risk Level"],
                                          style="background-color: white; color: black; border: 1px solid gray;")
        ).add_to(map_osm)

        # Display the map 
        map_loading.progress(100)
        folium_static(map_osm, width=1200, height=1000)

        st.subheader("Risk Analysis Description:")
        st.write("This risk analysis was performed by buffering Oil & Gas infrastructure and Basin data by 10 miles. Peatlands were identified to be at risk of disturbance if they were within 10 miles of any infrastructure, or within a basin. The risk was then identified as Low, Medium, or High by the number of O&G features in proximity, with all features being weighted equally in this analysis. Further work can be done to analyze the different factors that increase risk of disturbance.")
        st.subheader("Sources:")
        st.markdown("- **Oil & Gas Data:** GOGI Global Dataset - [GOGI Global Dataset](https://www.google.com/search?q=gogi+global+dataset&oq=gogi+global+dataset&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQIRigAdIBCDMyODFqMGo0qAIAsAIA&sourceid=chrome&ie=UTF-8)")
        st.markdown("- **Peatlands Data:** Global Peatlands Dataset, Global Forest Watch - [Global Peatlands Dataset](https://hub.arcgis.com/documents/f7cf86a081ff48c794edeb5a2d9dbfa7/about)")

        
        # O&G data

        file_paths = [
            "earth_insight/og/Basins_clipped.gpkg",
            "earth_insight/og/Fields_clipped.gpkg",
            "earth_insight/og/LNG_clipped.gpkg",
            "earth_insight/og/Pipelines_clipped.gpkg",
            "earth_insight/og/Platforms_and_Well_Pads_clipped.gpkg",
            "earth_insight/og/Ports_clipped.gpkg",
            "earth_insight/og/Processing_Plants_clipped.gpkg",
            "earth_insight/og/Railways_clipped.gpkg",
            "earth_insight/og/Refineries_clipped.gpkg",
            "earth_insight/og/Stations_clipped.gpkg",
            "earth_insight/og/Storage_clipped.gpkg",
        ]

        for file_path in file_paths:
            file_name = file_path.split("/")[-1].split(".")[0]
            if st.sidebar.checkbox(f"Show {file_name}"):
                additional_gdf = read_shapefile(file_path)
                folium.GeoJson(
                    additional_gdf,
                    name=file_name,
                    style_function=lambda feature: {
                        'fillColor': '#FFD700',
                        'fillOpacity': .5,
                        'color': 'black',
                        'weight': .5
                    }
                ).add_to(map_osm)

if __name__ == "__main__":
    main()