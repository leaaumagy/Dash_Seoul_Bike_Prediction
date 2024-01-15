import dash
from dash import html, dcc, dash_table
import plotly.graph_objs as go
import pandas as pd
from datetime import date

# Enregistrez la page "CovidEffect"
dash.register_page(__name__, path="/CovidEffect", order=6)

# Chargez les données à partir de "Predictions.csv"
data = pd.read_csv("Predictions.csv")

# Convertir la colonne "Date" en datetime
data["Date"] = pd.to_datetime(data["Date"])

# Calcul de la valeur quotidienne moyenne pour les colonnes "daily_counts_xgboost" et "daily_bike_count"
daily_average_xgboost = data.groupby(data["Date"].dt.date)[
    "daily_counts_xgboost"
].mean()
daily_average_bike = data.groupby(data["Date"].dt.date)["daily_bike_count"].mean()

# Options de période
period_options = {
    "Overall View": (date(2018, 12, 1), date(2023, 3, 31)),
    "Pre-Covid": (date(2018, 12, 1), date(2020, 3, 15)),
    "First Lockdown": (date(2020, 3, 15), date(2021, 8, 20)),
    "Deconfinement 1": (date(2021, 8, 20), date(2021, 11, 15)),
    "Lockdown 2": (date(2021, 11, 15), date(2022, 2, 15)),
    "Deconfinement 2": (date(2022, 2, 15), date(2022, 6, 10)),
    "End of Restrictions": (date(2022, 6, 10), date(2022, 12, 31)),
}


# Créez une nouvelle page pour "CovidEffect"
layout = html.Div(
    [
        html.H1("Future Predictions : Analyze of Covid Effect", className="divTitle"),
        html.P(
            "This section enables a graphical comparison of the predictions made by our model from December 2018 to March 2023. "
            " Users have the ability to select a predefined period to quantify the impact of COVID-19 on bike rentals."
            " This interactive tool provides a clear visualization of how the pandemic has influenced biking trends over time."
            " By selecting different periods, such as pre-COVID, lockdowns, and phases of reopening, users can gain insights into the fluctuating patterns of bike usage and how these align with the various stages of the pandemic."
            " This analysis is crucial for understanding the long-term effects of COVID-19 on urban mobility and the bike rental industry."
        ),
        html.P("Select the period you want to explore:"),
        # Menu déroulant pour choisir la période
        dcc.Dropdown(
            id="period-dropdown",
            options=[
                {"label": period_name, "value": period_name}
                for period_name in period_options.keys()
            ],
            value="Overall View",  # Période par défaut
            multi=False,
            className="custom-dropdown-style",
        ),
        dcc.Graph(id="covid-graph"),
    ]
)


# Callback pour mettre à jour le graphique en fonction de la période sélectionnée
@dash.callback(
    dash.Output("covid-graph", "figure"), dash.Input("period-dropdown", "value")
)
def update_graph(selected_period):
    start_date, end_date = period_options[selected_period]
    filtered_data_xgboost = daily_average_xgboost[start_date:end_date]
    filtered_data_bike = daily_average_bike[start_date:end_date]

    figure = {
        "data": [
            go.Scatter(
                x=filtered_data_xgboost.index,
                y=filtered_data_xgboost,
                mode="lines",
                name="Predictions",
            ),
            go.Scatter(
                x=filtered_data_bike.index,
                y=filtered_data_bike,
                mode="lines",
                name="Real Data",
            ),
        ],
        "layout": go.Layout(
            title=f"{selected_period} - Predictions vs. Real Data Over Time"
        ),
    }

    return figure
