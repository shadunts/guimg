import importlib.util
import json
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from PIL import Image, ImageTk

ALGORITHMS_DIRECTORY = "<SET YOUR PATH HERE>"
# dict with { module_name: parent_directory } structure
# NOTE: when adding algorithms make sure to include them here as well
ALGORITHMS_MAP = {
    'Adaptive_Histogram_Equalization': 'preprocessing',
    'Histogram_Equalization': 'preprocessing',
    'Zero_DCE': 'preprocessing',
    'ame': 'quality_measures',
    'BIE': 'quality_measures',
    'mean_deviation': 'quality_measures',
    'shannon_entropy': 'quality_measures',
}

# order in which the algorithms should run
# NOTE: this gets sorted on category level,
#       if you want to sort on function level as well, you need to modify the sorting logic in process_image
PROCESSING_ORDER = ['preprocessing', 'quality_measures']


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.state('zoomed')
        # dict holding which algorithms have been checked by the user
        self.modules_map = {}
        # dict holding args/kwargs for each function
        self.function_args = {}
        # this is a reference to the last checked function
        # so the args/kwargs input is connected to the last selected algorithm
        self.current_function = None
        # to display images and tables in a grid
        self.image_grid_position = [0, 0]

        # START styling

        style = ttk.Style()
        style.configure('TButton', padding=6, relief="flat")
        style.configure('TCheckbutton', padding=6)
        style.configure('TLabel', padding=6)
        style.configure('Treeview', rowheight=35)
        style.configure("Custom.Treeview",
                        background="white",
                        foreground="black",
                        fieldbackground="white")
        style.configure("Custom.Treeview.Heading",
                        background="white",
                        foreground="black")

        style.layout("Custom.Treeview.Item",
                     [('Treeitem.padding', {'sticky': 'nswe', 'children':
                         [('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                          ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                          ('Treeitem.text', {'side': 'left', 'sticky': ''})]})])

        style.configure("Custom.Treeview",
                        background="white",
                        foreground="black",
                        fieldbackground="white")
        style.configure("Custom.Treeview.Heading",
                        background="white",
                        foreground="black")
        style.map('Custom.Treeview', background=[('selected', '#ececec')])

        style.map('Custom.Treeview', background=[('selected', '#ececec')])

        # END styling

        # START init layout
        self.sidebar_frame = ttk.Frame(self.root, width=200)
        self.sidebar_frame.pack(side='left', fill='y')

        self.functions_frame = ttk.Frame(self.sidebar_frame, height=400, width=200)
        self.functions_frame.pack(pady=10, padx=10, fill='x')
        # displays checkboxes based on packages in ALGORITHMS_DIRECTORY
        self.populate_function_list(self.functions_frame)

        self.upload_button = ttk.Button(self.sidebar_frame, text="Upload Image",
                                        command=lambda: self.thread_it(self.upload_image), cursor="hand2")
        self.upload_button.pack(pady=5)

        self.process_button = ttk.Button(self.sidebar_frame, text="Process Image",
                                         command=lambda: self.thread_it(self.process_image), cursor="hand2")
        self.process_button.pack(pady=5)

        self.reset_button = ttk.Button(self.sidebar_frame, text="Reset",
                                       command=lambda: self.thread_it(self.reset), cursor="hand2")
        self.reset_button.pack(pady=5)

        # input is shown when a function is selected
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(side='top', fill='x', pady=10)
        self.json_input_label = ttk.Label(self.input_frame, text="Args/kwargs (JSON):")
        self.json_input_field = ttk.Entry(self.input_frame, width=50)
        # event listener to save the input in function_args
        self.json_input_field.bind("<KeyRelease>", self.save_json_input)
        self.json_input_label.pack(side='left', padx=10)
        self.json_input_field.pack(side='left', padx=10)

        self.pipeline_var = tk.BooleanVar(value=True)
        self.pipeline_checkbox = ttk.Checkbutton(self.sidebar_frame, text="Run in a pipeline",
                                                 variable=self.pipeline_var, cursor="hand2")
        self.pipeline_checkbox.pack(pady=5)

        # main frame where images and tables are displayed
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side='right', fill='both', expand=True)

        self.image_frame = ttk.Frame(self.main_frame)
        self.image_frame.pack(fill='both', expand=True)

        # END init layout

    def thread_it(self, func, *args):
        """ Packing functions into threads """
        threading.Thread(target=func, args=args, daemon=True).start()

    def reset(self):
        # remove everything from tmp folder
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if os.path.exists(tmp_dir):
            for file in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

        # do not display any images or tables
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        # unset grid position
        self.image_grid_position = [0, 0]

        # uncheck the checked in modules map
        for module in self.modules_map:
            self.modules_map[module].set(False)

        # reset self.function_args to default state
        self.function_args = {}
        self.json_input_field.delete(0, tk.END)
        self.json_input_field.insert(0, json.dumps({"args": [], "kwargs": {}}))

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            tmp_file_path = os.path.join(tmp_dir, os.path.basename(file_path))
            with open(file_path, "rb") as f_src:
                with open(tmp_file_path, "wb") as f_dest:
                    f_dest.write(f_src.read())
            self.display_image(tmp_file_path, "Original")

    def populate_function_list(self, parent_frame):
        """ Helper to display function names with checkboxes in the sidebar """
        # loop through algorithms directory: this returns first level subdirectories (preprocessing, etc.)
        for dir_name in os.listdir(ALGORITHMS_DIRECTORY):
            dir_path = os.path.join(ALGORITHMS_DIRECTORY, dir_name)
            if os.path.isdir(dir_path):
                # the section that will hold checkboxes for current subdirectory
                section_frame = ttk.LabelFrame(parent_frame, text=dir_name, height=10, width=10)
                # fill the current section with checkboxes
                self._populate_checkboxes(section_frame, dir_path)
                section_frame.pack(fill="both", expand='yes', pady=10, anchor="w")

    def _populate_checkboxes(self, parent_frame, dir_path):
        """ Helper to display checkboxes for each category """
        for sub_dir in os.listdir(dir_path):
            # check if sub_dir is a python package
            if os.path.isdir(sub_dir_path := os.path.join(dir_path, sub_dir)) and "__init__.py" in os.listdir(
                    sub_dir_path):
                # create the checkbox
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(parent_frame, text=sub_dir, variable=var, cursor="hand2")
                chk.pack(anchor="w")
                # store the checkbox variable in modules_map for later reference
                self.modules_map[sub_dir] = var
                # add an event listener to trigger args/kwargs input on check/uncheck
                var.trace_add('write',
                              lambda *args, name=sub_dir, var=var: self.on_function_select(name, var))

    def on_function_select(self, name, var):
        """ Event listener for function checkboxes """
        # if checked
        if var.get():
            # cache the selected function name
            self.current_function = name
            # display the input
            self.json_input_label.pack(side='left')
            self.json_input_field.pack(side='left')
        else:
            # else hide the input
            self.json_input_label.pack_forget()
            self.json_input_field.pack_forget()

        # if there is already an args/kwargs input for this function
        if name in self.function_args:
            self.json_input_field.delete(0, tk.END)
            # display the previously added value
            self.json_input_field.insert(0, json.dumps(self.function_args[name]))
        else:
            self.json_input_field.delete(0, tk.END)
            # display default json
            self.json_input_field.insert(0, json.dumps({"args": [], "kwargs": {}}))

    def save_json_input(self, event=None):
        """ Event listener for args/kwargs input """
        if self.current_function:
            args_input = self.json_input_field.get()
            parsed_args = json.loads(args_input)
            self.function_args[self.current_function] = parsed_args

    def process_image(self):
        """ Apply selected algorithms to the uploaded image """
        import cv2
        import numpy as np
        import torch
        import torchvision.utils

        print('processing the image...')
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        # get the uploaded image
        image_path = next(
            (os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir) if f.endswith(('.png', '.jpg', '.jpeg'))), None)

        if not image_path:
            messagebox.showerror("Error", "No image uploaded.")
            return

        # add ALGORITHMS_DIRECTORY to sys path, so the imports in modules work
        parent_dir = os.path.dirname(ALGORITHMS_DIRECTORY)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # get the functions which need to be executed
        selected_modules = [key for key, selected in self.modules_map.items() if selected.get()]
        # sort the functions by processing order
        sorted_modules = sorted(selected_modules, key=lambda x: PROCESSING_ORDER.index(ALGORITHMS_MAP[x]))

        # doct for the numeric results(quality_measures)
        results = {}

        for module_name in sorted_modules:
            print(f'performing {module_name}...')
            # get the package
            module_dir = os.path.join(ALGORITHMS_DIRECTORY, ALGORITHMS_MAP[module_name], module_name)
            # load the main function of the package
            spec = importlib.util.spec_from_file_location('main', os.path.join(module_dir, '__init__.py'))
            # import the package
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # check if there should be any args/kwargs passed to this function
            func_args = self.function_args.get(module_name, {})
            args = func_args.get('args', [])
            kwargs = func_args.get('kwargs', {})

            # execute the main function
            result = module.main(image_path, *args, **kwargs)

            # numeric results -> store in results dict
            if isinstance(result, (int, float, np.floating)):
                results[module_name] = float(result)
            elif isinstance(result, torch.Tensor):
                # save the image with its algorithm name
                result_path = os.path.join(tmp_dir, f"{module_name}.png")
                torchvision.utils.save_image(result, result_path)
                # check if running in a pipeline is checked
                if self.pipeline_var.get():
                    # update the image_path so the next function gets the result of this function as input
                    image_path = result_path
                # display the result with it's label as module_name
                self.display_image(result_path, module_name)
            elif isinstance(result, np.ndarray):
                # save the image with its algorithm name
                result_path = os.path.join(tmp_dir, f"{module_name}.png")
                cv2.imwrite(result_path, result)
                # check if running in a pipeline is checked
                if self.pipeline_var.get():
                    # update the image_path so the next function gets the result of this function as input
                    image_path = result_path
                # display the result with it's label as module_name
                self.display_image(result_path, module_name)
            else:
                # unexpected type was returned from the main function of current module
                messagebox.showerror("Error", f"Unexpected result type from module {module_name}")
                print(type(result))
                return
            print(f'finished {module_name}')

        # if there are numeric results
        if results:
            # save json to tmp
            results_path = os.path.join(tmp_dir, "results.json")
            with open(results_path, "w") as f:
                json.dump(results, f)

            # display the table
            self.display_results_table(results_path)

        messagebox.showinfo("Processing Complete", "Image processing is complete.")

    def display_image(self, image_path, title):
        img = Image.open(image_path)
        img = img.resize((300, 200), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        row, col = self.image_grid_position
        panel = ttk.Label(self.image_frame, text=title, image=img, compound='top')
        panel.image = img
        panel.grid(row=row, column=col, padx=10, pady=10)

        # update grid position
        if col == 2:
            self.image_grid_position = [row + 1, 0]
        else:
            self.image_grid_position = [row, col + 1]

    def display_results_table(self, results_path):
        with open(results_path, "r") as f:
            results = json.load(f)

        row, col = self.image_grid_position
        tree = ttk.Treeview(self.image_frame, columns=("Algorithm", "Value"), show='headings', height=6,
                            style="Custom.Treeview")

        tree.heading("Algorithm", text="Algorithm")
        tree.heading("Value", text="Value")

        tree.tag_configure('oddrow', background='white', foreground='black')
        tree.tag_configure('evenrow', background='#f2f2f2', foreground='black')

        for idx, (algorithm, value) in enumerate(results.items()):
            row_tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
            tree.insert("", "end", values=(algorithm, value), tags=(row_tag,))
        tree.grid(row=row, column=col, padx=10, pady=10)

        # update grid position
        if col == 2:
            self.image_grid_position = [row + 1, 0]
        else:
            self.image_grid_position = [row, col + 1]


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
