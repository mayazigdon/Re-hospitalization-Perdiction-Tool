
from DataProcessing import DataProcessing
SERIAL_NUMBER = "מספר סידורי מקורי"
DIAGNOSE = "אבחנות"
DOCTOR = "רופא מאשפז"


class FilterProcessing:
    def __init__(self, df, er_df,json):
        self.update_ui_callback = None
        self.date_filter = None
        self.filter = None
        self.dates_data = None
        self.df = df
        self.er_df = er_df
        self.dp = DataProcessing(df, er_df,json)
        self.diagnoses_group = json["diagnoses"]

    @staticmethod
    def filter_data_by_diagnose(df_cleaned, selected_filter, filter_column, selected_option, diagnoses_group):
        filtered_values = []
        for index, row in df_cleaned.iterrows():
            for x in diagnoses_group[selected_filter]:
                if x in row[filter_column]:
                    filtered_values.append(row[selected_option])
        return filtered_values

    def set_update_ui_callback(self, callback):
        self.update_ui_callback = callback

    @staticmethod
    def filter_diagnose(df_cleaned, selected_filter, filter_column, selected_option, diagnoses_group):
        filtered_values = []
        # Iterate over the DataFrame rows
        for index, row in df_cleaned.iterrows():
            # Check if the value in the filter_column matches the selected_filter
            if row[filter_column] == selected_filter:
                for x in diagnoses_group:
                    for y in diagnoses_group[x]:
                        if y in row[selected_option]:
                            # If it matches, add the corresponding value from selected_option to the list
                            filtered_values.append(y)
        return filtered_values

    @staticmethod
    def generalFilter(df_cleaned, filter_column, selected_filter, selected_option):
        filtered_values = []
        for index, row in df_cleaned.iterrows():
            # Check if the value in the filter_column matches the selected_filter
            if row[filter_column] == selected_filter:
                # If it matches, add the corresponding value from selected_option to the list
                filtered_values.append(row[selected_option])
        return filtered_values

    def manage_filter_options(self,selected_option, selected_filter, filter_column):
        # Drop rows with NaN values in either the selected_option column or the filter_column
        df_cleaned = self.df.dropna(subset=[selected_option, filter_column])
        # Initialize an empty list to store the values that match the selected filter
        filtered_values = []

        if DIAGNOSE in filter_column:
            filtered_values = self.filter_data_by_diagnose(df_cleaned, selected_filter, filter_column, selected_option,self.diagnoses_group)

        elif DIAGNOSE in selected_option:
            filtered_values = self.filter_diagnose(df_cleaned, selected_filter, filter_column, selected_option,self.diagnoses_group)

        elif self.dp.is_date_col([str(value) for value in self.df[selected_option]]):
            all_dates = []
            for index, row in df_cleaned.iterrows():
                # Check if the value in the filter_column matches the selected_filter
                if row[filter_column] == selected_filter:
                    all_dates.append(row[selected_option])
            self.dp.process_dates_data(all_dates)
            filtered_values = self.dp.handle_date_data(self.date_filter)

        elif selected_option == DOCTOR:
            filtered_values = self.generalFilter(df_cleaned, filter_column, selected_filter, selected_option)
            filtered_values = self.dp.process_doctors_data(filtered_values)

        else:
            filtered_values = self.generalFilter(df_cleaned, filter_column, selected_filter, selected_option)
            # Iterate over the DataFrame rows
        filtered_values = [str(val) for val in filtered_values]
        filtered_values = [param[::-1] if self.dp.is_hebrew(param) else param for param in filtered_values]

        # Check if the column is a date column and extract/format dates if necessary
        if self.dp.isNumericData(filtered_values):
            filtered_values = self.dp.sortParameters(filtered_values)
        return filtered_values

    def choose_filter(self, selected_option,data):
        self.filter = data
        if not self.dp.is_date_col(data) and DIAGNOSE not in selected_option:
            self.update_ui_callback(self.df[selected_option].dropna().unique())
            # Set a flag to indicate that we are in the second step of filtered graph generation

    def handle_filter_selection(self, filter_column):
        col_names = []
        for col in self.df.columns:
            if not self.df[col].isna().all() and col.strip() != SERIAL_NUMBER and not self.dp.is_date_col(
                    [str(value) for value in self.df[col]]):
                if DIAGNOSE in filter_column:
                    if DIAGNOSE not in col:
                        col_names.append(col)
                else:
                    col_names.append(col)

            ui_data = [col for col in col_names if col != filter_column and not self.df[col].isna().all()]
            self.update_ui_callback(ui_data)
            # Set a flag to indicate that we are in the second step of filtered graph generation
