import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import os



cities = {
    1: "Cherkasy", 2: "Chernihiv", 3: "Chernivtsi", 4: "Crimea", 5: "Dnipropetrovs'k", 6: "Donets'k",
    7: "Ivano-Frankivs'k", 8: "Kharkiv", 9: "Kherson", 10: "Khmel'nyts'kyy", 11: "Kyiv", 12: "Kiev City",
    13: "Kirovohrad", 14: "Luhans'k", 15: "L'viv", 16: "Mykolayiv", 17: "Odessa", 18: "Poltava", 19: "Rivne",
    20: "Sevastopol'", 21: "Sumy", 22: "Ternopil'", 23: "Transcarpathia", 24: "Vinnytsya", 25: "Volyn",
    26: "Zaporizhzhya", 27: "Zhytomyr"
}

def framer():
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'area']
    files_dir = "D:\python works\da\lab3\VHI_Files"
    dataframe = pd.DataFrame()
    files = os.listdir(files_dir)
    for file in files:
        path = os.path.join(files_dir, file)
        try:
            df = pd.read_csv(path, header=1, names=headers)
            df = df.drop(df.loc[df["VHI"] == -1].index)
            df["area"] = int(file.split("_")[1])
            df['Year'] = df['Year'].astype(str).str.replace("<tt><pre>", "")
            df = df[~df['Year'].str.contains('</pre></tt>')]
            df['Year'] = df['Year'].astype(int)
            df['Week'] = df['Week'].astype(int)
            dataframe = pd.concat([dataframe, df]).drop_duplicates().reset_index(drop=True)
        except:
            continue
    return dataframe

df = framer()

default_state = {
    "index": "TCI",
    "region_name": list(cities.values())[0],
    "week_range": (1, 52),
    "year_range": (2000, 2021),
    "sort_asc": False,
    "sort_desc": False,
}

for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.button("Скинути фільтри"):
    for key, val in default_state.items():
        st.session_state[key] = val
    st.rerun()


col1, col2 = st.columns([1, 3])

with col1:
    st.session_state.index = st.selectbox("Оберіть індекс:", ["VCI", "TCI", "VHI"], 
                                          index=["VCI", "TCI", "VHI"].index(st.session_state.index))
    st.session_state.region_name = st.selectbox("Оберіть область:", list(cities.values()),
                                                index=list(cities.values()).index(st.session_state.region_name))
    st.session_state.week_range = st.slider("Інтервал тижнів:", 1, 52, st.session_state.week_range)
    st.session_state.year_range = st.slider("Інтервал років:", int(df["Year"].min()), int(df["Year"].max()), 
                                            st.session_state.year_range)
    st.session_state.sort_asc = st.checkbox("Сортувати за зростанням", value=st.session_state.sort_asc)
    st.session_state.sort_desc = st.checkbox("Сортувати за спаданням", value=st.session_state.sort_desc)

    if st.session_state.sort_asc and st.session_state.sort_desc:
        st.warning("Виберіть лише один тип сортування.")

with col2:
    tab1, tab2, tab3 = st.tabs(["Таблиця", "Графік", "Порівняння"])

    region_id = list(cities.keys())[list(cities.values()).index(st.session_state.region_name)]

    filtered = df[
        (df["area"] == region_id) &
        (df["Week"].between(*st.session_state.week_range)) &
        (df["Year"].between(*st.session_state.year_range))
    ][["Year", "Week", st.session_state.index, "area"]]

    if st.session_state.sort_asc:
        filtered = filtered.sort_values(by=st.session_state.index, ascending=True)
    elif st.session_state.sort_desc:
        filtered = filtered.sort_values(by=st.session_state.index, ascending=False)

    with tab1:
        st.dataframe(filtered)

    with tab2:
        if not filtered.empty:
            pivot = filtered.pivot(index="Year", columns="Week", values=st.session_state.index)
            plt.figure(figsize=(12, 6))
            sns.heatmap(pivot, cmap="YlGnBu", annot=False)
            plt.title(f"Теплова карта {st.session_state.index} для області {st.session_state.region_name}")
            st.pyplot(plt.gcf())
        else:
            st.info("ℹ Немає даних для побудови графіка.")

    with tab3:
        comparison = df[
            (df["Week"].between(*st.session_state.week_range)) &
            (df["Year"].between(*st.session_state.year_range))
        ]
        comparison_grouped = comparison.groupby("area")[st.session_state.index].mean().reset_index()
        comparison_grouped["region"] = comparison_grouped["area"].map(cities)
        plt.figure(figsize=(14, 5))
        sns.barplot(data=comparison_grouped, x="region", y=st.session_state.index)
        plt.xticks(rotation=90)
        plt.title(f"Порівняння середнього значення {st.session_state.index} по всіх областях")
        st.pyplot(plt.gcf())
