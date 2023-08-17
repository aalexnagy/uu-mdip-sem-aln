from os import name, path
from datetime import date, timedelta
import math

import pandas as pd
# from pandas.core.indexes import multi
# from pandas.io.formats import style
# import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import (
    dcc,
    html,
    Input,
    Output,
)


# POMOCNE FCE
def weeks_for_year(year):
    year = int(year)
    last_week = date(year, 12, 28)
    return int(last_week.isocalendar()[1])


# app = Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "color": "#262626",
    "background-color": "#fdfdfd",
    "border-right": "1px solid #262626"
}
# content
CONTENT_STYLE = {
    "margin-left": "18.5rem",
    "margin-right": "0.0rem",
    "padding": "0.25rem 0.25rem",
}
# page
PAGE_STYLE = {
    "color": "#262626",
    "background-color": "#fdfdfd"
}

# -- Import and clean data (importing csv into pandas)
folder = path.dirname(__file__)
data = path.join(folder, "data")


df = pd.read_csv(
    path.join(data, "MDIP_data4.csv"), sep=";", encoding="ISO-8859-1", low_memory=False
)
df.set_index(["Index"], drop=True, inplace=True)
df.index = pd.to_datetime(df.index)
df = df[
    [
        "Castka",
        "Autor",
        "CisloRadku",
        "CisloUcet",
        "DatumPorizeno",
        "DatumPorizeno_D",
        "DatumPorizeno_M",
        "DatumPorizeno_Y",
        "DatumPorizeno_Q",
        "DatumPorizeno_W",
        "DatumPripad",
    ]
].copy()


# colors dictionary
my_colors = ["firebrick", "royalblue", "rgba(249, 180, 45, 1)", "forestgreen"]
# hodnoty do dropdownu
years = df.DatumPorizeno_Y.unique()
agg_dict = {"W": "Týdny", "MS": "Měsíce", "QS": "Kvartály"}

# ------------------------------------------------------------------------------
# App layout ===================================================================
# ------------------------------------------------------------------------------
# DASHBOARD ELEMENTS ===========================================================


theme_select = [
    dbc.Label("Barevné schéma grafů: ", html_for="slct_theme"),
    dcc.Dropdown(
        id="slct_theme",
        options=[{'label': c[0], 'value': c[1]}
                 for c in [("Světlý", "plotly_white"), ("Tmavý", "plotly_dark")]],
        multi=False,
        clearable=False,
        value="plotly_white",
    )]

db_select = [
    dbc.Label("Vyberte databázi: ", html_for="slct_db"),
    dcc.Dropdown(
        id="slct_db",
        options=[{"label": "TEST_DB", "value": "test"}],
        multi=False,
        clearable=False,
        value="test",
    )]

year_select = [
    dbc.Label("Vyverte rok: ", html_for="slct_year"),
    dcc.Dropdown(
        id="slct_year",
        options=[{"label": y, "value": y} for y in years],
        multi=False,
        clearable=False,
        value=2021,
        # style={"width": "40%"},
    )]

aggregation_select = [
    dbc.Label("Seskupit: ", html_for="slct_agg"), dcc.Dropdown(
        id="slct_agg",
        options=[
            {"label": "Týdně", "value": "W"},
            {"label": "Měsíčně", "value": "MS"},
            {"label": "Kvartálně", "value": "QS"},
        ],
        multi=False,
        clearable=False,
        value="MS",
        # style={"width": "40%"},
    )]

inv_month_limit = [
    dbc.Label("Měsíční limit: ", html_for="monthly_limit"),
    dbc.Col(
        dbc.Input(
            id="monthly_limit",
            type="number",
            placeholder="Zadejte číslo",
            value="200",
            disabled=True,
            className="me-3"
        ),
    )
]

sidebar = html.Div(
    children=[
        html.H2("MDIP ALN Dashboard", className="display-5"),
        html.Hr(className="p-0 m-0"),
        dbc.Row(theme_select, class_name="mb-1"),
        dbc.Row(db_select),
        dbc.Row(year_select),
        dbc.Row(aggregation_select),
        dbc.Row(inv_month_limit)
    ],
    style=SIDEBAR_STYLE,
)

vyvoj_uctu = (
    html.H3(
        "Vývoj nákladových a výnosových účtů",
        style={"margin-bottom": "0.5rem"},
    ),
    html.Hr(className="p-0 m-0"),
    dcc.Graph(
        id="graph2", style={"display": "inline-block"}
    ),
    dcc.Graph(
        id="bar_zisk",
        style={
            "display": "inline-block", "width": "40%"
        }
    )
)

# ------------------------------------------------------------------------------
# App layout ===================================================================
# ------------------------------------------------------------------------------
# Sestavime App layout ===================================================================
app.layout = html.Div(
    (
        sidebar,
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(
                            "Počet zpracovaných faktur a metody zpracování",
                            style={"margin-bottom": "0.5rem"},
                        ),
                        html.Hr(className="p-0 m-0"),
                        dcc.Graph(
                            id="graph1",
                            style={
                                "display": "inline-block",
                                "margin-right": "0.5rem",
                                "width": "45%",
                            },
                        ),
                        dcc.Graph(
                            id="pie_chart", style={"display": "inline-block", "margin-right": "0.5rem", "width": "20%"}
                        ),
                        dcc.Graph(
                            id="summary", style={"display": "inline-block", "width": "33%", }
                        ),
                    ],
                    style=CONTENT_STYLE,
                ),
                html.Div(
                    children=[
                        html.H3(
                            "Vývoj nákladových a výnosových účtů",
                            style={"margin-bottom": "0.5rem"},
                        ),
                        html.Hr(className="p-0 m-0"),
                        dbc.Row(
                            [dbc.Col(dcc.Graph(
                                id="graph2", style={"display": "inline-block"}
                            )),
                                dbc.Col(id="card_zisk")])
                    ],
                    style=CONTENT_STYLE,
                ),
            ],
            style={"overflow": "scroll"}
        ),
    ), style=PAGE_STYLE,
)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    # Output(component_id="inv_amounts_info", component_property="children"),
    [Output(component_id="graph1", component_property="figure"),
     Output(component_id="pie_chart", component_property="figure"),
     Output(component_id="summary", component_property="figure")],
    [Input(component_id="slct_year", component_property="value"),
     Input(component_id="slct_agg", component_property="value"),
     Input(component_id="monthly_limit", component_property="value"), Input(component_id="slct_theme", component_property="value")],
)
def update_faktury(year_slctd, agg_slctd, monthly_limit, theme):
    # mesicni limit
    monthly_limit = int(monthly_limit)
    # data
    dff = df[
        [
            "Castka",
            "Autor",
            "CisloRadku",
            "DatumPorizeno_M",
            "DatumPorizeno_Y",
            "DatumPorizeno_W",
            "DatumPorizeno_Q",
        ]
    ].copy()
    # data processing
    dff = dff[dff["DatumPorizeno_Y"] == year_slctd]
    dff = dff[dff["CisloRadku"] == 1]
    # pocet kvartalu v datech
    num_of_quartals = dff["DatumPorizeno_Q"].nunique()
    # pocet mesicu v datech
    num_of_months = dff["DatumPorizeno_M"].nunique()
    # redukce velikosti datasetu
    dff = dff[["Autor"]]
    # rozliseni ORC a ostatni
    df_ocr_ocr = dff[dff["Autor"] == "sahelios"]
    df_ocr_oth = dff[dff["Autor"] != "sahelios"]
    # vypocet hodnot pro pie chart
    dff_pie = [df_ocr_ocr["Autor"].count(), df_ocr_oth["Autor"].count()]
    # celkem faktur
    num_all_invoices = dff["Autor"].count()
    # agregace podle zadání z hlavního menu
    df_ocr_resample_maz = df_ocr_ocr.resample(agg_slctd).agg("count")
    df_ocr_resample_other = df_ocr_oth.resample(agg_slctd).agg("count")
    # novy dataset, vstupuje do grafu
    df_ocr_res = df_ocr_resample_maz.copy()
    df_ocr_res = df_ocr_res.rename(columns={"Autor": "OCR"})
    df_ocr_res["Other"] = df_ocr_resample_other
    df_ocr_res = df_ocr_res.fillna(0)
    # ziskam a vypocitam limity, pokud agregace
    if agg_slctd == "MS":
        limit = monthly_limit
    elif agg_slctd == "QS":
        limit = monthly_limit * 3
    elif agg_slctd == "W":
        num_of_weeks = weeks_for_year(year_slctd)
        limit = math.ceil((monthly_limit * 12) / num_of_weeks)
    # doplnim limit do datasetu
    df_ocr_res["Limit"] = limit
    # set limits
    month_limit = monthly_limit
    quartal_limit = monthly_limit * 3
    year_limit = monthly_limit * 12
    # calculate usage : Y,Q,M
    used_yearly = (num_all_invoices/year_limit)*100
    used_quarterly_avg = (
        ((num_all_invoices / num_of_quartals)/quartal_limit)*100
    )
    used_month_avg = (((num_all_invoices / num_of_months)/month_limit)*100)
    # calculate remains : Y,Q,M
    remains_yearly = 100 - used_yearly
    remains_quarterly = 100 - used_quarterly_avg
    remains_monthly = 100 - used_month_avg
    # ovetlimit : default = 0
    over_limit_yearly = 0
    over_limit_quarterly = 0
    over_limit_monthly = 0
    # pokud vice nez 100%, tak musim upravit
    # remains yearly
    if remains_yearly < 0:
        used_yearly = 100
        over_limit_yearly = -(remains_yearly)
        remains_yearly = 0
    # remains quarterly
    if remains_quarterly < 0:
        used_quarterly_avg = 100
        over_limit_quarterly = -(remains_quarterly)
        remains_quarterly = 0
    # remains monthly
    if remains_monthly < 0:
        used_month_avg = 100
        over_limit_monthly = -(remains_monthly)
        remains_monthly = 0

    # FIG 1
    # vytvorim trace pro fig 1
    trace_ocr = go.Bar(
        x=df_ocr_res.index, y=df_ocr_res["OCR"], name="OCR", marker_color=my_colors[0]
    )
    trace_oth = go.Bar(
        x=df_ocr_res.index,
        y=df_ocr_res["Other"],
        name="Ruční zpracování",
        marker_color=my_colors[1],
    )
    month_limit = go.Scatter(
        x=df_ocr_res.index,
        y=df_ocr_res["Limit"],
        mode="lines",
        name="Limit",
        line=dict(color=my_colors[2], width=4, dash="dot"),
    )
    # pridam trace do grafu
    data = [trace_ocr, trace_oth]
    layout = go.Layout(barmode="stack")
    fig = go.Figure(data=data, layout=layout)
    fig.add_trace(month_limit)
    fig.update_layout(
        template=theme,
        title="Množství a způsob zpracování faktur ({} [{}])".format(
            agg_dict[agg_slctd], year_slctd),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            y=-0.2,
            x=0.2
        )
    )
    fig.update_xaxes(title_text="Sledované období", title_standoff=25)
    fig.update_yaxes(title_text="Počet faktur [ks]", title_standoff=25)

    # FIG2 - Pie chart
    fig2 = go.Figure(
        go.Pie(
            labels=["OCR", "Other"],
            values=dff_pie,
            marker_colors=my_colors,
        )
    )
    fig2.update_layout(template=theme, title="Zastoupení metod zpracování [{}]".format(year_slctd), legend=dict(
        orientation="h",
        yanchor="top",
        xanchor="center",
        y=0,
        x=0.0
    ))
    fig2.update_traces(hoverinfo="value", textinfo="percent")

    # FIG 3
    fig3 = go.Figure()
    # Vycerpano
    fig3.add_trace(go.Bar(
        # y=["Ø Měsíc", "Ø Kvartál", "Celkem"],
        y=["Ø Měsíc", "Ø Kvartál", "Celkem"],
        x=[used_month_avg, used_quarterly_avg, used_yearly],
        name='Vyčerpáno',
        orientation='h',
        marker=dict(
            color=my_colors[3],
            line=dict(color='rgba(58, 71, 80, 1.0)', width=0)
        )
    ))
    # 100 %
    fig3.add_trace(go.Bar(
        y=["Ø Měsíc", "Ø Kvartál", "Celkem"],
        x=[remains_monthly, remains_quarterly, remains_yearly],
        name="Smluvený objem",
        orientation='h',
        marker=dict(
            color=my_colors[1],
            line=dict(color='rgba(246, 78, 139, 1.0)', width=0)
        )
    ))
    fig3.add_trace(go.Bar(
        y=["Ø Měsíc", "Ø Kvartál", "Celkem"],
        x=[over_limit_monthly, over_limit_quarterly, over_limit_yearly],
        name='Nad limit',
        orientation='h',
        marker=dict(
            # color='rgba(158, 80, 180, 0.6)',
            color=my_colors[0],
            line=dict(color='rgba(158, 80, 180, 1.0)', width=0)
        )
    ))
    # fig3.update_layout(barmode='stack')
    fig3.update_layout(
        template=theme,
        barmode='stack',
        title="Čerpání služeb za období [{}]".format(year_slctd),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            y=-0.3,
            x=0.2
        ))
    fig3.update_xaxes(title_text="Čerpáno [%]", title_standoff=25)
    return fig, fig2, fig3

# Nakladove a vynosove ucty


@ app.callback(
    # Output(component_id="inv_amounts_info", component_property="children"),
    Output(component_id="graph2", component_property="figure"),
    Output(component_id="card_zisk", component_property="children"),
    Input(component_id="slct_year", component_property="value"),
    Input(component_id="slct_agg", component_property="value"),
    Input(component_id="slct_theme", component_property="value"),


)
def update_vyvoj_uctu(year_slctd, agg_slctd, theme):
    # fig = "Test"
    # return fig
    dff = df[
        [
            "Castka",
            "Autor",
            "CisloUcet",
            "DatumPorizeno_M",
            "DatumPorizeno_Y",
            "DatumPorizeno_W",
        ]
    ].copy()
    dff = dff[dff["DatumPorizeno_Y"] == year_slctd]
    # data_5 = dff[dff["CisloUcet"] >= 500000]
    data_5 = dff[dff["CisloUcet"].between(500000, 599999)]
    data_5 = data_5["Castka"].resample(agg_slctd).agg("sum")
    # data_5 = data_5.resample(agg_slctd).agg("sum")
    data_6 = dff[dff["CisloUcet"].between(600000, 699999)]
    data_6 = data_6["Castka"].resample(agg_slctd).agg("sum")
    data_zisk = pd.DataFrame(columns=["Zisk"])
    data_zisk["Zisk"] = data_6 - data_5
    data_zisk["Line"] = 0
    # print(data_zisk)
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data_5.index,
            # y=dff[dff["Castka"].astype(str).str.startswith("^[5]+$", na=False)],
            y=data_5,
            name="Nákladové účty",
            mode="lines",
            line=dict(color="firebrick", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data_6.index,
            y=data_6,
            name="Výnosové účty",
            mode="lines",
            line=dict(color="royalblue", width=3),
        )
    )
    fig.add_trace(
        go.Bar(
            x=data_zisk.index,
            y=data_zisk["Zisk"],
            name="Zisk",
            marker_color="rgba(249, 180, 45, 0.6)",
        )
    )
    fig.update_layout(
        template=theme,
        title="Vývoj nákladových a výnosových účtů[{}]".format(year_slctd),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            y=-0.2,
            x=0.2
        )
    )
    fig.update_xaxes(title_text="Sledované období", title_standoff=25)
    fig.update_yaxes(title_text="Částka [Kč]", title_standoff=25)

    # vytvoreni obsahu karty
    zisk = data_zisk["Zisk"].sum()
    if zisk > 0:
        card_color = "success"
    elif zisk < 0:
        card_color = "danger"
    else:
        card_color = "secondary"
    card_content = [
        dbc.Card(
            dbc.CardBody(
                [html.H4("Zisk [{}]".format(year_slctd),
                         className="card-title"),
                 html.P(str(round(zisk, 2))+" Kč")], class_name="alert-"+card_color
            ),
            color=card_color,
            outline=True,
            inverse=False,
            style={"width": "18rem", "display": "inline-block"},
            class_name="my-2"
        ),
    ]

    return fig, card_content


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
