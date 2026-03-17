import streamlit as st
import pandas as pd
from api_client import client
import plotly.express as px

def render_overview():
    st.header("Overview")
    
    # Fetch data
    with st.spinner("Loading overview data..."):
        sensors = client.get_sensors()
        species = client.get_species()
        detections_data = client.get_detections(limit=1) # Just to get the total count
        
    # Display KPIs
    col1, col2, col3 = st.columns(3)
    
    total_detections = detections_data.get("total", 0)
    active_sensors = len(sensors)
    total_species = len(species)
    
    with col1:
        st.metric("Total Detections", f"{total_detections:,}")
    with col2:
        st.metric("Active Sensors", active_sensors)
    with col3:
        st.metric("Species Identified", total_species)
        
    st.divider()
    
    # Recent activity summary
    st.subheader("Recent Activity Summary")
    if total_detections > 0:
        recent = client.get_detections(limit=10)
        df = pd.DataFrame(recent.get("detections", []))
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            st.dataframe(
                df[['timestamp', 'species', 'sensor_id', 'confidence']],
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("No detections recorded yet.")

def render_detections():
    st.header("Detections Explorer")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        species_filter = st.text_input("Filter by Species (Scientific Name)", "")
    with col2:
        sensor_filter = st.text_input("Filter by Sensor ID", "")
        
    limit = st.slider("Number of records to fetch", min_value=10, max_value=100, value=50, step=10)
    
    # Fetch data
    with st.spinner("Loading detections..."):
        kwargs = {"limit": limit}
        if species_filter: kwargs["species"] = species_filter
        if sensor_filter: kwargs["sensor_id"] = sensor_filter
            
        data = client.get_detections(**kwargs)
        detections = data.get("detections", [])
        total = data.get("total", 0)
        
    st.caption(f"Showing {len(detections)} of {total} total detections matching criteria")
    
    if detections:
        df = pd.DataFrame(detections)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Display as a nicely formatted dataframe
        st.dataframe(
            df[['timestamp', 'species', 'sensor_id', 'confidence']],
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Detected At", format="MMM DD, YYYY, h:mm a"),
                "species": "Species",
                "sensor_id": "Sensor",
                "confidence": st.column_config.ProgressColumn("Confidence", min_value=0.0, max_value=1.0)
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No detections found matching the current filters.")

def render_sensors():
    st.header("Sensor Network")
    
    with st.spinner("Loading sensors..."):
        sensors = client.get_sensors()
        
    if not sensors:
        st.info("No sensors registered yet.")
        return
        
    df = pd.DataFrame(sensors)
    
    # Display sensors map if lat/lon are available
    if 'latitude' in df.columns and 'longitude' in df.columns:
        st.subheader("Sensor Map")
        map_df = df.dropna(subset=['latitude', 'longitude'])
        if not map_df.empty:
            fig = px.scatter_mapbox(
                map_df, 
                lat="latitude", 
                lon="longitude", 
                hover_name="name", 
                hover_data=["sensor_id", "total_detections"],
                color="total_detections",
                size="total_detections",
                color_continuous_scale=px.colors.sequential.Viridis,
                zoom=3, 
                height=400
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)
            
    st.divider()
    st.subheader("Sensor Directory")
    
    if 'first_registered' in df.columns:
        df['first_registered'] = pd.to_datetime(df['first_registered'])
    if 'last_connection' in df.columns:
        df['last_connection'] = pd.to_datetime(df['last_connection'])
        
    display_cols = ['name', 'sensor_id', 'total_detections', 'last_connection']
    # Filter only columns that actually exist
    display_cols = [col for col in display_cols if col in df.columns]
    
    st.dataframe(
        df[display_cols],
        hide_index=True,
        use_container_width=True
    )

def render_species():
    st.header("Species Statistics")
    
    with st.spinner("Loading species data..."):
        species = client.get_species()
        
    if not species:
        st.info("No species detected yet.")
        return
        
    df = pd.DataFrame(species)
    
    st.subheader("Most Detected Species")
    
    # Bar chart of top species
    top_n = st.slider("Show top N species", min_value=5, max_value=50, value=15)
    top_species = df.nlargest(top_n, 'total_detections')
    
    fig = px.bar(
        top_species, 
        x='total_detections', 
        y='name', 
        orientation='h',
        title=f"Top {len(top_species)} Species by Detection Count",
        labels={'total_detections': 'Total Detections', 'name': 'Species'}
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("All Species")
    
    if 'last_detection' in df.columns:
        df['last_detection'] = pd.to_datetime(df['last_detection'])
        
    st.dataframe(
        df,
        column_config={
            "name": "Scientific Name",
            "total_detections": st.column_config.NumberColumn("Total Detections"),
            "last_detection": st.column_config.DatetimeColumn("Last Detected", format="MMM DD, YYYY, h:mm a")
        },
        hide_index=True,
        use_container_width=True
    )
