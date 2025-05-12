import streamlit as st
import pandas as pd
import time
import datetime

# --- Configuration ---
# How often the app will try to rerun and data will be considered stale (in seconds)
APP_REFRESH_INTERVAL_SECONDS = 60
# How long data is cached (should be similar to or slightly less than APP_REFRESH_INTERVAL_SECONDS)
DATA_CACHE_TTL_SECONDS = 55

# --- Page Setup ---
st.set_page_config(page_title="Fan Favorite Posters", layout="wide")
st.title("🏆 Fan Favorite Posters")
st.write(f"This app displays fan favorite posters and their vote counts. Data attempts to refresh every {APP_REFRESH_INTERVAL_SECONDS} seconds.")

# --- Session State Initialization for Timestamps ---
if 'last_app_rerun_time' not in st.session_state:
    st.session_state.last_app_rerun_time = time.time()
if 'last_successful_data_fetch_time' not in st.session_state:
    # Initialize with a very old time to ensure first load fetches data
    st.session_state.last_successful_data_fetch_time = 0

# --- Auto Rerun Logic for the App ---
current_time = time.time()
if current_time - st.session_state.last_app_rerun_time > APP_REFRESH_INTERVAL_SECONDS:
    st.session_state.last_app_rerun_time = current_time
    st.rerun()

# --- Data Loading Function with Caching ---
@st.cache_data(ttl=DATA_CACHE_TTL_SECONDS)
def load_data_from_url(url: str, sheet_name: str) -> pd.DataFrame:
    """Loads data from a Google Sheets CSV URL into a pandas DataFrame."""
    try:
        df = pd.read_csv(url)
        # Record the time of successful data fetch for this specific cache entry implicitly via ttl
        # We'll display a general "last attempted fetch" time or "data as of" time based on this.
        st.session_state.last_successful_data_fetch_time = time.time()
        st.toast(f"Successfully fetched fresh data for {sheet_name}.", icon="✅")
        return df
    except pd.errors.EmptyDataError:
        st.warning(f"Warning: The sheet '{sheet_name}' at {url} is empty or not a valid CSV.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data for {sheet_name} from {url}: {e}")
        # Return an empty DataFrame or a previously cached version if available (cache handles this)
        # For robustness, ensure an empty df is returned if critical.
        return pd.DataFrame()


# --- Data Sources ---
# It's good practice to ensure your Google Sheets are published to the web as CSV
# File > Share > Publish to web > Select specific sheets > CSV > Publish
fan_fav_sheet_id = "1Xt5E3iyr_QL9jL8xNQ3mQ9IY8WuAC1JnDyeueYtvErc"
main_poster_sheet_id = "1A165s6AM7IWTP62z87W34PmnwAjPrtY395fMTunKISY"

# Ensure you use the correct sheet ID (gid) if your document has multiple sheets.
# If it's the first sheet, gid=0 is often the default when not specified.
# For more complex sheets, you might need to add &gid={sheet_gid} to the URL.
fan_fav_csv_url = f"https://docs.google.com/spreadsheets/d/{fan_fav_sheet_id}/export?format=csv"
main_poster_csv_url = f"https://docs.google.com/spreadsheets/d/{main_poster_sheet_id}/export?format=csv"

# --- Load Data ---
df_fan_fav_raw = load_data_from_url(fan_fav_csv_url, "Fan Favorites")
df_main_poster_raw = load_data_from_url(main_poster_csv_url, "Main Posters")

# --- Display Last Successful Data Fetch Time ---
if st.session_state.last_successful_data_fetch_time > 0:
    utc_time = datetime.datetime.fromtimestamp(st.session_state.last_successful_data_fetch_time)
    # PDT is UTC-7
    pdt_time = utc_time - datetime.timedelta(hours=7)
    fetch_time_str = pdt_time.strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"Data last successfully fetched around: {fetch_time_str}")
else:
    st.caption("Attempting to fetch data...")

# --- Validate Loaded Data ---
if df_fan_fav_raw.empty and df_main_poster_raw.empty:
    st.error("Both Fan Favorites and Main Poster data sheets could not be loaded or are empty. Please check the Google Sheet URLs and permissions.")
    st.stop()
if df_fan_fav_raw.empty:
    st.warning("Fan Favorites data is empty. Polling results may not be accurate.")
if df_main_poster_raw.empty:
    st.warning("Main Poster data is empty. Poster details might be missing.")

# Create copies for manipulation to avoid altering cached data if complex inplace operations were used.
# For simple merges/renames, it's less critical but good practice.
df_fan_fav = df_fan_fav_raw.copy()
df_main_poster = df_main_poster_raw.copy()

# --- Data Processing ---
required_fan_fav_columns = ['poster_id'] # Expecting 'poster_id' (lowercase) as per original
required_main_poster_columns = ['POSTER_ID', 'Poster Title', "PI's Full Name"]

# Standardize POSTER_ID column in df_fan_fav
if 'poster_id' in df_fan_fav.columns:
    df_fan_fav = df_fan_fav.rename(columns={'poster_id': 'POSTER_ID'})
elif 'POSTER_ID' not in df_fan_fav.columns and not df_fan_fav.empty:
    st.error("Critical: 'POSTER_ID' or 'poster_id' column not found in Fan Favorites data. Cannot process votes.")
    st.stop()

# Check required columns in main_poster_df
missing_main_cols = [col for col in required_main_poster_columns if col not in df_main_poster.columns]
if missing_main_cols and not df_main_poster.empty:
    st.warning(f"Warning: Main poster data is missing expected columns: {', '.join(missing_main_cols)}. Details might be incomplete.")
    # Add missing columns with NaNs if they don't exist, to prevent merge errors later
    for col in missing_main_cols:
        df_main_poster[col] = pd.NA


# --- Live Polling Results Display ---
st.subheader("🗳️ Live Polling Results")

if 'POSTER_ID' in df_fan_fav.columns and not df_fan_fav.empty:
    # Group by POSTER_ID and count the number of occurrences (votes)
    df_polling = df_fan_fav.groupby('POSTER_ID').size().reset_index(name='Total Votes')

    # Prepare main poster data for merging (select relevant columns and drop duplicates by POSTER_ID)
    if 'POSTER_ID' in df_main_poster.columns:
        details_to_merge = df_main_poster[['POSTER_ID', 'Poster Title', "PI's Full Name"]].drop_duplicates(subset=['POSTER_ID'])
        df_polling = pd.merge(df_polling, details_to_merge, on='POSTER_ID', how='left')
    else:
        st.warning("No 'POSTER_ID' in Main Poster data to merge details.")
        df_polling['Poster Title'] = "Details Unavailable"
        df_polling["PI's Full Name"] = "Details Unavailable"


    # Fill missing titles or PI names if any POSTER_ID from fan_fav was not in main_poster
    df_polling['Poster Title'] = df_polling['Poster Title'].fillna("Title Not Found")
    df_polling["PI's Full Name"] = df_polling["PI's Full Name"].fillna("PI Name Not Found")

    # Sort in descending order by Total Votes
    df_polling = df_polling.sort_values(by='Total Votes', ascending=False).reset_index(drop=True)

    # Add a rank
    df_polling.insert(0, 'Rank', df_polling.index + 1)

    # Select and order columns for display
    columns_to_display = ['Rank', 'POSTER_ID', 'Poster Title', "PI's Full Name", 'Total Votes']
    # Filter out columns that might not exist if main_poster data was incomplete
    columns_to_display = [col for col in columns_to_display if col in df_polling.columns]

    st.dataframe(
        df_polling[columns_to_display],
        use_container_width=True,
        hide_index=True,
        column_config={
            "POSTER_ID": st.column_config.TextColumn("Poster ID"),
            "Poster Title": st.column_config.TextColumn("Poster Title", width="large"),
            "PI's Full Name": st.column_config.TextColumn("PI's Name"),
            "Total Votes": st.column_config.NumberColumn("Total Votes", format="%d 👍"),
        }
    )
else:
    if df_fan_fav.empty:
        st.info("No fan votes recorded yet or fan favorites data is empty.")
    else:
        st.warning("Could not generate polling results. 'POSTER_ID' column might be missing in the Fan Favorites data after processing.")

# --- Optional: Display raw or merged DataFrames for debugging ---
# with st.expander("Show Debugging Data"):
# st.subheader("Raw Fan Fav Data")
# st.dataframe(df_fan_fav_raw.head())
# st.subheader("Raw Main Poster Data")
# st.dataframe(df_main_poster_raw.head())
# st.subheader("Processed & Merged Polling Data")
# st.dataframe(df_polling.head() if 'df_polling' in locals() else "Polling data not generated.")
