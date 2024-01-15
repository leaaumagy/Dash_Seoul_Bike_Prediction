import style
from dash import html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash

# Initialisation de l'app Dash
dash.register_page(__name__, path='/Overall_View',order=2,suppress_callback_exceptions=True)

# Lecture des données
bike = pd.read_csv("Dashbike.csv")
bike["Date"] = pd.to_datetime(bike["Date"], format="%Y-%m-%d")
bike['Day'] = bike['Date'].dt.day_name()  # Ajout de la colonne 'Day'

# Calculs pour le premier graphique
bike_daily_mean = (
    bike.groupby(bike["Date"].dt.date)["Rented_Bike_Count"].mean().reset_index()
)

# Calculs pour le second graphique
mean_week = bike.groupby("Day")["Rented_Bike_Count"].mean()
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
mean_week = mean_week.reindex(ordered_days)

# Calculs pour le troisième graphique (assurez-vous que cela soit fait en amont)
total_bikes_by_season = bike.groupby('Seasons')['Rented_Bike_Count'].sum()


# Définition du layout de la page
layout = html.Div(
    [
        # Section pour le premier graphique
        html.Div([html.H1('Overview of Bike Rental Trends')], className="divTitle"),
        html.Div([
        html.P(
            "In this section, we offer various types of general visualizations, encompassing overall trends, variations in bike rentals based on different days of the week, and seasonal fluctuations. You are invited to explore each of these interactive charts and adjust their various parameters to suit your analysis needs."
            " This interactive capability allows for a deeper understanding of the data, enabling you to identify specific patterns, compare different time periods, and observe how external factors like weather and holidays impact bike rental trends."
            " By manipulating these parameters, you can gain valuable insights into the dynamics of urban mobility and its correlations with temporal and environmental factors.",
            style={"marginBottom":"40px"}
        ),
        html.Div([html.H2("Daily average of bike rentals")], className="divH", style={"marginTop":"30px"}),
        html.P("This visualization presents the daily average of bike rentals in the city. You can utilize the date range selector to customize the view according to your specific requirements.", style={"font-size": "18px", "marginBottom":"20px", "marginTop":"20px"}),
        html.Div(
            [
                html.Label(
                    "Select a date range:",
                    style={"marginTop": "20px", "display": "block", "font-size": "18px"},
                ),
                html.Div([
                dcc.DatePickerRange(
                    id="date-range",
                    min_date_allowed=bike_daily_mean["Date"].min(),
                    max_date_allowed=bike_daily_mean["Date"].max(),
                    start_date=bike_daily_mean["Date"].min(),
                    end_date=bike_daily_mean["Date"].max(),
                    style={
                        "marginBottom": "20px",
                        "border": "1px solid #ccc",  # Bordure du sélecteur
                        "padding": "5px",  # Padding interne
                        "borderRadius": "5px",  # Rayon des coins arrondis
                        "color": "#333",  # Couleur du texte
                        "backgroundColor": "#333333"  # Couleur de fond
                    },
                ),
                dcc.Graph(id="bike-graph"),
                ], style={"textAlign": "center"})
            ],
            className="sub-container",
        ),
        # Section pour le second graphique
        html.Div(
            [
                html.Div([html.H2("Weekly Distribution of Rentals")], className="divH", style={"marginTop":"30px"}),
                html.P("Choose the days to be displayed on the chart. This option allows you to customize the data visualization to focus on specific days of the week, enabling a more detailed analysis of rental patterns.", style={"font-size": "18px", "marginBottom":"20px", "marginTop":"20px"}),
                html.Div(
                    dcc.Checklist(
                        id='day-checklist',
                        options=[{'label': day, 'value': day} for day in ordered_days],
                        value=ordered_days,
                        inline=True
                    ),
                    className='checklist-container'
                ),
                dcc.Graph(id="week-graph"),
            ],
            className="sub-container",
        ),
        html.Div([
                html.Div([html.H2("Total Number of Rented Bikes by Season")], className="divH", style={"marginTop":"30px"}),
                html.P("Choose the seasons to be displayed on the chart. This option allows you to customize the data visualization to focus on specific seasons of the year, enabling a more detailed analysis of rental patterns.", style={"font-size": "18px", "marginBottom":"20px", "marginTop":"20px"}),
                dcc.Dropdown(
                    id='season-dropdown',
                    options=[{'label': season, 'value': season} for season in total_bikes_by_season.index],
                    value=[season for season in total_bikes_by_season.index],
                    # Sélection par défaut de toutes les saisons
                    multi=True,  # Permettre la sélection multiple
                ),
                dcc.Graph(id='season-graph')
            ])
        ],

        style={"padding": "10px 20px 10px 10px"})
    ],
)

# Callback pour le premier graphique
@callback(
    Output("bike-graph", "figure"),
    [Input("date-range", "start_date"), Input("date-range", "end_date")]
)

def update_graph(start_date, end_date):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    filtered_df = bike_daily_mean[
        (bike_daily_mean["Date"] >= start_date) & (bike_daily_mean["Date"] <= end_date)
    ]
    fig = px.line(
        filtered_df,
        x="Date",
        y="Rented_Bike_Count",
        title="Daily Average of Bikes Rented",
        line_shape="linear",
    )
    fig.update_traces(line_color="green")
    return fig

# Callback pour le second graphique
@callback(
    Output("week-graph", "figure"),
    [Input("day-checklist", "value")]
)
def update_week_graph(selected_days):
    # Filtrer les données pour inclure seulement les jours sélectionnés
    filtered_data = bike[bike['Day'].isin(selected_days)]
    mean_week_selected = filtered_data.groupby("Day")["Rented_Bike_Count"].mean().reindex(selected_days)

    # Créer le graphique à barres avec Plotly
    fig = px.bar(
        mean_week_selected,
        x=mean_week_selected.index,
        y="Rented_Bike_Count",
        title="Mean Rented Bikes by Selected Day",
        labels={"Rented_Bike_Count": "Mean Rented Bikes", "index": "Day"}
    )


    # Mise à jour de la couleur des barres
    fig.update_traces(marker_color='#66FF66')  # On définit un Vert clair

    # Mise à jour de la disposition du graphique
    fig.update_layout(
        xaxis=dict(title='Day'),
        yaxis=dict(title='Mean Rented Bikes', range=[0, max(mean_week_selected) * 1.2])
    )

    return fig

@callback(
    Output('season-graph', 'figure'),
    [Input('season-dropdown', 'value')]
)
def update_season_graph(selected_seasons):
    filtered_data = total_bikes_by_season[total_bikes_by_season.index.isin(selected_seasons)]
    fig = px.bar(
        filtered_data,
        x=filtered_data.index,
        y='Rented_Bike_Count',
        title="Total Number of Rented Bikes by Season",
        labels={"Rented_Bike_Count": "Total Rented Bikes", "index": "Season"}
    )
    fig.update_layout(xaxis=dict(title='Season'), yaxis=dict(title='Total Rented Bikes'))
    fig.update_traces(marker_color='#006400') # On définit un vert foncé
    return fig