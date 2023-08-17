from dash import Dash, dcc, html, no_update, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from loguru import logger
import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import openpyxl
import markdown

external_stylesheets = [
  dbc.icons.BOOTSTRAP,
  dbc.icons.FONT_AWESOME,
  dbc.themes.DARKLY,
  "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css", # https://github.com/AnnMarieW/dash-bootstrap-templates#dbccss--stylesheet

]

app = Dash(
  __name__, 
  external_stylesheets=external_stylesheets,
  external_scripts=[
  ],
  use_pages=False,
  # Add meta tags for mobile devices
  # https://community.plotly.com/t/reorder-website-for-mobile-view/33669/5?
  meta_tags = [
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
  ],
)

filename = "list.xlsx"
wb = openpyxl.load_workbook(filename, data_only=False)
ws = wb.active

# Iterate over cells to extract hyperlinks
links = {}
for row in ws.iter_rows():
    for cell in row:
        if cell.hyperlink:
            if cell.value not in links:
                links[cell.value] = cell.hyperlink.target

# Convert the Excel file to DataFrame
df = pd.read_excel(filename, header=2)

# Rename the "Restaurant Name" column to "Name"
df.rename(columns={"Restaurant Name": "Name"}, inplace=True)

# Convert the "Updated" column to American date format without the time
df["Updated"] = df["Updated"].dt.strftime("%m/%d/%Y")

# Move the "Updated" column to the end
df = df[[col for col in df.columns if col != "Updated"] + ["Updated"]]

# Update the Menu and Source columns with hyperlinks using Markdown
for col in ["Menu", "Source"]:
    df[col] = df[col].apply(lambda x: f'[{x}]({links.get(x, "#")})' if x in links else x)

def generate_column_def(col):
    # Default column definition
    col_def = {
        'headerName': col,
        'field': col,
        'resizable': True,
        'sortable': True,
        'filter': True,
    }
    
    # If the column contains hyperlinks, specify the cell renderer as Markdown
    if col in ["Menu", "Source"]:
        col_def["cellRenderer"] = "markdown"
    
    # Pin the 'Name' column to the left side
    if col == "Name":
        col_def["pinned"] = "left"
    
    return col_def

# Set the page title
app.title = "FedUp.LA"
app.description = "A list of restaurants in Los Angeles that add a surcharge to their customers' bills."

title_card = dbc.Card(
  [
    html.H3("FedUp.LA", className="card-title"),
    html.I("Add them to the fuckin' list.", style={"margin-bottom": "10px"}),
    html.P(
      "This is a mobile-friendly searchable, sortable, and filterable table of restaurants in Los Angeles that add a surcharge to their customers' bills.",
      style = {"margin-bottom": "0px"}
    ),
    html.I( # use a GitHub icon for my repo
      className="bi bi-github",
      style = {
        "margin-right": "5px",
        "margin-left": "0px"
      },
    ),
    html.A("GitHub", href='https://github.com/perfectly-preserved-pie/xenosaga', target='_blank'),
    html.I( # Add an icon for my blog
      className="fa-solid fa-blog",
      style = {
        "margin-right": "5px",
        "margin-left": "15px"
      },
    ),
    html.A("About This Project", href='https://automateordie.io/xenosaga/', target='_blank'),
  ],
  body = True
)

app.layout = html.Div([
    title_card,
    dag.AgGrid(
        id='my-grid',
        columnDefs=[generate_column_def(col) for col in df.columns],
        defaultColDef={
            'flex': 1,
            'autoSizePadding': 1,
            'minWidth': 100,
            'autoSize': True,
        },
        rowData=df.to_dict('records')
    )
])

# Dash webserver
if __name__ == '__main__':
    app.run_server(debug=True)

# Gunicorn webserver
server = app.server