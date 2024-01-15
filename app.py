import dash
from dash import Dash, html, dcc, callback, Input, Output

# Création de l'application Dash
app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# Mise en page de l'application
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        # Barre latérale
        html.Div(
            [
                html.H2("Seoul Bike"),
                html.Hr(),
                html.Div(id='sidebar-links'),
            ],
            className="sidebar",
        ),
        html.Div(
            dash.page_container, # Conteneur de la page, où le contenu de chaque page sera affiché
            className="page-content", # Classe CSS pour le contenu de la page
        ),
    ],
    className="container", # Classe CSS pour le conteneur principal de l'application
)

@app.callback(
    Output('sidebar-links', 'children'),
    [Input('url', 'pathname')]
)
def render_sidebar_links(pathname):
    return [
        dcc.Link(
            f"{page['name']} - {page['path']}",
            href=page["relative_path"],
            className='link' + (' active' if pathname == page["relative_path"] else ''),
            style={'display': 'block', 'padding': '5px'}
        )
        for page in dash.page_registry.values()
    ]

# Exécution de l'application en mode débogage
if __name__ == "__main__":
    app.run_server(debug=True)
