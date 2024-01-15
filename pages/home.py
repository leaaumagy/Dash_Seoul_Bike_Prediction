import dash
from dash import html

dash.register_page(__name__, path="/", order=1, suppress_callback_exceptions=True)
# page d introduction avec une image qu on charge
layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Seoul Bike Sharing Demand Forecast: Unveiling Temporal and Meteorological Effects"
                )
            ],
            className="divTitle",
        ),
        html.Div(
            [
                html.P(
                    "This dashboard offers an in-depth examination of the interplay between weather conditions and temporal variables on the usage patterns of Seoul’s bike-sharing service. The analysis embarks with exploratory data examination to discern the impact of diverse factors on rental frequencies. Progressing further, a regression model is utilized to pinpoint the most significant determinants of rental demand. The analytical journey culminates with the deployment of an XGBoost model, engineered to forecast future bike rental volumes, thereby facilitating data-driven decision-making and trend prediction.",
                    style={"font-size": "18px"},
                ),
                html.Div(
                    html.Img(
                        src="assets/images/bike.png",
                        style={"width": "60%", "height": "auto"},
                    ),
                    style={"textAlign": "center"},
                ),
                html.P(
                    "Dive into the various sections to uncover a deeper level of detail and gain valuable insights into the data.",
                    style={"font-size": "18px"},
                ),
            ],
            style={"padding": "10px 20px 10px 10px"},
        ),
    ]
)
