import ultraimport
SV = ultraimport('__dir__/../utils/standard_version.py').StandardVersion

versions = ['1.3.2', '1.0.3', '3.7.1']
versions = sorted(versions, key=lambda x:SV(x), reverse=False)
print(versions)


# # Import necessary libraries
# import plotly.express as px
# import pandas as pd

# # Load the dataset provided by Plotly Express
# df = px.data.tips()

# # Display the first five rows of the data
# print(df.head())

# # Create the density heatmap plot
# fig = px.density_heatmap(df, x='total_bill', y='tip')

# # Customize the plot
# fig.update_layout(
#     title="Density Heatmap Plot",
#     xaxis_title="Total Bill",
#     yaxis_title="Tip"
# )

# # Display the plot
# fig.show()