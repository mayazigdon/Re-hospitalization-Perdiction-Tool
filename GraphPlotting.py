from collections import Counter
import matplotlib.pyplot as plt
from DataProcessing import DataProcessing
from filterProcessing import FilterProcessing
from tkinter import messagebox
ER_DATA = "עומס בחדר המיון"
DOCTOR = "רופא מאשפז"
DIAGNOSE = "אבחנות"


class GraphPlotting:
    def __init__(self, df, er_df,json):
        self.df = df
        self.er_df = er_df
        self.dp = DataProcessing(df,er_df,json)
        self.fp = FilterProcessing(df, er_df,json)

    def plotGraph(self, data, selected_parameter):

        value_counts = Counter(data)
        frequencies = list(value_counts.values())
        unique_parameters = list(value_counts.keys())  # Get the unique parameters

        # Set the font to a font that supports Hebrew characters
        plt.rcParams['font.family'] = 'David'

        # Create a figure with a wider aspect ratio to spread the labels along the x-axis
        plt.figure(figsize=(14, 6))  # Adjust the width as needed

        # Plot the bar graph using the unique_parameters and frequencies
        bars = plt.bar(unique_parameters, frequencies,color="#47b56d")

        # Add text above each bar with the y-value
        for bar in bars:
            y_value = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, y_value, f'{y_value}', ha='center', va='bottom')

        # Reverse the selectedParameter if it's in Hebrew
        if self.dp.is_hebrew(selected_parameter):
            selected_parameter = selected_parameter[::-1]

        # Customize the plot
        plt.title(selected_parameter, fontsize=10)
        plt.xlabel('Parameters', fontsize=8)
        plt.ylabel('Frequency', fontsize=8)

        # Rotate x-axis labels to prevent overlap
        if len(unique_parameters) > 5:
            plt.xticks(range(len(unique_parameters)), unique_parameters, fontsize=8, rotation=90, ha='center')
        else:
            plt.xticks(range(len(unique_parameters)), unique_parameters, fontsize=8, ha='right')

        # Adjust the margins to provide more space for x-axis labels
        plt.subplots_adjust(bottom=0.3)  # Increase the bottom margin
        plt.xlim(-1, len(unique_parameters))

        # Show the plot
        plt.show()

    def plotFilteredGraph(self, selected_option, selected_filter, filter_column):
        if self.df.empty:
            messagebox.showerror("Error", "No data available to plot.")
            return

        filtered_values = self.fp.manage_filter_options(selected_option, selected_filter, filter_column)
        # Calculate the frequencies of each unique value in the filtered list
        value_counts = Counter(filtered_values)
        # Separate the unique values and their frequencies
        unique_values = [str(value) for value in value_counts.keys()]  # Convert each value to string
        frequencies = list(value_counts.values())
        # Plot the bar graph
        plt.figure(figsize=(14,6))  # Optional: specify the figure size
        bars = plt.bar(unique_values, frequencies,color="#47b56d")  # You can choose your own color
        # Add text above each bar with the y-value
        for bar in bars:
            y_value = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, y_value, f'{y_value}', ha='center', va='bottom')
        if self.dp.is_hebrew(selected_option):
            selected_option = selected_option[::-1]
        if self.dp.is_hebrew(selected_filter):
            selected_filter = selected_filter[::-1]
        plt.title(f'Filter: {selected_filter}, Parameter: {selected_option} ')
        plt.xlabel(selected_option)
        plt.ylabel('Frequency')

        # Rotate the x-axis labels for better readability if necessary
        if len(unique_values) > 5:
            plt.xticks(range(len(unique_values)), unique_values, fontsize=8, rotation=90, ha='center')
        else:
            plt.xticks(range(len(unique_values)), unique_values, fontsize=8, ha='right')

        plt.subplots_adjust(bottom=0.3)  # Increase the bottom margin
        plt.xlim(-1, len(unique_values))
        # Show the plot
        plt.show()
