import pandas as pd
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity
from easygui import *
import PySimpleGUI as sg


def recommendations(user):
    sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
    best = []
    most_common = {}
    for i in sim_users:
        max_score = piv_norm.loc[:, i].max()
        best.append(piv_norm[piv_norm.loc[:, i] == max_score].index.tolist())
    for i in range(len(best)):
        for j in best[i]:
            if j in most_common:
                most_common[j] += 1
            else:
                most_common[j] = 1
    sorted_list = sorted(most_common.items(), key=lambda elem: elem[1], reverse=True)
    return [i[0] for i in sorted_list[:5]]


text = 'Введите любимые фильмы через запятую. Пример ввода: The Shawshank Redemption (1994), The Godfather (1969), ' \
       'The Dark Kinght (2008) '
value = enterbox(text)
sg.one_line_progress_meter('Загрузка', 0, 4, '-key-')
movies = pd.read_csv("movies.csv")
rating = pd.read_csv("ratings.csv", usecols=[0, 1, 2])
rating = rating[rating.rating == 5.0]
merged = pd.merge(movies, rating, on='movieId', how='outer')
merged.pop('movieId')
merged.pop('genres')
merged_sub = merged[merged.userId <= 1000] #в качестве примера взято 1000 пользователей (для более быстрого расчета)
sg.one_line_progress_meter('Загрузка', 1, 4, '-key-')
max_id = max(merged['userId'])
value.split(', ')
for movie in value:
    merged_sub.loc[len(merged_sub)] = {'userId': max_id, 'title': movie, 'rating': 5.0}
sg.one_line_progress_meter('Загрузка', 2, 4, '-key-')
piv = merged_sub.pivot_table(index=['userId'], columns=['title'], values='rating')
piv.fillna(0, inplace=True)
piv_norm = piv.T
piv_norm = piv_norm.loc[:, (piv_norm != 0).any(axis=0)]
piv_sparse = sp.sparse.csr_matrix(piv_norm.values)
sg.one_line_progress_meter('Загрузка', 3, 4, '-key-')
item_similarity = cosine_similarity(piv_sparse)
user_similarity = cosine_similarity(piv_sparse.T)
item_sim_df = pd.DataFrame(item_similarity, index=piv_norm.index, columns=piv_norm.index)
user_sim_df = pd.DataFrame(user_similarity, index=piv_norm.columns, columns=piv_norm.columns)
sg.one_line_progress_meter('Загрузка', 4, 4, '-key-')
msg = "Какой фильм вас заинтересовал?"
title = "Рекомендуемые фильмы"
choices = recommendations(max_id)
choice = choicebox(msg, title, choices)
