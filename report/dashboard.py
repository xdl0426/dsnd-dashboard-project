from fasthtml.common import *
import os
import sys
import matplotlib.pyplot as plt
#from fastcore.xml import FT

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
     sys.path.insert(0, PROJECT_ROOT)

#Import QueryBase, Employee, Team from employee_events
from employee_events.query_base import QueryBase
from employee_events.employee import Employee
from employee_events.team import Team

#import the load_model function from the utils.py file
from utils import load_model


# def _normalize_render_children(items):
#     """Keep only valid FastHTML children and drop None/bool placeholders."""
#     normalized = []
#     for item in items:
#         if item is None or isinstance(item, bool):
#             continue
#         if isinstance(item, (list, tuple)):
#             normalized.extend(_normalize_render_children(item))
#         else:
#             normalized.append(item)
#     return normalized


# # Runtime compatibility patch: keep the custom project files untouched,
# # but ensure FastHTML only receives valid node children and safe attributes.
# def _patch_dashboard_rendering():
#     from base_components import Dropdown, Radio
#     from combined_components import CombinedComponent

#     def safe_call_children(self, userid, model):
#         called = []
#         for child in getattr(self, 'children', []):
#             if child is None or isinstance(child, bool):
#                 continue

#             if isinstance(child, FT):
#                 rendered = child()
#             elif callable(child):
#                 try:
#                     rendered = child(userid, model)
#                 except TypeError:
#                     rendered = child()
#             else:
#                 rendered = child

#             if rendered is None or isinstance(rendered, bool):
#                 continue
#             if isinstance(rendered, (list, tuple)):
#                 called.extend(_normalize_render_children(rendered))
#             else:
#                 called.append(rendered)

#         return called

#     def safe_radio_build(self, entity_id, model):
#         children = []
#         selected_name = getattr(model, 'name', '').title()
#         for value in self.values:
#             input_child = Input(
#                 type='radio',
#                 id=value.lower(),
#                 name=self.name,
#                 value=value,
#                 hx_get=self.hx_get,
#                 hx_target=self.hx_target,
#                 checked='checked' if value == selected_name else None,
#             )
#             label_child = Label(value, _for=value.lower())
#             children.extend([input_child, label_child])
#         return children

#     def safe_dropdown_build(self, entity_id, model):
#         options = []
#         for text, value in self.component_data(entity_id, model):
#             option = Option(
#                 text,
#                 value=value,
#                 selected='selected' if str(value) == str(entity_id) else None,
#             )
#             options.append(option)
#         return Select(*options, name=self.name)

#     CombinedComponent.call_children = safe_call_children
#     Radio.build_component = safe_radio_build
#     Dropdown.build_component = safe_dropdown_build


# _patch_dashboard_rendering()

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent

# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, entity_id, model):
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name.title()
        
        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model)
    
    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(self, entity_id, model):
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        return model.names()

# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(self, entity_id, model):
        
        # Using the model argument for this method
        # return a fasthtml H1 objects
        # containing the model's name attribute
        return H1(
            f"{model.name.title()} Performance Dashboard"
        )
          

# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):
    
    # Overwrite the parent class's `visualization`
    # method. Use the same parameters as the parent
    def visualization(self, asset_id, model):
    

        # Pass the `asset_id` argument to
        # the model's `event_counts` method to
        # receive the x (Day) and y (event count)
        data = model.event_counts(asset_id)
        
        # Use the pandas .fillna method to fill nulls with 0
        data = data.fillna(0)
        
        # User the pandas .set_index method to set
        # the date column as the index
        data = data.set_index("event_date")
        
        # Sort the index
        data = data.sort_index()
        
        # Use the .cumsum method to change the data
        # in the dataframe to cumulative counts
        data = data.cumsum()
        
        
        # Set the dataframe columns to the list
        # ['Positive', 'Negative']
        data.columns = ["Positive", "Negative"]
        
        # Initialize a pandas subplot
        # and assign the figure and axis
        # to variables
        fig, ax = plt.subplots()
        # call the .plot method for the
        # cumulative counts dataframe
        data.plot(ax=ax)
        
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        # Use keyword arguments to set 
        # the border color and font color to black. 
        # Reference the base_components/matplotlib_viz file 
        # to inspect the supported keyword arguments
        self.set_axis_styling(
            ax,
            bordercolor="black",
            fontcolor="black"
        )
        
        # Set title and labels for x and y axis
        ax.set_title(f"Cumulative {model.name.title()} Events")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Event Count")

        return fig


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):

    # Create a `predictor` class attribute
    # assign the attribute to the output
    # of the `load_model` utils function
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    # Use the same parameters as the parent
    def visualization(self, asset_id, model):

        # Using the model and asset_id arguments
        # pass the `asset_id` to the `.model_data` method
        # to receive the data that can be passed to the machine
        # learning model
        data = model.model_data(asset_id)
        
        # Using the predictor class attribute
        # pass the data to the `predict_proba` method
        probabilities = self.predictor.predict_proba(data)
        
        # Index the second column of predict_proba output
        # The shape should be (<number of records>, 1)
        probabilities = probabilities[:, 1]
        
        
        # Below, create a `pred` variable set to
        # the number we want to visualize
        #
        # If the model's name attribute is "team"
        # We want to visualize the mean of the predict_proba output
        if model.name == "team":
            pred = probabilities.mean()
        # Otherwise set `pred` to the first value
        # of the predict_proba output
        else:
           pred = probabilities[0]    
        
        # Initialize a matplotlib subplot
        fig, ax = plt.subplots()
        
        # Run the following code unchanged
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)
        
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        self.set_axis_styling(
            ax,
            bordercolor="black",
            fontcolor="black"
        )
        
        return fig
 
# Create a subclass of combined_components/CombinedComponent
# called Visualizations       
class Visualizations(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    children = [
        LineChart(),
        BarChart()
    ]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')
            
# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(self, entity_id, model):
        
        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes 
        # method. Return the output
        return model.notes(entity_id)
    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#selector"
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    
# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing initialized instances 
    # of the header, dashboard filters,
    # data visualizations, and notes table
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]

    def outer_div(self, children, div_args):
        return Div(
            *children,
            cls="container",
            **div_args
        )

# Initialize a fasthtml app 
#app, rt = fast_app()
app, rt = fast_app(debug=True)

# Initialize the `Report` class
report = Report()


# Create a route for a get request
# Set the route's path to the root
@rt("/")
def get():

    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return report(1, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`. 
# parameterize the employee ID 
# to a string datatype
@rt("/employee/{id}")
def get(id: str):

    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return report(id, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`. 
# parameterize the team ID 
# to a string datatype
@rt("/team/{id}")
def get(id: str):

    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    

if __name__ == "__main__":
    serve()
