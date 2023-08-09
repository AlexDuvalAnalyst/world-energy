import dash
from dash import Input, Output, dcc, html, State, dash_table
import dash_bootstrap_components as dbc
import sqlite3 as sq
import plotly.express as px
import pandas as pd

# pour les app on peut soit utiliser un fichier css externe ou alors utiliser la bibliotheque dash_bootstrap_components
# qui contient des composants bootstrap et des themes bootstrap predefinis

# initialisation des variables et autres elements dont on aura besoin

# on va creer la liste des pays a partir de la base de donnees
conn = sq.connect('energy.db')
c = conn.cursor()
c.execute("SELECT country FROM energy")
country_list = c.fetchall()
country_list = [i[0] for i in country_list]
country_list = list(set(country_list)) # on veut garder que les pays uniques et la fonction set permet de cree un set qui ne contient que des elements uniques 

# recuperation des donnees pour le tableau initial

df = pd.DataFrame(c.execute("SELECT year, primary_energy_consumption,biofuel_consumption, coal_consumption, fossil_fuel_consumption, gas_consumption, hydro_consumption, nuclear_consumption, oil_consumption, solar_consumption, wind_consumption FROM energy where country = 'France'").fetchall())
df.columns = ['Year','PEC','Biofuel','Coal','Fossil fuel','Gas','Hydro','Nuclear','Oil','Solar','Wind']
df.dropna(inplace=True)

df2 = pd.DataFrame(c.execute("SELECT year, electricity_generation,biofuel_electricity, coal_electricity, fossil_electricity, gas_electricity, hydro_electricity, nuclear_electricity, oil_electricity, solar_electricity, wind_electricity FROM energy where country = 'France'").fetchall())
df2.columns = ['Year','Electricity generation','Biofuel','Coal','Fossil fuel','Gas','Hydro','Nuclear','Oil','Solar','Wind']
df2.dropna(inplace=True)

conn.close()

# recuperationd des fichies css externes
external_stylesheets = [dbc.themes.SOLAR,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/font-awesome.min.css'
                       ]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) # on ajoute le theme boostrap SOLAR

server = app.server  # expose le serveur pour Gunicorn

# se rendre sur la page du theme pour voir les differentes options de theme et les classes css disponibles https://bootswatch.com/solar/

# les elements html de base vont avoir des classes css bootstrap predefinis mais on peut les modifier en ajoutant style={""}
# children est un argument spécial qui peut être utilisé pour passer des enfants de manière plus lisible que le premier argument 
# (html.H1(children='Hello Dash') est équivalent à html.H1('Hello Dash'))

# pour le layout row et column voir la doc mais en gros il faut un container qui contient des row qui contiennent des col
# l'avantage de boostrap c'est qu'il gère le redimensionnement automatiquement, donc pas besoin de toucher à la taille des row et col


# le layout que l'on veut c'est une sidebar a gauche et le contenu a droitem donc on va creer 2 divs, une pour la sidebar et une pour le contenu
# le div de contenu sera rempli avec les rows et col boostrap

# creation du style de la sidebar, pour quelle prenne tout le temps la meme taille et la meme position
SIDEBAR_STYLE = {
    "height": "100vh",
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "17rem",
    "padding": "2rem 1rem",
    "background-color": "#2b7570",
    }

# creation du style pour le div de contenu, juste a droite de la sidebar
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# creation de la sidebar, qui est enfait un div qui va contenir notamment un navbar boostrap
# voir doc offCanvas si on veut une sidebar qui se cache et se montre quand on clique sur un bouton
# ca peut aussi marcher pour d autres elements que la sidebar
sidebar = html.Div(
    [
        html.H1("World energy", className="display-6",style = {"color":"white"}), # display-4 est une classe boostrap qui permet de mettre le texte en plus gros par rapport a un h1 normal
        html.Hr(style = {"color":"white","height":"10px","border-width":"3px"}), # hr est une classe boostrap qui permet de mettre une ligne de separation horizontale
        html.P(
            "Energy consumtion and production around the world !", className="lead",style = {"color":"#c8dedc"}  # lead est une classe boostrap qui permet de mettre le texte en plus gros par rapport a un p normal
        ),
        html.I(className="fa-solid fa-question"),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink([html.I(className="fa-solid fa-question"),"Global energy analysis"], href="/", active="exact",style = {"font-size":"1.3rem","color":"white"})), # pour changer la taille on peut utiliser clas
                dbc.NavItem(html.Hr(style = {"color":"white","border-width":"1px","width":"50%", "margin": "auto","margin-top":"7px","margin-bottom":"7px"})),
                dbc.NavItem(dbc.NavLink("Country data", href="/country-data", active="exact",style = {"font-size":"1.3rem","color":"white"})),
                dbc.NavItem(html.Hr(style = {"color":"white","border-width":"1px","width":"50%", "margin": "auto","margin-top":"7px","margin-bottom":"7px"}))
            ],
            vertical=True,
            pills=True,
        ),
        dbc.Offcanvas(
            html.Div([
                html.P(
                    "These data come from the Our World in Data website. It has been collected, aggregated, and documented by Hannah Ritchie, Pablo Rosado, Edouard Mathieu, Max Roser" 
                ),
                html.A(href = "https://github.com/owid/energy-data", target="_blank", children = "Visit this github page for more informations"),
            ]),
            id="openmoreinfo",
            scrollable=True,
            title="More info",
            is_open=False,
            style = {"width":"100%", "height":"50%","opacity":"0.7","margin-top":"15%","color":"white","font-size":"2rem"}
        ),
        html.Div([
            html.A(
                html.Img(src='/assets/github.png', style={'height':'40px'}),
                href='https://github.com/AlexDuvalAnalyst',target='_blank'
            ),
            dbc.Button("+ infos", id="open-more_info", n_clicks=0, 
                   style = {"font-size":"1.6rem","border-color":"#073642","background-color":"#073642","margin-left":"1rem","margin-right":"1rem"}), 
            html.A(
                html.Img(src='/assets/linkedin.png', style={'height':'55px'}),
                href='https://www.linkedin.com/in/alexandre-duval-6021711ba/',target='_blank'
            )
        ],style = {"position":"absolute","bottom":"3vh","left":"1.5rem"})
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# gestion du rendu des pages en fonction de l'url
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])

# pour mettre du code python pour creer des variables ou autre, il faut le faire dans une fonction
def render_page_content(pathname):
    
    if pathname == "/":
        # premiere page, c'est un div qui contient des row et des col boostrap
        return html.Div([
            dbc.InputGroup([
                 dcc.Dropdown(
                    id='my-dropdown',
                    options=[{'label': i, 'value': i} for i in country_list],
                    searchable=True,
                    value='France',
                    placeholder="Choose a country...",
                    style={"width":"100%","border-radius":"8px"},
                    className='my-dropdown-class' # besoin de css externe pour les elements dcc
                )
            ],style = {"width":"40%","min-width":"250px"}),
            # la taille de la row est automatiquement ajustee par boostrap en fonction de la taille de son contenu
            dbc.Row([
               dbc.Col(html.Div([
                            html.Div("Total energy consumption", className="card-header",style = {"color":"white"}),
                            html.Div(
                                dcc.Graph(id='graph1',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"calc(100% - 40px)","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=12, style = {"height":"410px"}
                        )
                    ], style = {"margin-top":"2rem"}),
            html.Div(
                dbc.Row([
               # md permet de dire que la col prendra 4/12 de la largeur de l'ecran pour les ecrans de taille moyenne
               # xs permet de dire que la col prendra 12/12 de la largeur de l'ecran pour les ecrans de petite taille
               # avec boostrap la largeur max attribuable a une col est 12, 3 colonnes avec md=4 va les repartir uniformement sur la ligne'
               # avec un padding par defaut de 15px entre les col
                    dbc.Col(html.Div([
                                html.Div(dcc.Graph(id='graph2',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),
                                        className="card-body text-white",style = {"height":"100%","background-color":"#2b7570","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}),
                                    ],className="card",style = {"height":"100%"}),
                        xs=12, md=4, style = {"height":"410px","margin-top":"1.5rem"}),
                    dbc.Col(html.Div([
                                html.Div(dcc.Graph(id='graph3',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),
                                        className="card-body text-white",style = {"height":"100%","background-color":"#2b7570","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}),
                                    ],className="card",style = {"height":"100%"}),
                        xs=12, md=4, style = {"height":"410px","margin-top":"1.5rem"}),
                    dbc.Col(html.Div([
                                html.Div(
                                    dcc.Graph(id='graph4',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"100%","background-color":"#2b7570","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                ),
                                    ],className="card",style = {"height":"100%"}),
                        xs=12, md=4, style = {"height":"410px","margin-top":"1.5rem"}),
                ], className='justify-content-center',style = {'min-width': '1600px'}), # justify-content-center permet de centrer les col sur la ligne peut importe leur taille et emplacement
                 style = {'overflowX': 'auto'}
            ),
            html.Div(
                dbc.Row([
                    dbc.Col(html.Div([
                                html.Div("Yearly electricity production (terawatt-hours)", className="card-header",style = {"color":"white"}),
                                html.Div(
                                    html.Div([
                                        dash_table.DataTable(
                                            id='table1',
                                            columns=[{"name": i, "id": i} for i in df2.columns],
                                            data=df2.to_dict('records'),
                                            style_cell={'textAlign': 'left', 'padding': '5px', 'background-color': 'rgba(0, 0, 0, 0)','fontWeight': 'bold'},
                                            style_header={'background-color': 'rgba(45, 104, 252,0.3)','fontWeight': 'bold'},
                                        )
                                    ], style = {"overflowY":"auto","height":"100%"}),
                                    className="card-body text-white",style = {"height":"calc(100% - 40px)","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                ),
                                    ],className="card",style = {"height":"100%"}),
                        xs=12, md=6, style = {"height":"700px","margin-top":"1.5rem"}),
                    dbc.Col(html.Div([
                                html.Div("Yearly energy consumption (terawatt-hours)", className="card-header",style = {"color":"white"}),
                                html.Div(
                                    html.Div([
                                        dash_table.DataTable(
                                            id='table2',
                                            columns=[{"name": i, "id": i} for i in df.columns],
                                            data=df.to_dict('records'),
                                            style_cell={'textAlign': 'left', 'padding': '5px', 'background-color': 'rgba(0, 0, 0, 0)','fontWeight': 'bold'},
                                            style_header={'background-color': 'rgba(45, 104, 252,0.3)','fontWeight': 'bold'},
                                        )
                                    ], style = {"overflowY":"auto","height":"100%"}),
                                    className="card-body text-white",style = {"height":"calc(100% - 40px)","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                ),
                                    ],className="card",style = {"height":"100%"}),
                        xs=12, md=6, style = {"height":"700px","margin-top":"1.5rem"}),
                    ], className='justify-content-center',style = {'min-width': '1200px'}),
                    style = {'overflowX': 'auto'}
            )
                ])

    elif pathname == "/country-data":
        return html.P([
            dbc.InputGroup([
                 dcc.Dropdown(
                    id='my-dropdown2',
                    options=[{'label': i, 'value': i} for i in country_list],
                    searchable=True,
                    value='France',
                    placeholder="Choose a country...",
                    style={"width":"100%","border-radius":"8px"},
                    className='my-dropdown-class' # besoin de css externe pour les elements dcc
                )
            ],style = {"width":"40%","min-width":"250px"}),
             dbc.Row([
               dbc.Col(html.Div([
                            html.Div("Population evolution", className="card-header",style = {"color":"white"}),
                            html.Div(
                                dcc.Graph(id='graph6',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"calc(100% - 40px)","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=8, style = {"height":"410px"}
                        ),
                dbc.Col(html.Div([
                            html.Div(
                                dcc.Graph(id='graph7',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"100%","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=4, style = {"height":"410px"}
                        )
                    ], style = {"margin-top":"2rem"}),
            dbc.Row([
                dbc.Col(html.Div([
                            html.Div(
                                dcc.Graph(id='graph8',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"100%","background-color":"#473140","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=4, style = {"height":"410px"}
                        ),
                dbc.Col(html.Div([
                            html.Div("GDP evolution", className="card-header",style = {"color":"white"}),
                            html.Div(
                                dcc.Graph(id='graph9',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"calc(100% - 40px)","background-color":"#473140","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=8, style = {"height":"410px"}
                        ),
                    ], style = {"margin-top":"2rem"}),
            dbc.Row([
               dbc.Col(html.Div([
                            html.Div("Greenhouse gas emissions evolution", className="card-header",style = {"color":"white"}),
                            html.Div(
                                dcc.Graph(id='graph10',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"calc(100% - 40px)","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=8, style = {"height":"410px"}
                        ),
                dbc.Col(html.Div([
                            html.Div(
                                dcc.Graph(id='graph11',config={'responsive': True},style={"width": "100%", "height": "100%",'display': 'none'}),className="card-body text-white", style={"height":"100%","background-color":"#333147","border-radius":"7px","box-shadow": "rgba(99, 99, 99, 0.6) 0px 1px 4px 0px"}
                                )
                            ],className="card",style = {"height":"100%"}), xs=12, md=4, style = {"height":"410px"}
                        )
                    ], style = {"margin-top":"2rem"}),
        ])
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


# gestion de l'apparission de la sidebar quand on clique sur le bouton
@app.callback(
    Output("openmoreinfo", "is_open"),
    Input("open-more_info", "n_clicks"),
    [State("openmoreinfo", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

# gestion du contenu de la page 1
@app.callback(
    [Output('table1', 'data'),
     Output('table2', 'data'),
     Output('graph1', 'figure'),
     Output('graph1', 'style'),
     Output('graph2', 'figure'),
     Output('graph2', 'style'),
     Output('graph4', 'figure'),
     Output('graph4', 'style'),
     Output('graph3', 'figure'),
     Output('graph3', 'style'),],
    [Input('my-dropdown', 'value')]
)
def update_output(selected_country):
    conn = sq.connect('energy.db')
    c = conn.cursor()
    # recuperation des donnees pour le tableau initial

    # recuperations des donnees pour les tables
    df = pd.DataFrame(c.execute("SELECT year, primary_energy_consumption,biofuel_consumption, coal_consumption, fossil_fuel_consumption, gas_consumption, hydro_consumption, nuclear_consumption, oil_consumption, solar_consumption, wind_consumption FROM energy where country = '{}'".format(selected_country)).fetchall())
    df.columns = ['Year','PEC','Biofuel','Coal','Fossil fuel','Gas','Hydro','Nuclear','Oil','Solar','Wind']
    dffig1 = df[['Year','PEC']].dropna()
    df.dropna(inplace=True)

    df2 = pd.DataFrame(c.execute("SELECT year, electricity_generation,biofuel_electricity, coal_electricity, fossil_electricity, gas_electricity, hydro_electricity, nuclear_electricity, oil_electricity, solar_electricity, wind_electricity FROM energy where country = '{}'".format(selected_country)).fetchall())
    df2.columns = ['Year','Electricity generation','Biofuel','Coal','Fossil fuel','Gas','Hydro','Nuclear','Oil','Solar','Wind']
    dffig4 = df2[['Year','Electricity generation']].dropna()
    df2.dropna(inplace=True)

    # mise a jour du graphique 1
    figure = px.area(dffig1, x = 'Year', y = 'PEC',title="Primary energy consumtion (terawatt-hours) in {}".format(selected_country))
    
    # setting de la ligne
    figure.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#d117a6', width=4))
    # Setting du graph
    figure.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=35, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title=None),
    )

    # mise a jour du graphique 2
    df4 = pd.DataFrame(c.execute("SELECT sum(biofuel_consumption), sum(coal_consumption), sum(fossil_fuel_consumption), sum(gas_consumption), sum(hydro_consumption), sum(nuclear_consumption), sum(oil_consumption), sum(solar_consumption), sum(wind_consumption) FROM energy WHERE country = '{}' group by country".format(selected_country)).fetchall())
    df4.columns = ['Biofuel','Coal','Fossil fuel','Gas','Hydro','Nuclear','Oil','Solar','Wind']
    # organiser en ligne
    df4 = df4.melt(var_name='Type', value_name='Total')
    # ordonner par amount
    df4 = df4.sort_values(by='Total', ascending=False)
    barplot = px.bar(df4, x='Type', y='Total',title="Total energy consumption by category <br>(terawatt-hours)")
    barplot.update_traces(
        marker_line_color='rgba(51, 49, 71, 1)',  # Définir la couleur du contour
        marker_line_width=4,  # Définir l'épaisseur du contour
        marker_color='rgba(45, 104, 252, 0.2)'  # Définir la couleur de remplissage en transparent
    )
    barplot.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'showlegend': False,
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(241, 240, 250, 0.9)",
        font_size = 14,
        yaxis=dict(title=None,gridcolor='rgba(51, 49, 71, 0.2)'),
        xaxis=dict(gridcolor='rgba(51, 49, 71, 0.2)',title=None,tickangle=45),
        title={
        'font': dict(
            size=18
        )
        }
    )
   
    # pour le graphique 4 faire comme le 1 mais avec la production d'electricite
    # mise a jour du graphique 4
    figure4 = px.area(dffig4, x = 'Year', y = 'Electricity generation',title="Electricity generation (terawatt-hours)")
    
    # setting de la ligne
    figure4.update_traces(fillcolor='rgba(30, 36, 201,0.1)',line=dict(color='#00ffbf', width=4))
    # Setting du graph
    figure4.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=45, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(title=None,gridcolor='rgba(51, 49, 71, 0.2)'),
        xaxis=dict(gridcolor='rgba(51, 49, 71, 0.2)',title=None),
        title={
            'font': dict(
                        size=18
                    )
        }
    )

    # Créez le graphique avec les données filtrées
    # pour le graphique 3 faire comme le 2 mais avec la production d'electricite en categorie, peut etre faire un pie chart plutot qu'un barplot

    # creation de la figure 3
    df5 = pd.DataFrame(c.execute("SELECT sum(biofuel_electricity), sum(coal_electricity), sum(fossil_electricity), sum(gas_electricity), sum(hydro_electricity), sum(nuclear_electricity), sum(oil_electricity), sum(solar_electricity), sum(wind_electricity) FROM energy WHERE country = '{}' group by country".format(selected_country)).fetchall())
    df5.columns = ['Biofuel','Coal','Fossil fuel','Gas','Hydro','Nuclear','Oil','Solar','Wind']
    # organiser en ligne
    df5 = df5.melt(var_name='Type', value_name='Total')
    # ordonner par amount
    df5 = df5.sort_values(by='Total', ascending=False)
    figure5 = px.pie(df5, values='Total', names='Type', hole=.3,title="Total electricity production by category <br>(terawatt-hours)")
    figure5.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(241, 240, 250, 0.9)",
        font_size = 20,
        title={
        'font': dict(
            size=18
        )
        }
    )

    conn.close()


    return df2.to_dict('records'),df.to_dict('records'), figure,{"width": "100%", "height": "100%"},barplot,{"width": "100%", "height": "100%"},figure4,{"width": "100%", "height": "100%"}, figure5,{"width": "100%", "height": "100%"},

@app.callback(
    [Output('graph6', 'figure'),
     Output('graph6','style'),
     Output('graph7', 'figure'),
     Output('graph7', 'style'),
     Output('graph8', 'figure'),
     Output('graph8', 'style'),
     Output('graph9', 'figure'),
     Output('graph9', 'style'),
     Output('graph10', 'figure'),
     Output('graph10', 'style'),
     Output('graph11', 'figure'),
     Output('graph11', 'style'),],
    [Input('my-dropdown2', 'value')]
)
def update_page2(selected_country):
    conn = sq.connect('energy.db')
    c = conn.cursor()
    df = pd.DataFrame(c.execute("SELECT year, primary_energy_consumption,population,gdp,greenhouse_gas_emissions FROM energy WHERE country = '{}'".format(selected_country)).fetchall())
    df.columns = ['Year','PEC','Population','GDP','GAE']
    df6 = df[['Year','Population']].dropna()
    df7 = df[['Population','PEC']].dropna()
    df8 = df[['GDP','PEC']].dropna()
    df9 = df[['Year','GDP']].dropna()
    df10 = df[['Year','GAE']].dropna()
    df11 = df[['Population','GAE']].dropna()

    # evolution de la population
    figure6 = px.line(df6, x='Year', y='Population',title="Population evolution in {}".format(selected_country))
    figure6.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#d117a6', width=4))
    # Setting du graph
    figure6.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title=None),
        title={
        'font': dict(
            size=18
        )
        }
    )
    # relation entre population et pec
    figure7= px.scatter(df7, x='Population', y='PEC',title="Relation between population size <br>and PEC (terawatt-hours)")
    figure7.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#d117a6', width=4))
    # Setting du graph
    figure7.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title='Population'),
        title={
        'font': dict(
            size=18
        )
        }
    )

    # relation entre population et pec
    figure8= px.scatter(df8, x='GDP', y='PEC',title="Relation between GDP <br>and PEC (terawatt-hours)")
    figure8.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#d117a6', width=4))
    # Setting du graph
    figure8.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title='GDP'),
        title={
        'font': dict(
            size=18
        )
        }
    )

    # Evolution du gdp
    figure9= px.line(df9, x='Year', y='GDP',title="Evolution of GDP")
    figure9.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#26d117', width=4))
    # Setting du graph
    figure9.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title=None),
        title={
        'font': dict(
            size=18
        )
        }
    )

    # Evolution du greenhouse gas emissions
    figure10= px.line(df10, x='Year', y='GAE',title="Greenhouse gas emissions evolution <br>(million tonnes of CO2 equivalent)")
    figure10.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#d15e17', width=4))
    # Setting du graph
    figure10.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=40, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 16,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title=None),
        title={
        'font': dict(
            size=18
        )
        }
    )

    #  gas emissions en fonction de la population
    figure11= px.scatter(df11, x='Population', y='GAE',title="Relation between population size <br>and greenhouse gas emissions")
    figure11.update_traces(fillcolor='rgba(209, 23, 166,0.13)',line=dict(color='#d117a6', width=4))
    # Setting du graph
    figure11.update_layout(
        {
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        },
        margin=dict(l=10, r=0, t=50, b=10),
        font_color = "rgba(255, 255, 255, 0.7)",
        font_size = 14,
        yaxis=dict(showgrid=False, title=None),
        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.03)',gridwidth=2,nticks=15, title='Population'),
        title={
        'font': dict(
            size=18
        )
        }
    )
    conn.close()
    return figure6,{"width": "100%", "height": "100%"},figure7,{"width": "100%", "height": "100%"},figure8,{"width": "100%", "height": "100%"},figure9,{"width": "100%", "height": "100%"},figure10,{"width": "100%", "height": "100%"},figure11,{"width": "100%", "height": "100%"},

if __name__ == '__main__':
    app.run_server(debug=True)
