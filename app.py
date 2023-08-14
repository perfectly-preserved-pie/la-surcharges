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
    # See https://youtu.be/MzmefjD9Oow?t=331
    if col in ["Menu", "Source"]:
        col_def["cellRenderer"] = "markdown"
    
    return col_def


app.layout = html.Div([
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

# Gunicon webserver
server = app.server