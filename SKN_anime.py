import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

st.set_page_config(layout="wide")

@st.cache_resource
def load_data():
    df = pd.read_csv("./data/anime_rating_-1.csv")
    anime_info = pd.read_csv("./data/anime_v2.csv")

    with open("knn_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("df_pivot.pkl", "rb") as f:
        df_pivot = pickle.load(f)

    return df, model, df_pivot, anime_info

df, model, df_pivot, anime_info = load_data()

def fetch_anime_image(anime_name):
    url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
    try:
        response = requests.get(url)
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["images"]["jpg"]["large_image_url"]
        else:
            return "https://via.placeholder.com/150"
    except:
        return "https://via.placeholder.com/150"

def search_anime_by_title(query):
    query = query.lower()
    matched_animes = anime_info[anime_info["name"].str.lower().str.contains(query, na=False)]
    return matched_animes[["name", "genre", "rating"]]

def search_anime_by_genre(selected_genres):
    filtered_animes = anime_info[anime_info["genre"].str.contains("|".join(selected_genres), na=False, case=False)]
    return filtered_animes[["name", "genre", "rating"]]

def recommend_knn(anime_name, n_recommendations=5):
    if anime_name not in df_pivot.index:
        return [f"Sorry, we don't have information for '{anime_name}'"], [], [], []
    query_index = df_pivot.index.get_loc(anime_name)
    distances, indices = model.kneighbors(df_pivot.iloc[query_index, :].values.reshape(1, -1), 
                                          n_neighbors=n_recommendations + 1)
    recommended_animes = df_pivot.index[indices.flatten()[1:]]
    genres = []
    ratings = []
    images = []
    anime_info["name_clean"] = anime_info["name"].str.strip().str.lower()
    for anime in recommended_animes:
        anime_clean = anime.strip().lower()
        anime_info_row = anime_info[anime_info["name_clean"] == anime_clean]
        if not anime_info_row.empty:
            genres.append(anime_info_row.iloc[0]["genre"])
            ratings.append(anime_info_row.iloc[0]["rating"])
        else:
            genres.append("No Information")
            ratings.append("No Information")
        images.append(fetch_anime_image(anime))
    return recommended_animes.tolist(), genres, ratings, images

def fetch_anime_youtube(anime_name):
    url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
    try:
        response = requests.get(url)
        data = response.json()
        if "data" in data and len(data["data"]) > 0 and "trailer" in data["data"][0]:
            return data["data"][0]["trailer"]["url"]
        else:
            return None
    except:
        return None

st.markdown(
    f"""
    <style>
        /* 배경 이미지 적용 (Streamlit 컨테이너) */
        [data-testid="stAppViewContainer"] {{
            background-image: url('https://wallpapersok.com/images/high/demon-slayer-4k-official-art-zd3ibwgouvfhexct.webp');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        /* 메인 컨텐츠 배경 투명 처리 */
        [data-testid="stAppViewContainer"] > div:first-child {{
            background: rgba(255, 255, 255, 0.1) !important;
        }}

        /* 사이드바 투명도 조정 */
        [data-testid="stSidebar"] {{
            background: rgba(255, 255, 255, 0.3);
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
        body {
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
            
        .centered-title {
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            color: #ff4500;
            background-color: rgba(255, 255, 255, 0.8); /* 하얀색 반투명 배경 */
            padding: 10px;
            border-radius: 10px;
            width: 100%;
        }
    
        .anime-box {
            border: 2px solid #ff4500;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            background-color: #fff5e1;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
        }
        .bold-text {
            font-size: 20px;
            font-weight: bold;
        }
            
        .warning-text {
            font-size: 100px;
            font-weight: bold;
            color: red;
            background-color: rgba(255, 255, 255, 0.8); /* 하얀색 반투명 배경 */
            padding: 10px;
            border-radius: 10px;
            display: block;
            text-align: center;
        }

    </style>
""", unsafe_allow_html=True)


#st.markdown("<h1 class='centered-title'>SKN Animation</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='centered-title'>SKN Animation</h1>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

youtube_id = "UBdCw32yTFw"

youtube_url = f"https://www.youtube.com/embed/{youtube_id}?autoplay=1&loop=1&playlist={youtube_id}&mute=1"

video_html = f"""
    <iframe width="560" height="315" src="{youtube_url}" 
    frameborder="0" allow="autoplay; loop; encrypted-media" allowfullscreen 
    style="display: block; margin: auto; border-radius: 10px;">
    </iframe>
"""

st.markdown(video_html, unsafe_allow_html=True)
#st.markdown(video_html, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
#st.markdown("<p class='bold-text'>If anyone disrespects or behaves badly toward the great anime fans, call 010-5013-0715 or come to Taejeon-dong, Gwangju, Gyeonggi-do!</p>", unsafe_allow_html=True)
st.markdown("<p class='warning-text'>If anyone disrespects or behaves badly toward the great anime fans, call 010-5013-0715 or come to Taejeon-dong, Gwangju, Gyeonggi-do! I Love YACHA-RULE</p>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

title_query = st.text_input("Search Anime by Title")
if title_query:
    search_results = search_anime_by_title(title_query)
    st.dataframe(search_results)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

selected_genres = st.multiselect("Search Anime by Genre", anime_info["genre"].unique())
if selected_genres:
    genre_results = search_anime_by_genre(selected_genres)
    st.dataframe(genre_results)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

title_query = st.text_input("Search for the full name of the animation and check its Trailer and Image", key="anime_search")

if title_query:
    search_results = search_anime_by_title(title_query)
    st.dataframe(search_results)

    if not search_results.empty:
        selected_anime_info = search_results.iloc[0]
        image_url = fetch_anime_image(selected_anime_info["name"])
        youtube_url = fetch_anime_youtube(selected_anime_info["name"])

        st.image(image_url, width=200)

        if youtube_url:
            st.markdown(f"[Watch Trailer]({youtube_url})", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

selected_anime = st.selectbox("Select Your Animation", df_pivot.index)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

if st.button("Recommendation Button"):
    st.markdown(f"<h2 class='centered-title'>Here are some recommended anime for '{selected_anime}' fans:</h2>", unsafe_allow_html=True)
    names, genres, ratings, images = recommend_knn(selected_anime)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    for i, anime in enumerate(names):
        with cols[i]:
            st.markdown(f"""
                <div class='anime-box'>
                    <strong class='bold-text'>{anime}</strong>
                    <br>
                    <img src='{images[i]}' width='150'>
                    <br>
                    <strong class='bold-text'>Rating:</strong> {ratings[i]}
                    <br>
                    <strong class='bold-text'>Genre:</strong> {genres[i]}
                </div>
            """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)