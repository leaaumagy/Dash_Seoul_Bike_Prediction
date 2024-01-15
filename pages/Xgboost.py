import dash
from dash import html, dcc, callback, Output, Input, State, dash_table
import pandas as pd
import xgboost as xgb
import plotly.graph_objs as go
import numpy as np
from datetime import datetime

# Enregistrer la page dans le système de pages Dash
dash.register_page(
    __name__, path="/Results", order=5, suppress_callback_exceptions=True
)

# Charger le modèle XGBoost
loaded_model = xgb.Booster(model_file="xgb.model")

# Charger la base de données
bike = pd.read_csv("Dashbike.csv")

# Sélectionner les caractéristiques pour le modèle XGBoost
features = ["Hour", "Temperature_C", "Humidity", "Rainfall_mm", "Solar_Radiation_MJ_m2"]

# Créer une DMatrix pour les prédictions
dtest = xgb.DMatrix(bike[features])

# Effectuer des prédictions à l'aide du modèle chargé
bike["predictions_xgboost"] = loaded_model.predict(dtest)
bike["predictions_xgboost"] = bike["predictions_xgboost"].round(0)

# Assurer que la colonne 'Date' est de type datetime
bike["Date"] = pd.to_datetime(bike["Date"])

# Sélectionner uniquement les colonnes numériques pour le calcul de la moyenne
numeric_columns = bike.select_dtypes(include=["number"])

# Ajouter la colonne 'Date' au DataFrame des colonnes numériques
numeric_columns["Date"] = bike["Date"]

# Calculer la moyenne journalière pour les colonnes numériques
daily_average = numeric_columns.groupby(numeric_columns["Date"].dt.date).mean()

# Initialiser la variable globale pour stocker les requêtes
user_requests = pd.DataFrame(
    columns=[
        "Hour",
        "Temperature",
        "Humidity",
        "Rainfall",
        "Solar Radiation",
        "Predicted Value",
    ]
)

# Layout de la page
layout = html.Div(
    [
        html.H1("Prediction using XGboost Model", className="divTitle"),
        html.P(
            "Thanks to our analyses in the Feature Selection part, we were able to select the most relevant parameters for our XGBoost model."
            "XGBoost, which stands for eXtreme Gradient Boosting, is a sophisticated machine learning algorithm known for its efficiency and accuracy in predictive modeling."
        ),
        html.P(
            " On this page, you can find two different tabs. The first tab is an interactive prediction tool that allows you to select the model values in order to obtain a prediction."
        ),
        # création d'onglet
        dcc.Tabs(
            [
                dcc.Tab(
                    label="Prediction Tool",
                    children=[
                        html.Div(
                            [
                                html.P(
                                    "Here, you can select various variables to obtain predictions on the number of bicycles rented. "
                                    "This tool is extremely efficient and valuable for decision-making purposes. By inputting different environmental and temporal factors, such as weather conditions,"
                                    " time of the day, and other relevant variables, you can accurately forecast bike rental demand. This predictive capability is particularly useful for optimizing resource allocation, "
                                    "planning maintenance schedules, and enhancing customer satisfaction by ensuring adequate availability of bicycles. "
                                    "It serves as a crucial aid in strategic planning and operational efficiency in the bike rental business."
                                ),
                                html.P(
                                    " Important note: The Solar Radiation variable corresponds to the level of sunlight, equal to 0 it means it's night, and 10 corresponds to a heatwave day with a completely clear sky.",
                                    style={"fontWeight": "bold"},
                                ),
                                html.P("Select the different variables:"),
                                html.Div(
                                    [
                                        html.Label("Hour"),
                                        dcc.Slider(
                                            id="input-hour",
                                            min=0,
                                            max=23,
                                            value=12,
                                            marks={i: str(i) for i in range(0, 24)},
                                            step=1,
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Label("Temperature (C)"),
                                        dcc.Slider(
                                            id="input-temperature",
                                            min=-10,
                                            max=40,
                                            value=12,
                                            marks={i: str(i) for i in range(-10, 41)},
                                            step=1,
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Label("Humidity"),
                                        dcc.Slider(
                                            id="input-humidity",
                                            min=0,
                                            max=100,
                                            value=50,
                                            marks={i: str(i) for i in range(0, 101, 5)},
                                            step=1,
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Label("Rainfall"),
                                        dcc.Slider(
                                            id="input-rainfall",
                                            min=0,
                                            max=70,
                                            value=0,
                                            marks={i: str(i) for i in range(0, 71, 2)},
                                            step=1,
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Label("Solar Radiation (MJ/m2)"),
                                        dcc.Slider(
                                            id="input-solar",
                                            min=0,
                                            max=10,
                                            value=0,
                                            marks={i: str(i) for i in range(0, 11)},
                                            step=1,
                                        ),
                                    ]
                                ),
                                html.Button(
                                    "Predict",
                                    id="predict-button",
                                    className="predict-button",
                                ),
                                html.H2(
                                    "Prediction Result:", className="prediction-title"
                                ),
                                html.Div(
                                    id="prediction-result",
                                    className="prediction-result",
                                ),
                                html.H2("Predictions Table:"),
                                html.Div(id="table-container"),
                            ]
                        ),
                    ],
                    className="custom-tabs",
                ),
                dcc.Tab(
                    label="Real Data VS Xgboost",
                    children=[
                        html.Div(
                            [
                                html.P(
                                    "In this section, you can view the actual measured data alongside the predictions made by our model."
                                    " It s evident that our model is highly effective and capable of predicting the number of bicycles rented with considerable accuracy."
                                    " The close alignment between the predicted and actual data underscores the reliability and precision of our model."
                                    " This enables us to make well-informed decisions and effectively plan for future demands. "
                                    " The model s accuracy is a testament to its sophisticated design, which considers various influencing factors to forecast bike rental trends accurately."
                                    " Such precision is invaluable for businesses seeking to optimize operations and improve customer service."
                                ),
                                html.P(
                                    "This feature allows you to choose a specific period for analysis. By specifying the start and end dates, you can focus on the data relevant to that timeframe."
                                    " This functionality is particularly useful for observing trends, patterns, and changes in bike rental demand over different periods."
                                ),
                                html.Div("Select the date range:"),
                                dcc.DatePickerRange(
                                    id="date-picker-range",
                                    start_date=daily_average.index.min(),
                                    end_date=daily_average.index.max(),
                                    display_format="YYYY-MM-DD",
                                    style={
                                        "marginBottom": "20px",
                                        "border": "1px solid #ccc",  # Bordure du sélecteur
                                        "padding": "5px",  # Padding interne
                                        "borderRadius": "5px",  # Rayon des coins arrondis
                                        "color": "#333",  # Couleur du texte
                                        "backgroundColor": "#333333",  # Couleur de fond
                                    },
                                ),
                                html.Div(id="output-container-date-picker-range"),
                                dcc.Graph(id="prediction-graph"),
                            ]
                        )
                    ],
                    className="custom-tabs",
                ),
            ]
        ),
    ]
)


# Callbacks pour la page
@callback(
    [Output("prediction-result", "children"), Output("table-container", "children")],
    [Input("predict-button", "n_clicks")],
    [
        State("input-hour", "value"),
        State("input-temperature", "value"),
        State("input-humidity", "value"),
        State("input-rainfall", "value"),
        State("input-solar", "value"),
    ],
)
def update_prediction(n_clicks, hour, temperature, humidity, rainfall, solar_radiation):
    if n_clicks is None:
        return "Waiting for prediction...", None

    # Déterminer quel élément a déclenché le rappel
    trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if trigger_id != "predict-button":
        return dash.no_update, dash.no_update

    # Préparer les données pour la prédiction
    data = np.array([[hour, temperature, humidity, rainfall, solar_radiation]])
    dmatrix = xgb.DMatrix(
        data,
        feature_names=[
            "Hour",
            "Temperature_C",
            "Humidity",
            "Rainfall_mm",
            "Solar_Radiation_MJ_m2",
        ],
    )

    # Effectuer la prédiction
    prediction = loaded_model.predict(dmatrix)
    predicted_value = round(prediction[0])

    # Créer une nouvelle ligne sous forme de DataFrame
    new_row = pd.DataFrame(
        {
            "Hour": [hour],
            "Temperature": [temperature],
            "Humidity": [humidity],
            "Rainfall": [rainfall],
            "Solar Radiation": [solar_radiation],
            "Predicted Value": [predicted_value],
        }
    )

    global user_requests  # Déclaration de la variable globale

    # On s'assure que new_row et user_requests ont les mêmes colonnes
    new_row = new_row.reindex(columns=user_requests.columns)

    # On filtre les colonnes vides ou toutes NA dans new_row
    new_row = new_row.dropna(how="all", axis=1)

    # On concaténe uniquement si new_row n'est pas vide
    if not new_row.empty:
        user_requests = pd.concat([user_requests, new_row], ignore_index=True)

    # On crée une table Dash pour afficher les requêtes
    table = dash_table.DataTable(
        data=user_requests.to_dict("records"),
        columns=[{"name": i, "id": i} for i in user_requests.columns],
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold",
            "textAlign": "center",
            "color": "black",
            "fontSize": "16px",
        },
        style_cell={
            "padding": "10px",
            "border": "1px solid lightgrey",
            "textAlign": "center",
            "color": "black",
            "fontSize": "14px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"},
            {"if": {"row_index": "even"}, "backgroundColor": "rgb(220, 220, 220)"},
        ],
        style_cell_conditional=[
            {"if": {"column_id": "Variable"}, "fontWeight": "bold"}
        ],
        style_as_list_view=True,
    )

    return f"Predicted Value: {predicted_value}", table


@callback(
    Output("prediction-graph", "figure"),
    [Input("date-picker-range", "start_date"), Input("date-picker-range", "end_date")],
)
def update_graph(start_date, end_date):
    # On converti les dates de chaîne en datetime.date
    start_date = (
        datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    )
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    # On filtre les données en fonction de la plage de dates
    filtered_data = daily_average[
        (daily_average.index >= start_date) & (daily_average.index <= end_date)
    ]

    # On crée le graph avec les données filtrées
    figure = {
        "data": [
            go.Scatter(
                x=filtered_data.index,
                y=filtered_data["Rented_Bike_Count"],
                mode="lines",
                name="Daily Average Actual",
            ),
            go.Scatter(
                x=filtered_data.index,
                y=filtered_data["predictions_xgboost"],
                mode="lines",
                name="Daily Average Predicted",
            ),
        ],
        "layout": go.Layout(
            title="Daily Average Actual vs. Predicted Bike Rentals",
            xaxis_title="Date",
            yaxis_title="Bike Rentals",
        ),
    }
    return figure
