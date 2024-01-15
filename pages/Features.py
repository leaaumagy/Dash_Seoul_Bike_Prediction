from dash import html, dcc, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
import dash


bike = pd.read_csv('Dashbike.csv')

dash.register_page(__name__, path='/Selection',order=4,suppress_callback_exceptions=True)

# Création du modèle OLS
model_formula = "Rented_Bike_Count ~ Temperature_C + Hour + Humidity + Wind_speed_m_s + Rainfall_mm + Snowfall_cm + Solar_Radiation_MJ_m2 + Visibility_10m + Dew_point_temperature_C"
model = ols(model_formula, data=bike).fit()


# Exécution du test ANOVA
anova_results = sm.stats.anova_lm(model, typ=2)

# Convertir les résultats ANOVA en DataFrame pour l'affichage dans Dash DataTable
anova_table = pd.DataFrame(anova_results)

# Nommer la première colonne "Variable"
anova_table = anova_table.rename_axis('Variable').reset_index()


# Sélection des colonnes numériques pour la matrice de corrélation
numeric_cols = bike.select_dtypes(include=['number']).columns

layout = html.Div([
    html.Div([html.H1('Features Selection')], className="divTitle"),
    html.P("Welcome to the Feature Selection section. In this crucial step of our analysis, we focus on identifying the most impactful variables for our regression model."
           " Through various statistical methods, including correlation matrices and ANOVA, we can discern which features significantly influence bike rental patterns. "
           "This process not only enhances the accuracy of our model but also provides valuable insights into the factors driving bike rentals."),
    # Affichage du résumé du modèle OLS
    html.Div([html.H2("OLS Model Summary and Anova Test")], className="divH", style={"marginTop":"30px"}),
    html.P("Below is the summary of our OLS model. This comprehensive summary presents key statistics and coefficients that help in understanding the influence of each variable in our model."
           " The summary is crucial for interpreting the model's effectiveness and the significance of each predictor in estimating bike rental counts."),
    html.Div([html.Pre(model.summary().as_text())],
             style={"fontFamily": "monospace", "textAlign": "center", "marginTop": "30px", "marginBottom": "30px"}), # Utilisez html.Pre pour un formatage de texte préformaté

    # Affichage de la table ANOVA
    html.Div([html.H2("ANOVA Results"),
        html.P("This part of the analysis presents the ANOVA (Analysis of Variance) results. ANOVA helps us understand if there are any statistically significant differences between the group means in our model."
               " It's a vital step in assessing the overall significance of the model and the variables involved."),
        html.Div(
            dash_table.DataTable(
                id='table-anova',
                columns=[{"name": col, "id": col} for col in anova_table.columns],
                data=anova_table.reset_index().to_dict('records'),
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'color': 'black',
                    'fontSize': '16px'
                },
                style_cell={
                    'padding': '10px',
                    'border': '1px solid lightgrey',
                    'textAlign': 'center',
                    'color': 'black',
                    'fontSize': '14px'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                    {'if': {'row_index': 'even'}, 'backgroundColor': 'rgb(220, 220, 220)'}
                ],
                style_cell_conditional=[
                    {'if': {'column_id': 'Variable'}, 'fontWeight': 'bold'}
                ],
                style_as_list_view=True,
            ),
            className="table-container"
        ),
    ],
    className="main-container"
),
    html.Div([html.H2("Correlation Matrix")], className="divH", style={"marginTop":"50px"}),
    html.P('In this section, you can explore the correlation matrix. A correlation matrix is a table showing correlation coefficients between variables. '
           'Each cell in the table shows the correlation between two variables. This visual representation helps in identifying patterns and potential relationships between different variables involved in our study.'
           , style={"font-size": "18px"}),
    html.P(' You can select variables of your interest to see how they correlate with each other.'),
    dcc.Dropdown(
        id='variable-selector',
        options=[{'label': col, 'value': col} for col in numeric_cols],
        value=numeric_cols.tolist(),
        multi=True,
        style={"width": "100%", "padding": "10px 20px 10px 10px"}
    ),

    dcc.Graph(id='correlation-matrix'),

])

# Callback pour la mise à jour de la heatmap de corrélation
@callback(
    Output('correlation-matrix', 'figure'),
    [Input('variable-selector', 'value')]
)
def update_correlation_matrix(selected_variables):
    # Filtrer les données pour inclure seulement les variables sélectionnées
    filtered_data = bike[selected_variables]
    corr_matrix = filtered_data.corr()

    # Créer la heatmap avec Plotly
    fig = px.imshow(
        corr_matrix,
        labels=dict(color="Correlation"),
        x=selected_variables,
        y=selected_variables,
        color_continuous_scale='Greens',
        aspect='auto'  # Ajustez 'auto' si vous voulez des cellules carrées
    )

    fig.update_layout(
        title='Correlation Matrix',
        margin={'l': 10, 'b': 20, 't': 50, 'r': 10},
        height=600
    )
    return fig
