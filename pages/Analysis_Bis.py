import dash
from dash import html, dcc, Output, Input, callback
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path="/VariableHour", order=3, suppress_callback_exceptions=True)

# Charger la base de données
bike = pd.read_csv("Dashbike.csv")

# Définir les heures maximale et minimale
min_hour = bike["Hour"].min()
max_hour = bike["Hour"].max()

ordered_days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# Définir la mise en page de la page avec des range sliders
layout = html.Div(
    [
        html.H1("Study of the Impact of the Hour Variable", className="divTitle"),
        html.P(
            "In this section, we analyze the impact of the hour variable on the number of bikes rented, considering both its direct influence and its varying effects depending on the season and the day of the week. "
            "You can navigate through the three tabs below to view different interactive charts. "
            "Each chart is designed to be interactive, allowing you to adjust parameters for a more refined visualization.",
        ),
        dcc.Tabs(
            [
                dcc.Tab(
                    label=" View by Hour",
                    children=[
                        html.P(
                            "In this section, you can adjust the time window of the day to gain a more detailed view."
                        ),
                        html.Div(
                            [
                                html.Label("Hours selection"),
                                dcc.RangeSlider(
                                    id="hourly-range-slider",
                                    min=min_hour,
                                    max=max_hour,
                                    value=[min_hour, max_hour],
                                    marks={
                                        i: str(i) for i in range(min_hour, max_hour + 1)
                                    },
                                    step=1,
                                ),
                                dcc.Graph(id="hourly-mean-bikes"),
                            ]
                        ),
                    ],
                    className="custom-tabs",
                ),
                dcc.Tab(
                    label="View by Hour and Season",
                    children=[
                        html.P(
                            "In this section, you can not only adjust the time slot but"
                            " also select one or multiple seasons to obtain the view that suits you best."
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Seasons Selection: "),
                                        dcc.Checklist(
                                            id="season-checklist",
                                            options=[
                                                {"label": season, "value": season}
                                                for season in bike["Seasons"].unique()
                                            ],
                                            value=bike["Seasons"]
                                            .unique()
                                            .tolist(),  # Toutes les saisons sont sélectionnées par défaut
                                            inline=True,  # Permettre la sélection de plusieurs options
                                            style={"width": "50%", "padding": "20px"},
                                        ),
                                    ],
                                    className="checklist-container",
                                ),
                                html.Label("Hours Selection:"),
                                dcc.RangeSlider(
                                    id="seasonal-range-slider",
                                    min=min_hour,
                                    max=max_hour,
                                    value=[min_hour, max_hour],
                                    marks={
                                        i: str(i) for i in range(min_hour, max_hour + 1)
                                    },
                                    step=1,
                                ),
                                dcc.Graph(id="seasonal-mean-bikes"),
                            ]
                        ),
                    ],
                    className="custom-tabs",
                ),
                dcc.Tab(
                    label="View by Hour and Days of the week",
                    children=[
                        html.P(
                            "In this section, you can not only adjust the time slot but"
                            " also select one or multiple days of the week to obtain the view that suits you best."
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Days Selection: "),
                                        dcc.Checklist(
                                            id="day-checklist",
                                            options=[
                                                {"label": day, "value": day}
                                                for day in ordered_days
                                            ],
                                            value=ordered_days,
                                            inline=True,
                                            style={"width": "100%", "padding": "20px"},
                                        ),
                                    ],
                                    className="checklist-container",
                                ),
                                html.Label("Hours Selection:"),
                                dcc.RangeSlider(
                                    id="daily-range-slider",
                                    min=min_hour,
                                    max=max_hour,
                                    value=[min_hour, max_hour],
                                    marks={
                                        i: str(i) for i in range(min_hour, max_hour + 1)
                                    },
                                    step=1,
                                ),
                                dcc.Graph(id="daily-mean-bikes"),
                            ]
                        ),
                    ],
                    className="custom-tabs",
                ),
            ]
        ),
    ]
)


# Callback pour le graphique "Mean Rented Bikes by Hour"
@callback(Output("hourly-mean-bikes", "figure"), Input("hourly-range-slider", "value"))
def update_hourly_graph(selected_range):
    filtered_df = bike[
        (bike["Hour"] >= selected_range[0]) & (bike["Hour"] <= selected_range[1])
    ]
    mean_hour = filtered_df.groupby("Hour")["Rented_Bike_Count"].mean().reset_index()
    fig_hourly = px.bar(
        mean_hour,
        x="Hour",
        y="Rented_Bike_Count",
        labels={"Rented_Bike_Count": "Mean Rented Bikes"},
        color="Rented_Bike_Count",
        color_continuous_scale="Viridis",
        title="Bike Rental Per Hour",
    )
    return fig_hourly


# Callback pour le graphique "Rented Bike Count by Hour and Season"
@callback(
    Output("seasonal-mean-bikes", "figure"),
    [Input("seasonal-range-slider", "value"), Input("season-checklist", "value")],
)
def update_seasonal_graph(selected_range, selected_seasons):
    # Filtrer la dataframe pour les heures et les saisons sélectionnées
    filtered_df = bike[
        (bike["Hour"] >= selected_range[0])
        & (bike["Hour"] <= selected_range[1])
        & (bike["Seasons"].isin(selected_seasons))
    ]
    bike_grouped = (
        filtered_df.groupby(["Hour", "Seasons"])["Rented_Bike_Count"]
        .mean()
        .reset_index()
    )

    fig_season = px.line(
        bike_grouped,
        x="Hour",
        y="Rented_Bike_Count",
        color="Seasons",
        title="Bike Rental Per Hour Depending on the Season",
    )

    return fig_season


# Callback pour le graphique "Bike Rental Per Hour Depending on the Day"
@callback(Output("daily-mean-bikes", "figure"), Input("daily-range-slider", "value"),Input("day-checklist", "value"))
def update_daily_graph(selected_range, selected_days):
    filtered_df = bike[
        (bike["Hour"] >= selected_range[0]) & (bike["Hour"] <= selected_range[1]) &
        (bike["Day"].isin(selected_days))
    ]
    bike_grouped_by_day = (
        filtered_df.groupby(["Hour", "Day"])["Rented_Bike_Count"].mean().reset_index()
    )
    fig_by_day = px.line(
        bike_grouped_by_day,
        x="Hour",
        y="Rented_Bike_Count",
        color="Day",
        labels={"Rented_Bike_Count": "Mean Rented Bike", "Day": "Day of the Week"},
        title="Bike Rental Per Hour Depending on the Day of the Week",
    )
    return fig_by_day
