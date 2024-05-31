import re
from datetime import datetime
import pandas as pd
ER_ARRIVAL_DATE = "תאריך הגעה למיון"
WALKING_ER = "מיון מהלכים"
INTERNAL_ER = "מיון פנימי"
INTERNAL_ER_INF = "רפואה דחופה זיהומים"


class DataProcessing:
    def __init__(self, df, er_df,json):
        self.diagnose_data = None
        self.diagnoses_group = None
        self.dates_data = None
        self.df = df
        self.er_df = er_df

    @staticmethod
    def is_date(string):
        date_pattern = r'\b\d{4}-\d{1,2}-\d{1,2}\b'
        match = re.search(date_pattern, string)
        if match:
            return True
        else:
            return False

    @staticmethod
    def is_not_empty_or_whitespace(s):
        return bool(s.strip())

    @staticmethod
    def extractDate(string):
        date_pattern = r'\b\d{4}-\d{1,2}-\d{1,2}\b'
        match = re.search(date_pattern, string)
        if match:
            matched_date = match.group()
            return matched_date
        else:
            return None

    @staticmethod
    def sortParameters(parameters):
        parameters = [float(s) for s in parameters]
        parameters = sorted(parameters)
        parameters = [str(value) for value in parameters]  # Convert each value to string
        return parameters

    @staticmethod
    def is_hour(string):
        hour_pattern = r'\b\d{2}:\d{2}:\d{2}\b'
        match = re.search(hour_pattern, string)
        if match:
            return True
        else:
            return False

    @staticmethod
    def extractHour(string):
        hour_pattern = r'\b\d{2}:\d{2}:\d{2}\b'
        match = re.search(hour_pattern, string)
        if match:
            matched_hour = match.group()
            return matched_hour
        else:
            return None

    @staticmethod
    def is_hebrew(word):
        for char in word:
            if '\u0590' <= char <= '\u05FF':
                return True
        return False

    def is_date_col(self, column_data):
        # check whether it's a date format - if 10 first elements contains date format it's probably a date
        for i in range(min(10, len(column_data))):
            if not self.is_date(column_data[i]) and column_data[i] != ' ':
                return False
        return True

    @staticmethod
    def get_day_of_week(date_string):
        date_format = "%Y-%m-%d"
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_string, date_format)
        # Format the datetime object to get the day of the week
        # %A returns the full weekday name
        day_of_week = date_obj.strftime("%A")
        return day_of_week

    @staticmethod
    def get_month_name(date_string, date_format="%Y-%m-%d"):
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_string, date_format)
        # Format the datetime object to get the full month name
        month_name = date_obj.strftime("%B")
        return month_name

    def handle_date_data(self, selected_parameter):
        if selected_parameter == "sort by hours":
            return self.dates_data["hour"]

        elif selected_parameter == "sort by the day of the week":
            all_days = []
            for date in self.dates_data["date"]:
                day = self.get_day_of_week(date)
                all_days.append(day)
            return all_days

        elif selected_parameter == "sort by months":
            all_months = []
            for date in self.dates_data["date"]:
                month = self.get_month_name(date)
                all_months.append(month)
            return all_months

        elif selected_parameter == "sort by years":
            all_years = []
            for date in self.dates_data["date"]:
                year = date.split("-")[0]
                all_years.append(year)
            return all_years

    def handle_ER_date_data(self, selected_parameter,data):

        dates_list = [date for date in self.er_df[ER_ARRIVAL_DATE] if not pd.isna(date)]
        dates_list = [self.extractDate(str(date)) for date in dates_list]

        if selected_parameter == "sort by the day of the week":
            all_days = {}
            for key, value in data.items():
                for date in dates_list:
                    if date in key:
                        day = self.get_day_of_week(date)
                        if day in all_days:
                            all_days[day] += value
                        else:
                            all_days[day] = value
            return all_days

        elif selected_parameter == "sort by months":
            all_months = {}
            for key, value in data.items():
                for date in dates_list:
                    if date in key:
                        month = self.get_month_name(date)
                        if month in all_months:
                            all_months[month] += value
                        else:
                            all_months[month] = value
            return all_months

        elif selected_parameter == "sort by years":
            all_years = {}
            for key, value in data.items():
                for date in dates_list:
                    if date in key:
                        year = date.split("-")[0]
                        if year in all_years:
                            all_years[year] += value
                        else:
                            all_years[year] = value
            return all_years

    def process_dates_data(self, parameters):
        date = [self.extractDate(parameter) for parameter in parameters if
                parameter and self.is_date(parameter)]
        hour = [self.extractHour(parameter) for parameter in parameters if
                parameter and self.is_hour(parameter)]
        hour = [h.split(":")[0] for h in hour]
        hour = self.sortParameters(hour)
        self.dates_data = {"hour": hour, "date": date}

    def process_er_data(self):
        date_col = ER_ARRIVAL_DATE
        load_info = {}
        sum_load_info = {}
        df_cleaned = []
        relevant_columns = [WALKING_ER, INTERNAL_ER, INTERNAL_ER_INF]

        for col in self.er_df.columns:
            # Check if the current column is one of the specified ER departments/services
            if col in relevant_columns:
                # Drop rows where data in either the current column or the date column is missing
                df_cleaned = self.er_df.dropna(subset=[col, date_col])
                # Iterate over the rows in the cleaned DataFrame

        for index, row in df_cleaned.iterrows():
            for col in relevant_columns:
                # Get the date from the date column
                date = self.extractDate(row[date_col])
                # If the date is not already in the load_info dictionary, initialize it with an empty list
                if date not in load_info:
                    load_info[date] = []
                    # Append the value from the current ER department/service column to the list for this date
                load_info[date].append(row[col])

        for key, value in load_info.items():
            sum = 0
            for v in value:
                sum += v
                sum_load_info[key] = sum

        return sum_load_info

    @staticmethod
    def process_doctors_data(parameters):
        pattern_to_remove = r'מ\.ר\.\d+'
        all_cleaned_data = []
        for parameter in parameters:
            # Use re.sub() to replace the matched pattern with an empty string
            cleaned_data = re.sub(pattern_to_remove, '', parameter).strip()
            all_cleaned_data.append(cleaned_data)
        return all_cleaned_data

    def preprocess_data(self, selected_column,json_data):
        self.diagnoses_group = json_data["diagnoses"]
        self.diagnose_data = self.df[selected_column]

        # Combine conversion to string, removal of brackets, and stripping in one list comprehension
        self.diagnose_data = [str(x).replace("[", "").replace("]", "").strip() for x in self.diagnose_data]

        # Split the strings by commas and strip whitespace in one step using a nested list comprehension
        self.diagnose_data = [item.strip() for s in self.diagnose_data for item in s.split(',')]

    def process_diagnose_data(self, selected_column):
        all_data = []
        for x in self.diagnoses_group[selected_column]:
            for y in self.diagnose_data:
                if x == y:
                    all_data.append(x)
        return all_data

    @staticmethod
    def isNumericData(parameters):
        for value in parameters:
            try:
                float(value)
            except ValueError:
                return False
        return True
