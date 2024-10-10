import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import mplcursors

class InterestRateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3-Slope Jump Rate Interest Model")
        self.root.geometry("800x600")

        self.create_input_fields()
        self.create_kink_sliders()

        self.plot_button = ttk.Button(self.root, text="Plot", command=self.update_plot)
        self.plot_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.figure, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.data_borrow = None
        self.data_supply = None

        self.root.grid_rowconfigure(8, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def create_input_fields(self):
        ttk.Label(self.root, text="Base Borrow Rate (per unit of time)").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.base_borrow_rate = tk.DoubleVar(value=0)
        ttk.Entry(self.root, textvariable=self.base_borrow_rate).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Encourage Slope").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.low_slope = tk.DoubleVar(value=0)
        ttk.Entry(self.root, textvariable=self.low_slope).grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Normal Slope").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.first_jump_slope = tk.DoubleVar(value=1.585489599e-9)
        ttk.Entry(self.root, textvariable=self.first_jump_slope).grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Discourage Slope").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.second_jump_slope = tk.DoubleVar(value=3.4563673262e-8)
        ttk.Entry(self.root, textvariable=self.second_jump_slope).grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Reserve Factor (%)").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.reserve_factor = tk.DoubleVar(value=5.0)
        ttk.Entry(self.root, textvariable=self.reserve_factor).grid(row=4, column=1, padx=10, pady=5, sticky="ew")

    def create_kink_sliders(self):
        # First kink slider
        ttk.Label(self.root, text="First Kink (%)").grid(row=5, column=0, padx=10, pady=5, sticky="w")

        first_kink_frame = ttk.Frame(self.root)
        first_kink_frame.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        self.first_kink = tk.DoubleVar(value=5.0)
        self.first_kink_slider = ttk.Scale(first_kink_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.first_kink, command=self.update_slider_label)
        self.first_kink_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.first_kink_label = ttk.Label(first_kink_frame, text=f"{self.first_kink.get():.2f}%")
        self.first_kink_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Second kink slider
        ttk.Label(self.root, text="Second Kink (%)").grid(row=6, column=0, padx=10, pady=5, sticky="w")

        second_kink_frame = ttk.Frame(self.root)
        second_kink_frame.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        self.second_kink = tk.DoubleVar(value=85.0)
        self.second_kink_slider = ttk.Scale(second_kink_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.second_kink, command=self.update_slider_label)
        self.second_kink_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.second_kink_label = ttk.Label(second_kink_frame, text=f"{self.second_kink.get():.2f}%")
        self.second_kink_label.pack(side=tk.RIGHT, padx=(10, 0))

    def update_slider_label(self, value):
        self.first_kink_label.config(text=f"{self.first_kink.get():.2f}%")
        self.second_kink_label.config(text=f"{self.second_kink.get():.2f}%")
        self.update_plot()

    def update_plot(self, *args):
        base_rate = self.base_borrow_rate.get()
        low_slope = self.low_slope.get()
        first_jump_slope = self.first_jump_slope.get()
        second_jump_slope = self.second_jump_slope.get()
        first_kink = self.first_kink.get()
        second_kink = self.second_kink.get()
        reserve_factor = self.reserve_factor.get() / 100.0

        utilization = np.linspace(0, 100, 100)
        borrow_rates = []
        supply_rates = []

        for U in utilization:
            if U <= first_kink:
                borrow_rate = base_rate + (U * low_slope)
            elif U <= second_kink:
                normal_rate = base_rate + (first_kink * low_slope)
                excess_util = U - first_kink
                borrow_rate = normal_rate + (excess_util * first_jump_slope)
            else:
                normal_rate = base_rate + (first_kink * low_slope)
                normal_rate += (second_kink - first_kink) * first_jump_slope
                excess_util = U - second_kink
                borrow_rate = normal_rate + (excess_util * second_jump_slope)

            supply_rate = borrow_rate * (U / 100) * (1 - reserve_factor)
            borrow_rates.append(borrow_rate)
            supply_rates.append(supply_rate)

        self.ax.clear()
        self.data_borrow, = self.ax.plot(utilization, borrow_rates, '-b', label='Borrow Rate')
        self.data_supply, = self.ax.plot(utilization, supply_rates, '-r', label='Supply Rate')
        self.ax.set_title('Borrow and Supply Rates')
        self.ax.set_xlabel('Utilization (%)')
        self.ax.set_ylabel('Rate (per unit of time)')
        self.ax.legend()

        # Add mplcursors to enable hover
        self.cursor = mplcursors.cursor(self.ax)
        self.cursor.connect("add", self.on_hover)

        self.canvas.draw()

    def on_hover(self, sel):
        x = sel.target[0]
        borrow_rate_y = np.interp(x, np.linspace(0, 100, len(self.data_borrow.get_ydata())), self.data_borrow.get_ydata())
        supply_rate_y = np.interp(x, np.linspace(0, 100, len(self.data_supply.get_ydata())), self.data_supply.get_ydata())
        borrow_apr = borrow_rate_y * 31536000
        supply_apr = supply_rate_y * 31536000
        sel.annotation.set_text(f'Utilization: {x:.2f}%\nBorrow Rate: {borrow_rate_y:.2e} ({borrow_apr:.2f}%)\nSupply Rate: {supply_rate_y:.2e} ({supply_apr:.2f}%)')

if __name__ == "__main__":
    root = tk.Tk()
    app = InterestRateApp(root)
    root.mainloop()