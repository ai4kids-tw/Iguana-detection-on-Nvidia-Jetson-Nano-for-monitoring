import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html


def get_navbar(app):
    """Generate the navigation bar of our web-monitor.
    parameters:
        app (dash.Dash): Instance of a dash application. We use a special function to load static images.
    Output:
        navbar (dbc.Navbar): The navigation bar for our web-monitor.
    """
    navbar = dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=app.get_asset_url('AI4kids.png'),
                                     height="40px",
                                     className="ml-2")
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("AI4Kids presents",
                                            className="ml-4")
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://plot.ly",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
        ],
        color="primary",
        dark=True,
    )
    return navbar


def get_sidebar(app):
    """Generate the side bar which includes some realitive links of this project.
        parameters:
            app (dash.Dash): Instance of a dash application. We use a special function to load static images.
        Output:
            sidebar (dbc.Navbar): The side bar for our web-monitor.
        """
    sidebar = dbc.Col(
        [
            html.Div(
                [
                    html.Div(
                        html.A(
                            # A github link to this project
                            html.Img(
                                src=app.get_asset_url(
                                    'github_logo.png'),
                                width='40px',
                                className='img-fliuid')
                        )
                    ),
                    html.Div(
                        html.A(
                            # Our linkedin account
                            html.Img(
                                src=app.get_asset_url(
                                    'linkedin_logo.png'),
                                width='40px',
                                className='img-fliuid mt-4')
                        )
                    )
                ],
                className='mt-3'
            )
        ],
        width=1,
        className='border-right ml-4'
    )
    return sidebar


def get_header_grp():
    header_grp = html.Div(
        [
            # Header
            html.H2('Iguana data dashboard'),
            # Sub-header
            html.H4(
                'Live Iguana detection monitoring',
                className='text-muted')
        ]
    )
    return header_grp


def get_main_panel():
    monitor = dbc.Row(
        [

            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Loading(
                                id="rtsp-streaming-process",
                                type="default",
                                children=[
                                    html.Img(id='rtsp-stream',
                                             src="/video_feed",
                                             style={
                                                 'width': '100%'}
                                             )
                                ]
                            )
                        ]
                    )
                ),
                className='mr-10',
                width=6
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            dcc.Graph(
                                id='live-update-graph', animate=False),
                            dcc.Interval(
                                id='interval-component', interval=5 * 1000)
                        ]
                    )
                ),
                className='mr-10',
                width=6
            )
        ]
    )
    return monitor


def get_html_body(app):
    """Generate the full html for our web-monitor.
        parameters:
            app (dash.Dash): Instance of a dash application. We use a special function to load static images.
        Output:
            navbar (html.Div): A div tag that include all of the html components for our web-monitor.
    """
    html_body = html.Div([
        # Navigation Bar
        get_navbar(app),
        # Page main body
        dbc.Row([
            get_sidebar(app),
            # Monitor
            dbc.Col(
                [
                    get_header_grp(),
                    html.Br(),
                    get_main_panel()
                ]
            )]
        )])

    return html_body
