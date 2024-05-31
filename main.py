
import tkinter as tk
import pandas as pd
import json
from tkinter import messagebox
from tkinter import filedialog
import os
from DataProcessing import DataProcessing
from filterProcessing import FilterProcessing
from GraphPlotting import GraphPlotting

DIAGNOSE = "אבחנות"
DOCTOR = "רופא מאשפז"
SERIAL_NUMBER = "מספר סידורי מקורי"
READMISSION_DIAGNOSES = "אבחנות בקבלה לאשפוז החוזר"
ER_DATA = "עומס בחדר המיון"
ER_ARRIVAL_DATE = "תאריך הגעה למיון"
WALKING_ER = "מיון מהלכים"
INTERNAL_ER = "מיון פנימי"
INTERNAL_ER_INF = "רפואה דחופה זיהומים"


class Application:
    def __init__(self, window):
        self.date_filter = None
        self.selected_parameter = None
        self.filter_column = None
        self.data = None
        self.filter = None
        self.listbox = None
        self.button_frame = None
        self.diagnose_data = None
        self.header_label = None
        self.dates_data = None
        self.diagnoses_group = None
        self.file_path = None
        self.graph_type = None
        self.json_file = "data.json"

        self.window = window  # Store the window as an instance variable
        window.geometry("800x700")
        window.title("Readmission Prediction Tool")
        window.configure(bg="#051a1c")
        self.button_style = {
            'bg': '#90ee90',  # Light green background
            'fg': 'black',  # Text color
            'bd': 1,  # Border width
            'relief': 'groove',  # Border style
            'highlightthickness': 5,  # No highlight border
            'padx': 20,  # Horizontal padding
            'pady': 10,  # Vertical padding

        }
        with open(self.json_file, 'r', encoding='utf-8') as json_file:
            try:
                self.json_data = json.load(json_file)
                path = self.json_data["path"]
                er_path = self.json_data["ER path"]
                if path:
                    self.df = pd.read_csv(path,index_col=0)
                if er_path:
                    if self.is_excel_file(er_path):
                        er_path = self.convert_excel_to_csv(er_path)
                    self.er_df = pd.read_csv(er_path, skiprows=2, index_col=0, encoding='utf-8')
                    self.er_df = self.er_df.loc[:, ~self.er_df.columns.str.contains('^Unnamed')]

            except json.JSONDecodeError:
                messagebox.showerror("Error", "missing a CSV file path, please load CSV file first.")
        self.diagnoses_group = self.json_data["diagnoses"]
        self.dp = DataProcessing(self.df, self.er_df,self.json_data)
        self.gp = GraphPlotting(self.df, self.er_df,self.json_data)
        self.fp = FilterProcessing(self.df, self.er_df,self.json_data)
        self.fp.set_update_ui_callback(self.update_ui)
        self.write_diagnoses_list_to_computer()
        self.welcomePage()

    def update_ui(self, data_to_display):
        self.generateListboxForGraph(data_to_display)

    def write_diagnoses_list_to_computer(self):
        current_directory = os.getcwd()
        filename = 'Diagnoses List.txt'
        file_path = os.path.join(current_directory, filename)
        text = json.dumps(self.json_data["diagnoses"], ensure_ascii=False, indent=4)

        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text)

    @staticmethod
    def is_excel_file(file_path):
        return file_path.lower().endswith(('.xls', '.xlsx', '.xlsm'))

    @staticmethod
    def is_csv_file(file_path):
        return file_path.lower().endswith('.csv')

    @staticmethod
    def convert_excel_to_csv(excel_file_path):
        df = pd.read_excel(excel_file_path)
        csv_file_path = os.path.splitext(excel_file_path)[0] + '.csv'
        df.to_csv(csv_file_path, index=False)
        return csv_file_path

    def uploadERData(self):
        file_path = filedialog.askopenfilename()
        if self.is_excel_file(file_path):
            file_path = self.convert_excel_to_csv(file_path)
        if not self.is_csv_file(file_path):
            messagebox.showerror("Error",
                                 "The selected file is not a CSV or Excel file. Please select a different file.")
        self.er_df = pd.read_csv(file_path, skiprows=2, index_col=0, encoding='utf-8')

        cols = [ER_ARRIVAL_DATE, WALKING_ER,INTERNAL_ER,INTERNAL_ER_INF]
        if not all(col in self.er_df.columns for col in cols):
            messagebox.showerror("Error","The format of the  ER data is incorrect")
        else:
            with open(self.json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data["ER path"] = file_path
            with open(self.json_file, 'w') as file:
                json.dump(data, file)

    def uploadReadmissionData(self):
        file_path = filedialog.askopenfilename()
        if self.is_excel_file(file_path):
            file_path = self.convert_excel_to_csv(file_path)
        if not self.is_csv_file(file_path):
            messagebox.showerror("Error",
                                 "The selected file is not a CSV or Excel file. Please select a different file.")
        self.df = pd.read_csv(file_path, index_col=0)
        cols = [DOCTOR,READMISSION_DIAGNOSES]
        if not all(col.strip() in self.df.columns for col in cols):
            messagebox.showerror("Error", "The format of the readmission data is incorrect")

        else:
            self.file_path = file_path
            with open(self.json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            data["path"] = file_path
            with open(self.json_file, 'w') as file:
                json.dump(data, file)

    def uploadCSV(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        er_data_button = tk.Button(self.button_frame, text="Er data upload", command=self.uploadERData,
                                   **self.button_style, height=3, width=50)
        main_data_button = tk.Button(self.button_frame, text="readmission data upload",
                                     command=self.uploadReadmissionData, **self.button_style, height=3, width=50)
        back_button = tk.Button(self.button_frame, text="Back to Home", command=self.welcomePage,
                                **self.button_style, height=3, width=50)

        # Place buttons next to each other using grid
        er_data_button.pack(side='top',pady=10)
        main_data_button.pack(side='top',pady=10)
        back_button.pack(side='top',pady=10)

    def diagnosesMenu(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.generateListboxForGraph(self.diagnoses_group)

    def generateListboxForGraph(self, column_names):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        self.header_label = tk.Label(self.button_frame, text="Select parameter", bg="#051a1c", fg="white")
        self.main_header_label.config(bg='#7dd17d')
        if self.graph_type == 'filter_type_selection':
            self.header_label.config(text="Choose a filter")

        self.header_label.pack(side='top', fill='x')

        self.listbox = tk.Listbox(
            self.button_frame,
            selectmode='single',
            exportselection=False,
            bg="#051a1c",  # Background color of the Listbox
            fg="white",  # Text color of the Listbox items
            selectbackground="white",  # Background color of the selected item
            selectforeground="black",  # Text color of the selected item
            highlightthickness=0,  # No highlight border
            relief='flat'  # Flat relief to remove the border
        )

        for col_name in column_names:
            self.listbox.insert('end', col_name)
        self.listbox.pack(side='left', fill='both', expand=True)

        button_frame = tk.Frame(self.button_frame, bg='#051a1c')
        button_frame.pack(side='top', fill='x')

        confirm_button = tk.Button(button_frame, text="Confirm Selection", command=self.confirm_selection_for_graph)
        confirm_button.pack(side='top', fill='x', padx=10, pady=10)

        back_button = tk.Button(button_frame, text="Back To Main Menu", command=self.welcomePage)
        back_button.pack(side='top', fill='x', padx=10, pady=10)

    def dateMenu(self,selected_parameter):
        if ER_DATA in selected_parameter:
            parameters = ["sort by the day of the week", "sort by months", "sort by years"]
        else:
            parameters = ["sort by hours","sort by the day of the week","sort by months","sort by years"]
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.generateListboxForGraph(parameters)

    def generateFilteredGraph(self):
        if self.df.empty:
            messagebox.showerror("Error", "Please provide a CSV file first.")
            return
        # Initiate the first selection for the filter
        col_names = []
        for col in self.df.columns:
            if not self.df[col].isna().all() and col.strip() != SERIAL_NUMBER and not self.dp.isNumericData(
                    [str(value) for value in self.df[col]]) and not self.dp.is_date_col(
                    [str(value) for value in self.df[col]]):
                col_names.append(col)
        self.generateListboxForGraph(col_names)
        self.header_label.config(text="Choose a filter type")
        # Set a flag to indicate that we are in the first step of filtered graph generation
        self.graph_type = 'filter_type_selection'

    def generate_graph(self):
        if self.df.empty:
            messagebox.showerror("Error", "Please provide a CSV file first.")
            return
        if self.er_df.empty:
            messagebox.showerror("Error", "Please provide a ER CSV file first.")
            return
    # Set up the listbox for user selection for a regular graph
        col_names = []
        for col in self.df.columns:
            if not self.df[col].isna().all() and col.strip() != SERIAL_NUMBER:
                col_names.append(col)
        col_names.append(ER_DATA)
        self.generateListboxForGraph(col_names)
    # Set a flag to indicate that we are generating a regular graph
        self.graph_type = 'regular'

    def handle_data(self, selected_parameter):
        if self.df.empty:
            messagebox.showerror("Error", "No data available to plot.")
            return

        if ER_DATA in selected_parameter:
            data = self.dp.process_er_data()
            self.dateMenu(selected_parameter)
            return data

        else:
            column_data = self.df[selected_parameter]
            parameters = [str(value) for value in column_data]

            if selected_parameter == DOCTOR:
                parameters = self.dp.process_doctors_data(parameters)

            elif DIAGNOSE in selected_parameter:
                self.dp.preprocess_data(selected_parameter,self.json_data)
                if self.graph_type != "parameter_selection":
                    self.diagnosesMenu()

            # Check if the column is a date column and extract/format dates if necessary
            if self.dp.isNumericData(parameters):
                parameters = self.dp.sortParameters(parameters)

            if self.dp.is_date_col(parameters):  # Assuming is_date_col checks the column name
                self.dp.process_dates_data(parameters)
                self.dateMenu(selected_parameter)

                if self.graph_type == 'parameter_selection':
                    self.graph_type = "date_filter_selection"

            parameters = [param[::-1] if self.dp.is_hebrew(param) else param for param in parameters]
            return parameters

    def confirm_selection_for_graph(self):
        selection_index = self.listbox.curselection()
        if not selection_index:
            messagebox.showerror("Error", "Please select an option.")
            return

        selected_column = self.listbox.get(selection_index[0])

        if self.graph_type == 'regular':
            # The user has selected the parameter for a regular graph; generate the graph
            self.data = self.handle_data(selected_column)

            if ER_DATA in selected_column:
                self.graph_type = 'ER'

            elif self.dp.is_date_col(self.data) and self.graph_type != "ER":
                self.graph_type = "date"

            elif DIAGNOSE in selected_column:
                self.graph_type = 'diagnose'

            else:
                self.gp.plotGraph(self.data,selected_column)

        elif self.graph_type == 'diagnose':
            all_data = self.dp.process_diagnose_data(selected_column)
            self.gp.plotGraph(all_data,selected_column)

        elif self.graph_type == 'date':
            data = self.dp.handle_date_data(selected_column)
            self.gp.plotGraph(data,selected_column)

        elif self.graph_type == 'filter_selection':
            self.fp.handle_filter_selection(self.filter_column)
            self.graph_type = 'parameter_selection'
            self.filter = selected_column

        elif self.graph_type == 'filter_type_selection':
            data = self.handle_data(selected_column)
            self.fp.choose_filter(selected_column,data)
            self.graph_type = 'filter_selection'
            self.filter_column = selected_column

        elif self.graph_type == 'parameter_selection':
            if selected_column in [col for col in self.df.columns]:
                self.handle_data(selected_column)
                if not self.dp.is_date_col([str(value) for value in self.df[selected_column]]):
                    self.gp.plotFilteredGraph(selected_column,self.filter,self.filter_column)
                self.selected_parameter = selected_column

        elif self.graph_type == "date_filter_selection":
            self.date_filter = selected_column
            self.gp.plotFilteredGraph(self.selected_parameter, self.filter, self.filter_column)

        elif self.graph_type == "ER":
            dates_data = self.dp.handle_ER_date_data(selected_column,self.data)
            self.gp.plotGraph(dates_data,selected_column)

    def trainModelPage(self):
        pass

    def predictionsPage(self):
        pass

    def welcomePage(self):
        # Clear the window of any existing widgets
        for widget in self.window.winfo_children():
            widget.destroy()

        # Create a header label with the title of the application and add padding above it
        self.main_header_label = tk.Label(self.window, text="Analyze and Predict Readmission Tool", bg="#051a1c", fg="white",
                                font=("Helvetica", 16))
        self.main_header_label.pack(side=tk.TOP,pady=(100, 0))  # Increase the top padding to lower the headline


        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.window, bg='#051a1c')
        self.button_frame.pack(side=tk.TOP, fill='both', expand=True,
                               pady=(50, 0))  # Add padding to the top to lower the buttons

        # Create buttons and place them in the grid
        button = tk.Button(self.button_frame, text="Upload CSV", command=self.uploadCSV, height=5, width=20,
                           **self.button_style)
        button1 = tk.Button(self.button_frame, text="Generate Graph", command=self.generate_graph, height=5, width=20,
                            **self.button_style)
        button2 = tk.Button(self.button_frame, text="Generate Filtered Graph", command=self.generateFilteredGraph,
                            height=5, width=20, **self.button_style)
        button3 = tk.Button(self.button_frame, text="Train Machine Learning Model", command=self.trainModelPage,
                            height=5, width=20, **self.button_style)
        button4 = tk.Button(self.button_frame, text="Make ML Predictions", command=self.predictionsPage, height=5,
                            width=20, **self.button_style)

        # Align buttons to the right by adding empty columns to the left
        self.button_frame.grid_columnconfigure(0, weight=1)  # This empty column will push the buttons to the right

        # Add an empty row at the top with weight to push the buttons down
        self.button_frame.grid_rowconfigure(0, weight=1)  # This empty row will push the buttons down

        # Place buttons starting from the second row (index 1)
        button.grid(row=1, column=1, padx=5, pady=5, sticky='e')
        button1.grid(row=1, column=2, padx=5, pady=5, sticky='e')
        button2.grid(row=2, column=0, padx=5, pady=(20, 150), sticky='e')
        button3.grid(row=2, column=1, padx=5, pady=(20, 150), sticky='e')
        button4.grid(row=2, column=2, padx=5, pady=(20, 150), sticky='e')


if __name__ == "__main__":
    ui = tk.Tk()
    app = Application(ui)
    ui.mainloop()
