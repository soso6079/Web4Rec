import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
from dash.exceptions import PreventUpdate

# import feffery_antd_components as fac
from .utils import global_component as gct
from .utils.global_component import pretty_metric
from .utils import deep_analysis_func as daf
from collections import Counter
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import requests

dash.register_page(__name__, path="/deep_analysis")


user = None
item = None
uniq_genre = None

# load_figure_template("darkly") # figure 스타일 변경

# 포스터를 띄우는 함수
def make_card(element):
    tmp = item.loc[element]
    img = (
        "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/3e0c51b2-0058-4c7e-a081-63c36afbb9ab/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230206%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230206T092314Z&X-Amz-Expires=86400&X-Amz-Signature=459ae00b0cb7fe0924f62f17992549f0cb0de1fd2db35bd510675575b2c2ba8e&X-Amz-SignedHeaders=host&response-content-disposition=filename%3D%22Untitled.png%22&x-id=GetObject"
        if tmp["item_url"] == ""
        else tmp["item_url"]
    )

    card = dbc.Col(
        children=dbc.Card(
            [
                dbc.CardImg(src=img, top=True, className="h-3 mb-0"),
                dbc.CardBody(
                    [
                        html.H6(tmp["movie_title"], className="mt-0"),
                        html.P(f'({tmp["release_year"]})', className="my-1"),
                        html.Hr(className="my-1"),
                        html.P(
                            "장르: " + ", ".join((tmp["genre"]).split()), className="my-1"
                        ),
                        html.P(
                            f'인기도: {round(tmp["item_pop"] * 100, 3)}%', className="mt-1 mb-0"
                        ),
                    ],
                ),
            ],
            style={"height": 515, "width": 200},
        ),
        width={"size": 2},
        style={"margin": "10px"},
    )
    return card


#############################################################################################
###########                       메인                      #################################
###########################################################################################

header_exp = html.Div(
    children=[
        dbc.Row(
            [
                html.H3("실험 선택", className="mt-3"),
                dcc.Dropdown(
                    id="exp_id_for_deep_analysis",
                    options=["exp1"],
                    className="w-25 my-3",
                ),
            ]
        )
    ]
)

header_user_or_item = html.Div(
    children=[
        dbc.Row(
            [
                # dbc.Tabs(
                #     [
                #         dbc.Tab(label="유저",id="tab_user"),
                #         dbc.Tab(label="아이템", id="tab_item"),
                #     ],
                #     id="da_input_tabs",
                #     active_tab="tab_user"
                # ),
                dbc.RadioItems(
                    id="show_user_or_item",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                ),
                # dbc.Button(id=f"{kind}_run", children="RUN", className="ms-auto w-100"),
            ],
            className="radio-group mb-3",
        ),
        # first_interval:=dcc.Interval(interval=15*1000, n_intervals=0)
    ]
)


def get_input_options(year_min=None, year_max=None, user=None, kind: str = "user"):
    pretty_value = {
        "user": "유저",
        "item": "아이템",
    }
    if kind == "item":
        input_list = html.Div(
            [
                html.H6("장르"),
                dcc.Dropdown(
                    options=uniq_genre,
                    id="selected_genre",
                ),
                html.H6("년도", className="my-2"),
                dcc.RangeSlider(
                    min=year_min,
                    max=year_max,
                    value=[
                        year_min,
                        year_max,
                    ],
                    step=1,
                    marks=None,
                    tooltip={
                        "placement": "bottom",
                        "always_visible": True,
                    },
                    allowCross=False,
                    id="selected_year",
                    className="my-2 ps-2",
                ),
            ],
            # className="border-end"
        )
    elif kind == "user":
        option_age = html.Div(
            children=[
                html.H6("연령대", className=""),
                dbc.Checklist(
                    options=sorted(user["age"].unique()), id="selected_age", inline=True
                ),
            ]
        )
        option_gender = html.Div(
            children=[
                html.H6("성별"),
                dcc.Dropdown(
                    options=["M", "F"],
                    id="selected_gender",
                ),
            ]
        )
        option_occupation = html.Div(
            children=[
                html.H6("직업"),
                dcc.Dropdown(
                    options=sorted(user["occupation"].unique()),
                    multi=True,
                    id="selected_occupation",
                ),
            ]
        )
        option_wrong = html.Div(
            children=[
                dcc.Checklist(
                    options=["틀린 유저들만(0.5 기준으로)"],
                    id="selected_wrong",
                ),
            ]
        )
        input_list = html.Div(
            [
                option_age,
                option_gender,
                option_occupation,
                option_wrong,
                choose_rerank,
            ]
        )
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            children=[
                                html.H4(
                                    f"{pretty_value[kind]} 정보",
                                    className="mb-3",
                                    style={"margin-bottom": "1rem"},
                                ),
                                input_list,
                                html.H6(id=f"n_{kind}s"),
                                dbc.Button(
                                    id=f"{kind}_reset_selection",
                                    children="초기화",
                                    color="primary",
                                ),
                                dcc.Store(
                                    id=f"{kind}s_selected_by_option",
                                    storage_type="session",
                                ),  # 데이터를 저장하는 부분
                                dcc.Store(
                                    id=f"{kind}s_selected_by_embed",
                                    storage_type="session",
                                ),  # 데이터를 저장하는 부분
                                dcc.Store(
                                    id=f"{kind}s_for_analysis",
                                    storage_type="session",
                                ),  # 데이터를 저장하는 부분
                            ],
                            # className='form-style'
                        ),
                        width=2,
                        # className="h-1",
                    ),
                    dbc.Col(
                        html.Div(
                            children=[
                                html.H4(f"{pretty_value[kind]} 차원 축소 그래프"),
                                html.Br(),
                                dcc.Graph(
                                    id=f"{kind}_emb_graph", style={"margin-top": 0}
                                ),
                            ],
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                children=[
                                    html.H4(f"선택된 {pretty_value[kind]}들의 분포"),
                                    html.Div(
                                        id=f"{kind}_side_graph",

                                    ),
                                ],
                                # className="h-50",
                            style={"overflow": "scroll", "height":500})
                        ],
                        # style={"overflow": "scrolly", "height": "10px"},
                    ),
                ],
                className="mb-1",
                # style={"height": "30%"},
            ),
            dbc.Button(
                id=f"{kind}_run",
                children="RUN",
                className="w-100",
                # style={"margin-top": "-3rem"},
            ),
        ],
        # className="hstack",
    )


item_top = html.Div(
    id="item_top_poster",
    children=[html.P("골라야 볼 수 있습니다.")],
)

choose_rerank = html.Div(
    [
        html.P("Reranking Options"),
        dcc.Markdown(
            """$$\\alpha \\cdot rel(i) + (1 - \\alpha) \\cdot obj(i)$$
            """,
            mathjax=True,
        ),
        html.Br(),
        html.Div(
            dbc.RadioItems(
                id="rerank_obj",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                options=[
                    {"label": "Diversity(Cosine)", "value": "diversity(cos)"},
                    {"label": "Diversity(Jaccard)", "value": "diversity(jac)"},
                    {"label": "Serendipity(PMI)", "value": "serendipity(pmi)"},
                    {"label": "Serendipity(Jaccard)", "value": "serendipity(jac)"},
                    {"label": "Novelty", "value": "novelty"},
                ],
                inline=True,
            ),
        ),
        html.Div(
            [
                dcc.Input(
                    id="rerank_alpha",
                    type="number",
                    placeholder="Type alpha value",
                    min=0,
                    max=1,
                    step=0.1,
                ),
            ]
        ),
    ]
)


# 유저 분석
# user_analysis = html.Div(id="user_deep_analysis")

# test = html.Div(html.P(id="testin", children="gogo"))

layout = html.Div(
    children=[
        gct.get_navbar(has_sidebar=False),
        # test,
        html.Div(
            children=[
                header_exp,
                dbc.Spinner(
                    header_user_or_item,
                ),
                # TODO: Input 옵션들 아래 결과랑 분리 해두기
                input_optinos := html.Div(id="input_options"),
                # html.Div(id="item_top_poster"),
                # html.Div(id="rerank_box"),
                html.Div(
                    id="deep_analysis_page",
                    # style={"height":40}
                ),
                # html.Div(id="item_related_users"),
            ],
            className="container",
            style={"margin-top": "4rem"},  # navbar에 가려지는것 방지
        ),
        dcc.Store(id="trash"),  # 아무런 기능도 하지 않고, 그냥 콜백의 아웃풋 위치만 잡아주는 녀석
        dcc.Store(id="store_selected_exp"),
        dcc.Store(id="store_exp_names", storage_type="session"),
        dcc.Store(id="store_exp_ids", storage_type="session"),
        dcc.Store(id="store_exp_column", storage_type="session"),
    ],
)


### 고객이 정한 장바구니가 담긴 store id가 필요함
##그거 토대로 버튼 그룹을 구성해야 함
@callback(
    Output("exp_id_for_deep_analysis", "options"),
    Input("store_exp_names", "data"),
    State("store_exp_ids", "data"),
)
def show_exp_choice(exp_name, exp_id):
    if exp_id == None:
        # TODO: 모델이 선택되지 않으면 Alert 띄워주기
        raise PreventUpdate
    option = [{"label": i, "value": j} for i, j in zip(exp_name, exp_id)]
    return option


# 고객이 장바구니에서 원하는 exp_id를 선택하면 그에 대한 user, item을 불러온다.
@callback(
    Output("show_user_or_item", "options"),
    Output("show_user_or_item", "value"),
    # Output(progress_bar_DA, "value", ),
    # Input(first_interval, "n_intervals"),
    Input("exp_id_for_deep_analysis", "value"),
    State("store_user_state", "data"),
    State("store_user_dataset", "data"),
    prevent_initial_call=True,
)
def choose_experiment(
    # n_interval,
    exp,
    vip,
    dataset_name,
):
    if exp is None:
        raise PreventUpdate
    global user
    global item
    global uniq_genre

    params = {"ID": vip["username"], "dataset_name": dataset_name, "exp_id": exp}
    # params = {"ID": 'mkdir', "dataset_name": 'ml-1m', "exp_id": 140}
    # print(params)
    user = requests.get(gct.API_URL + "/frontend/user_info", params=params).json()
    # print(user)
    user = pd.DataFrame.from_dict(data=user, orient="tight")
    user.columns = [
        "user_id",
        "gender",
        "age",
        "occupation",
        "user_profile",
        "pred_item",
        "xs",
        "ys",
        "recall",
    ]

    user = user.set_index("user_id")
    item = requests.get(gct.API_URL + "/frontend/item_info", params=params).json()
    item = pd.DataFrame.from_dict(data=item, orient="tight")

    item.columns = [
        "item_id",
        "movie_title",
        "genre",
        "release_year",
        "item_pop",
        "item_url",
        "item_profile_user",
        "recommended_users",
        "xs",
        "ys",
    ]
    item["recommended_users"] = item["recommended_users"].apply(
        lambda d: d if isinstance(d, list) else []
    )
    item["release_year"] = item["release_year"].astype(np.int16)
    item = item.set_index("item_id")
    item["selected"] = 0
    item["len"] = item["recommended_users"].apply(len)
    uniq_genre = set()
    for i in item["genre"]:
        uniq_genre |= set(i.split(" "))
    uniq_genre = [*uniq_genre]

    option = [
        {"label": "item", "value": "item"},
        {"label": "user", "value": "user"},
    ]
    # print(item.describe())
    return (
        option,
        None,
    )


# @callback(
#         Output("deep_analysis_page", "children"),
#         Input("da_input_tabs","active_tab"),
#         State("da_input_tabs","active_tab"),
# )
# def draw_inputs(n, actived_tab):
#     if ctx.triggered_id == "exp_id_for_deep_analysis":
#         return None
#     if actived_tab == "tab_user":
#         print(123)
#         user_selection = html.Div(
#                 children=[
#                     get_input_options(user=user,
#                                       kind="user"),
#                 ])
#         return [
#                 user_selection,
#                 html.Div(id="rerank_box"),
#                 html.Div(id="user_deep_analysis"),
#                 ]
#     elif actived_tab == "tab_item":
#         print(123656)
#         year_min = item["release_year"].min()
#         year_max = item["release_year"].max()

#         item_selection = html.Div(
#                 children=[
#                     get_input_options(year_min=year_min,
#                                       year_max=year_max,
#                                       kind="item")
#                 ])
#         return [
#                 item_selection,
#                 html.Div(id="item_top_poster",),
#                 html.Div(id="item_related_users",)
#         ]

# 유저 페이지를 띄울지, 아이템 페이지를 띄울지
@callback(
    Output("deep_analysis_page", "children"),
    Input("show_user_or_item", "value"),
    Input("exp_id_for_deep_analysis", "value"),
    prevent_initial_call=True,
)
def display_overall(val, exp_id):
    if ctx.triggered_id == "exp_id_for_deep_analysis":
        return None
    else:
        if exp_id == None:
            return None
        if val == "item":  # 아이템을 선택함
            year_min = item["release_year"].min()
            year_max = item["release_year"].max()

            item_selection = html.Div(
                children=[
                    get_input_options(year_min=year_min, year_max=year_max, kind="item")
                ]
            )
            return [
                item_selection,
                html.Div(
                    id="item_top_poster",
                ),
                html.Div(
                    id="item_related_users",
                ),
            ]

        elif val == "user":
            user_selection = html.Div(
                children=[
                    get_input_options(user=user, kind="user"),
                    html.Div(id="rerank_box"),

                ]
            )
            return [
                user_selection,
                # html.Div(id="rerank_box"),
                dbc.Spinner(html.Div(id="user_deep_analysis")),
            ]


#########################################################
######################## 아이템 ##########################
#########################################################

# 옵션으로 선택한 아이템을 store1에 저장
@callback(
    Output("items_selected_by_option", "data"),
    Input("selected_genre", "value"),
    Input("selected_year", "value"),
)
def save_items_selected_by_option(genre, year):
    item_lst = item.copy()
    if genre is not None:
        item_lst = item_lst[
            item_lst["genre"].str.contains(
                "".join([*map(lambda x: f"(?=.*{x})", genre)]) + ".*", regex=True
            )
        ]
    item_lst = item_lst[
        (item_lst["release_year"] >= year[0]) & (item_lst["release_year"] <= year[1])
    ]
    return item_lst.index.to_list()


# embed graph에서 선택한 아이템을 store2에 저장
@callback(
    Output("items_selected_by_embed", "data"),
    Input("item_emb_graph", "selectedData"),
    State("items_selected_by_option", "data"),
)
def save_items_selected_by_embed(emb, data_from_option):
    if (emb is None) or (not emb['points']):
        raise PreventUpdate
    item_idx = []
    for i in emb["points"]:
        if i["curveNumber"] == 0:
            item_idx.append(i["pointNumber"])
    item_lst = item.iloc[item_idx]
    if len(data_from_option) != len(item):
        # 옵션으로 그림을 그리면 두번에 걸쳐서 그림을 넣기 때문에 아이템 순서가 달라진다.
        item_lst = selected_item.iloc[item_idx]

    emb_set = set(item_lst.index.to_list())
    option_set = set(data_from_option)
    item_lst = list(emb_set & option_set)

    return item_lst


# 최근에 선택한 아이템을 최종 store에 저장
@callback(
    Output("items_for_analysis", "data"),
    Output("n_items", "children"),
    Input("items_selected_by_embed", "data"),
    Input("items_selected_by_option", "data"),
    State("items_selected_by_embed", "data"),
    State("items_selected_by_option", "data"),
)
def prepare_analysis(trigger_embed, trigger_option, state_embed, state_option):
    if ctx.triggered_id == "items_selected_by_embed":
        return trigger_embed, f"selected items: {len(trigger_embed)}"
    else:
        return trigger_option, f"selected items: {len(trigger_option)}"


# 최근에 저장된 store 기준으로 임베딩 그래프를 그림
@callback(
    Output("item_emb_graph", "figure"),
    Input("items_selected_by_option", "data"),
)
def update_graph(store1):
    item["selected"] = "Not Selected"
    item.loc[store1, "selected"] = "Selected"

    global selected_item
    selected_item = item.loc[item["selected"] == "Selected"]
    # print("selected", selected_item.index)
    Notselected_item = item.loc[item["selected"] != "Selected"]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=selected_item["xs"],
            y=selected_item["ys"],
            name="selected       ",
            mode="markers",
            marker_color="green",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=Notselected_item["xs"],
            y=Notselected_item["ys"],
            name="Not selected",
            marker_color="red",
        )
    )
    fig.add_trace(go.Scatter(x=[0], y=[0], name=" ", marker_color="white"))

    fig.update_traces(mode="markers", opacity=0.6)
    fig.update_layout(
        # title="Item embedding plot",
        yaxis_zeroline=True,
        xaxis_zeroline=False,
        margin={},
        template='ggplot2',
    )
    return fig


# 최근에 저장된 store 기준으로 사이드 그래프를 그림
@callback(
    Output("item_side_graph", "children"),
    Input("items_selected_by_option", "data"),
    Input("items_selected_by_embed", "data"),
)
def update_graph(store1, store2):
    if ctx.triggered_id == "items_selected_by_option":
        tmp = item.loc[store1]
    else:
        if not store2:
            raise PreventUpdate
        tmp = item.loc[store2]

    year = px.histogram(tmp, x="release_year")
    year.update_layout(
        template='ggplot2'
        )
    genre_counter = Counter()
    for i in tmp["genre"]:
        genre_counter += Counter(i.split())
    genre_counter = dict(
        sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)
    )
    genre_fig = daf.plot_info_counter(genre_counter, "genre")
    return (dcc.Graph(figure=year), dcc.Graph(figure=genre_fig))


# 임베딩 그래프에서 선택할 시 옵션 비활성화, 초기화 눌렀을 때만 다시 활성화
# @callback(
#     Output("selected_genre", "disabled"),
#     Output("selected_year", "disabled"),
#     Input("item_reset_selection", "n_clicks"),
#     Input("item_emb_graph", "selectedData"),
#     State("items_selected_by_option", "data"),
#     prevent_initial_call=True,
# )
# def disable_options(able, disable, option):
#     # if ctx.triggered_id == "item_reset_selection" or (len(option) == len(item)):
#     if ctx.triggered_id == "item_reset_selection":
#         if not disable['points']:
#             pass
#         return False, False
#     else:
#         return True, True


# 초기화 버튼 누를 때 선택 초기화
@callback(
    Output("selected_genre", "value"),
    Output("selected_year", "value"),
    Input("item_reset_selection", "n_clicks"),
)
def item_reset_selection(value):
    return [], [item["release_year"].min(), item["release_year"].max()]


# 초기화 버튼을 누르지 않더라도 위에서 값을 바꾸면 다시 run 누를 수 있도록 수정
@callback(
    Output("item_run", "n_clicks"),
    Input("item_reset_selection", "n_clicks"),
    Input("items_selected_by_option", "data"),
    Input("items_selected_by_embed", "data"),
    prevent_intial_call=True,
)
def item_reset_selection(v1, v2, v3):
    return 0


#### item run 실행 시 실행될 함수들 #####

# 아이템 포스터 카드 표시(top pop 10, top rec 10)
@callback(
    Output("item_top_poster", "children"),
    Input("item_run", "n_clicks"),
    State("items_for_analysis", "data"),
    prevent_initial_call=True,
)
def draw_item_top(value, data):
    if value != 1:
        raise PreventUpdate
    else:
        pop = (
            item.loc[data].sort_values(by=["item_pop"], ascending=False).head(10).index
        )
        pop_lst = [make_card(item) for item in pop]  # 보여줄 카드 갯수 지정 가능
        rec = item.loc[data].sort_values(by=["len"], ascending=False).head(10).index
        rec_lst = [make_card(item) for item in rec]  # 보여줄 카드 갯수 지정 가능
        children = [
            html.H3("선택한 아이템 인기도 top 10", className="mt-4 mb-3"),
            dbc.Row(
                children=pop_lst,
                className="g-0 d-flex flex-row flex-nowrap overflow-auto",
                style={
                    # "overflow": "scroll",
                    "height": 548
                },
            ),
            html.H3("선택한 아이템 추천횟수 top 10", className="mt-5 mb-3"),
            dbc.Row(
                children=rec_lst,
                className="d-flex flex-row flex-nowrap overflow-auto",
                style={
                    # "overflow": "scroll",
                    "height": 548
                },
            ),
            html.Br(),
        ]
        return children


# 아이템 관련 유저 그리기
@callback(
    Output("item_related_users", "children"),
    Input("item_run", "n_clicks"),
    State("items_for_analysis", "data"),
    prevent_initial_call=True,
)
def draw_item_related_users(value, data):
    if value != 1:
        raise PreventUpdate
    else:
        (
            age_Counter_profile,
            age_Counter_rec,
            gender_Counter_profile,
            gender_Counter_rec,
            occupation_Counter_profile,
            occupation_Counter_rec,
        ) = daf.get_user_side_by_items(data, item, user)
        age = dcc.Graph(
            figure=daf.plot_age_counter(age_Counter_profile, age_Counter_rec)
        )
        gender = dcc.Graph(
            figure=daf.plot_gender_counter(gender_Counter_profile, gender_Counter_rec)
        )
        occupation = dcc.Graph(
            figure=daf.plot_occupation_counter(
                occupation_Counter_profile, occupation_Counter_rec
            )
        )

        children = [
            html.H3("아이템을 시청한 유저들 vs. 아이템을 추천받은 유저들", className="mt-4 mb-3"),
            html.Hr(),
            html.Div(
                [
                    age,
                    gender,
                    occupation,
                ]
            ),
        ]
        return children


#########################################################
######################## 유저 ###########################
#########################################################


# 선택한 유저들을 store1에 저장
@callback(
    Output("users_selected_by_option", "data"),
    Input("selected_age", "value"),
    Input("selected_gender", "value"),
    Input("selected_occupation", "value"),
    Input("selected_wrong", "value"),
)
def save_users_selected_by_option(age, gender, occupation, wrong):
    user_lst = user.copy()
    if age:
        user_lst = user_lst[user_lst["age"].isin(age)]
    if gender:
        user_lst = user_lst[user_lst["gender"] == gender]
    if occupation:
        user_lst = user_lst[user_lst["occupation"].isin(occupation)]
    if wrong:
        user_lst = user_lst[user_lst["recall"] <= 0.5]
    return user_lst.index.to_list()


# user embed graph에서 선택한 유저들을 store2에 저장
@callback(
    Output("users_selected_by_embed", "data"),
    Input("user_emb_graph", "selectedData"),
    State("users_selected_by_option", "data"),
)
def save_users_selected_by_embed(emb, data_from_option):
    if (emb is None) or (not emb['points']):
        raise PreventUpdate
    user_idx = []
    for i in emb["points"]:
        if i["curveNumber"] == 0:
            user_idx.append(i["pointNumber"])
    user_lst = user.iloc[user_idx]
    if len(data_from_option) != len(user):
        # 옵션으로 그림을 그리면 두번에 걸쳐서 그림을 넣기 때문에 아이템 순서가 달라진다.
        user_lst = selected_user.iloc[user_idx]

    emb_set = set(user_lst.index.to_list())
    option_set = set(data_from_option)
    user_lst = list(emb_set & option_set)

    return user_lst


# 최근에 선택한 유저를 최종 store에 저장
@callback(
    Output("users_for_analysis", "data"),
    Output("n_users", "children"),
    Input("users_selected_by_option", "data"),
    Input("users_selected_by_embed", "data"),
)
def prepare_analysis(val1, val2):
    if ctx.triggered_id == "users_selected_by_option":
        return val1, f"selected users: {len(val1)}"
    else:
        return val2, f"selected users: {len(val2)}"


# 최근에 저장된 store 기준으로 유저 임베딩 그래프를 그림
@callback(
    Output("user_emb_graph", "figure"),
    Input("users_selected_by_option", "data"),
)
def update_graph(store1):
    user["selected"] = "Not Selected"
    user.loc[store1, "selected"] = "Selected"

    global selected_user
    selected_user = user.loc[user["selected"] == "Selected"]
    Notselected_user = user.loc[user["selected"] != "Selected"]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=selected_user["xs"],
            y=selected_user["ys"],
            name="selected       ",
            mode="markers",
            marker_color="green",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=Notselected_user["xs"],
            y=Notselected_user["ys"],
            name="Not selected",
            marker_color="red",
        )
    )
    fig.add_trace(go.Scatter(x=[0], y=[0], name=" ", marker_color="white"))

    fig.update_traces(mode="markers", opacity=0.6)
    fig.update_layout(
        # title="user embedding plot",
        yaxis_zeroline=True,
        xaxis_zeroline=False,
        margin={},
        template='ggplot2'
    )
    return fig


# #최근에 저장된 store 기준으로 사이드 그래프를 그림
@callback(
    Output("user_side_graph", "children"),
    Input("users_selected_by_option", "data"),
    Input("users_selected_by_embed", "data"),
)
def update_graph(store1, store2):
    if ctx.triggered_id == "users_selected_by_option":
        tmp = user.loc[store1]
        age = daf.plot_info_counter(Counter(tmp["age"]), "Age")
        gender = daf.plot_info_counter(Counter(tmp["gender"]), "Gender")
        occupation = daf.plot_info_counter(Counter(tmp["occupation"]), "Occupation")
        return (
            dcc.Graph(figure=age),
            dcc.Graph(figure=gender),
            dcc.Graph(figure=occupation),
        )
    else:
        if not store2:
            raise PreventUpdate
        tmp = user.loc[store2]
        # tmp = tmp[tmp["selected"] == "Selected"]
        age = daf.plot_info_counter(Counter(tmp["age"]), "Age")
        gender = daf.plot_info_counter(Counter(tmp["gender"]), "Gender")
        occupation = daf.plot_info_counter(Counter(tmp["occupation"]), "Occupation")
        return (
            dcc.Graph(figure=age),
            dcc.Graph(figure=gender),
            dcc.Graph(figure=occupation),
        )


# 초기화 버튼 누를 때 선택 초기화
@callback(
    Output("selected_age", "value"),
    Output("selected_gender", "value"),
    Output("selected_occupation", "value"),
    Output("selected_wrong", "value"),
    Output("rerank_alpha", "value"),
    Output("rerank_obj", "value"),
    Input("user_reset_selection", "n_clicks"),
)
def user_reset_selection(value):
    return [], [], [], [], 0, 0

# 초기화 버튼을 누르지 않더라도 위에서 값을 바꾸면 다시 run 누를 수 있도록 수정
@callback(
    Output("user_run", "n_clicks"),
    Input("user_reset_selection", "n_clicks"),
    Input("users_selected_by_option", "data"),
    Input("users_selected_by_embed", "data"),
)
def user_reset_selection(val1,val2,val3):
    return 0


######################### 리랭킹 진행 ##############################
######################### 리랭킹 진행 ##############################
######################### 리랭킹 진행 ##############################

# 백엔드에 리랭킹 계산 요청하고 받은 것으로 바로 모든 그림을 그려냄
# 그리고 통째로 리턴
@callback(
    Output("user_deep_analysis", "children"),
    Input("user_run", "n_clicks"),  #  선택하기 전까지 비활성화도 필요
    State("users_for_analysis", "data"),
    State("rerank_obj", "value"),
    State("rerank_alpha", "value"),
    State("exp_id_for_deep_analysis", "value"),
    State("store_user_state", "data"),
    State("store_user_dataset", "data"),
    prevent_initial_call=True,
)
def draw_rerank(value, user_lst, obj, alpha, exp_id, id, dataset):
    if value != 1:
        raise PreventUpdate
    else:
        tmp = user.loc[user_lst]
        params = {
            "ID": id["username"],
            "dataset_name": dataset,
            "exp_id": exp_id,
            "n_candidates": 50,  # 추후 고객이 지정할 수 있도록 하면 좋을 듯.
            "objective_fn": obj,
            "alpha": alpha,
            "user_ids": user_lst,
        }
        # print(params)
        # params = {
        #     "ID": "mkdir",
        #     "dataset_name": "ml-1m",
        #     "exp_id": exp_id,
        #     "n_candidates": 50,
        #     "objective_fn": "diversity(cos)",
        #     "alpha": 0.5,
        #     "user_ids": user_lst,
        # }
        # params = None
        # print(params)
        get_dict = requests.get(gct.API_URL + "/frontend/rerank_users", params).json()
        diff_metric = get_dict["metric_diff"]
        diff_metric = pd.DataFrame.from_dict(data=diff_metric, orient="tight")
        reranked_lst = get_dict["rerank"]
        reranked_lst = pd.DataFrame.from_dict(data=reranked_lst, orient="tight")
        reranked_lst = reranked_lst.set_index("user_id")
        # diff는 데이터프레임화 가능
        # reranked는 시리즈화 가능
        tmp["reranked_item"] = reranked_lst
        # 지표와 아이템들을 바로 merge할 수 있는 상태로 받는다.

        # 첫번째 - 지표 변화
        sub = diff_metric.loc["rerank"] - diff_metric.loc["origin"]

        # print(len(tmp.loc["1", "pred_item"][:10]))
        # 두번째 - 아이템 포스터
        origin_item = set()
        rerank_item = set()
        profile_item = set()
        for i in user_lst:
            origin_item |= set(tmp.loc[i, "pred_item"][:10])
            rerank_item |= set(tmp.loc[i, "reranked_item"])
            profile_item |= set(tmp.loc[i, "user_profile"])
        new_item = rerank_item - origin_item
        # print(new_item)
        pop = (
            item.loc[list(origin_item)]
            .sort_values(by=["len"], ascending=False)
            .head(10)
            .index
        )
        pop_lst = [make_card(item) for item in pop]
        rer = (
            item.loc[list(rerank_item)]
            .sort_values(by=["len"], ascending=False)
            .head(10)
            .index
        )
        rer_lst = [make_card(item) for item in rer]
        new = (
            item.loc[list(new_item)]
            .sort_values(by=["len"], ascending=False)
            .head(10)
            .index
        )
        new_lst = [make_card(item) for item in new]
        def get_metric_list(metric, i, is_incremental):
            if is_incremental:
                color = "#7286D3"
                plus="+"
            else:
                color = "#CD0404"
                plus=""
            return dbc.Card(
                        [
                            dbc.CardHeader(html.H6(f"{pretty_metric[metric]}"), ),
                            dbc.CardBody(
                                [
                                    html.H6(f"{plus}{round(i,2)}", className="card-title",style={"color":color}),
                                ]
                            ),],
                        style={"width": "12rem"},
                        )
        indicator = dbc.Row(
            children=[
                    
                html.H3("리랭킹 후 지표 변화"),
                html.H5("증가한 지표"),
                html.Div(
                    children=[
                        get_metric_list(metric, i, is_incremental=True)
                        for metric, i in zip(sub.index, sub) if i>=0 
                    ],
                    className="hstack gap-1"
                ),
                html.H5("감소한 지표"),
                    html.Div(
                    children=[
                        get_metric_list(metric, i, is_incremental=False)
                        for metric, i in zip(sub.index, sub) if i<0 
                    ],
                    className="hstack gap-1"
                ),
            ],
            className="gap-3 my-3"
        )
        item_poster = html.Div(
            children=[
                html.H3("리랭킹 전 많이 추천된 아이템 top 10", className="mt-5 mb-3"),
                dbc.Row(children=pop_lst, 
                        className= 'd-flex flex-row flex-nowrap overflow-auto',
                        style={"height": 548}),
                html.H3("리랭킹 후 많이 추천된 아이템 top 10", className="mt-5 mb-3"),
                dbc.Row(children=rer_lst, 
                        className= 'd-flex flex-row flex-nowrap overflow-auto',
                        style={"height": 548}),
                html.H3("기존에 추천되지 않은 아이템 top 10", className="mt-5 mb-3"),
                dbc.Row(children=new_lst, 
                        className= 'd-flex flex-row flex-nowrap overflow-auto',
                        style={"height": 548}),
            ],
            className="gap-3 mb-3"
        )
        item_side = dbc.Row(
            children=[
                html.H3("리랭킹 관련한 장르 분포", className='mt-5 mb-2'),
                html.Hr(className='mb-0'),
                dcc.Graph(
                    figure=daf.plot_usergroup_genre(
                        item, origin_item, rerank_item, profile_item, tmp
                    )
                ),
            ],
            # className=""
        )
        children = [indicator, item_poster, item_side]

        return children
