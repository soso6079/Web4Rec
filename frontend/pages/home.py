import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from .utils import global_component as gct

dash.register_page(__name__, path='/')

def get_feature_component(img_url:str, emoji:str,
            title:str, description:str, img_position:str="left") -> dbc.Row:
    IMAGE_COL_WIDTH:int=7
    TEXT_COL_WIDTH:int=5
    feature_cn = "feature-image rounded-2 border border-primary border-4"
    if img_position == "left":
        return dbc.Row([
                    dbc.Col(
                        html.Img(src=img_url, className=feature_cn),
                    width=IMAGE_COL_WIDTH),
                    dbc.Col([
                        html.H1(emoji, className="text-start"),
                        html.H3(title),
                        html.H5(description),
                        ], width=TEXT_COL_WIDTH)
                    ], className="pt-4 pb-4")

    elif img_position == "right":
        return dbc.Row([
                    dbc.Col([
                        html.H1(emoji, className="text-start"),
                        html.H3(title),
                        html.H5(description)
                    ], width=TEXT_COL_WIDTH),
                    dbc.Col([
                        html.Img(src=img_url, className=feature_cn),
                    ], width=IMAGE_COL_WIDTH)
                        ], className="pt-4 pb-4")
    else:
        ValueError("img_url must be left or right")

img_url = "https://user-images.githubusercontent.com/67850665/217193988-a3b45bcd-ce8c-4e89-a8be-f95ae8f6f433.png"

feature_compare_table = get_feature_component(
    img_url=img_url,
    emoji="📋",
    title="각 실험 별 지표 비교 테이블",
    description="사용자가 실험한 모델의 정성, 정량 지표를 계산한 결과를 테이블로 확인할 수 있습니다.",
    img_position="left"
)


workflow_img_url = "https://user-images.githubusercontent.com/55279227/217210198-8df93292-b18d-4ee0-81dc-03f768e88c39.jpg"

img_url = "https://user-images.githubusercontent.com/76675506/216320888-7b790e97-61af-442c-93b3-c574ed0c119e.png"
feature1 = get_feature_component(
    img_url=img_url,
    emoji="🔍",
    title="모델의 임베딩을 다양한 관점에서 살펴볼 수 있습니다.",
    description="사용자가 선택한 옵션에 따라, 임베딩 그래프를 인터랙티브하게 변화시킬 수 있습니다.",
    img_position="right"
)

img_url = "https://user-images.githubusercontent.com/67850665/217196527-9699cd4d-df74-42fd-8a7d-61030cbf0ef4.png"
feature2 = get_feature_component(
    img_url=img_url,
    emoji="😊",
    title="실험별 지표 비교와 리랭킹 기능을 사용할 수 있습니다.",
    description="다양한 실험의 지표를 한 눈에 그래프로 비교할 수 있으며, 리랭킹을 통해 다양한 정성지표 값을 상승 시킬 수 있습니다.",
    img_position="left"
)

problem_intro = html.Div([
            html.H1("💡"),
            html.H3("추천시스템 문제는 조금 다릅니다."),
            html.H5("일반적으로 AI 모델에서는 높은 정확성, 혹은 재현율이 서비스 사용자의 만족으로 이어집니다."),
            html.H5("하지만 추천시스템에서는 그렇지 않습니다.", className="fst-italic"),
            html.H5(["정량적 지표인 정확성, 재현율 외에도 ", html.Span("정성적 지표", className="text-danger"), "(다양성, 참신성, 의외성 등)를 같이 고려해야 합니다."], ),
])
layout = html.Div([
    dbc.NavbarSimple([
        dbc.NavItem(dcc.Link(dbc.Button("시작하기!", className=" fs-6 mt-1",style={'margin-right':'20%','width':'25rem'}, color="light"),href="/login"),),
        ], brand=gct.BRAND_LOGO, brand_style={"margin-left":'47%', 'font-size':"2rem", 'color':'#FFFAF0'}
        , color="primary", class_name="home-navbar", sticky="top", fluid=True),
    html.Div([
        html.Div([
            html.Div([
            html.H1('프로젝트 소개', className="pt-3 text-center fs-1 mx-auto"),
            # dcc.Link(dbc.Button("시작하기!", className=" fs-6 mt-3 mb-4", color="light"),href="/login"),
            ], className="hstack"),
            html.Hr(),
            
            problem_intro,
            
            html.H4([gct.BRAND_LOGO+'은 이를 해결할 수 있는 ', html.Span('실험 관리 툴', className="text-info"),'입니다.'], 
            className="mt-5 pt-4 pb-3 text-center fs-1"),
            dbc.Row([
                    dbc.Col([
                        html.Img(src=workflow_img_url, className="feature-image rounded-2 border border-primary border-4"),
                    ], width={'size':10, 'offset':1})
                    ], 
                className="center"),
            html.Hr(),
            feature_compare_table,
            feature1,
            feature2,
            html.Br(),
            dcc.Link(dbc.Button("시작하기!", className="position-absolute top-105 start-50 translate-middle w-25 fs-2 my-4"), href="/login"),
            html.Br(className="h-25")
            ], className="container position-relative pb-4"),
    ], className="pb-5", style={'background-color': '#FFFAF0'}),
])