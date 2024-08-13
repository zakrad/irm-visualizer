import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import mplcursors

class InterestRateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Separated Interest Rate Model")
        self.root.geometry("800x600")

        self.create_input_fields()
        self.create_slider()

        self.plot_button = ttk.Button(self.root, text="Plot", command=self.update_plot)
        self.plot_button.grid(row=7, column=1, padx=10, pady=10, sticky="ew")

        self.figure, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.data_borrow = None
        self.data_supply = None

        self.root.grid_rowconfigure(8, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def create_input_fields(self):
        ttk.Label(self.root, text="Base Borrow Rate (per unit of time)").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.base_borrow_rate = tk.DoubleVar(value=4.75646879e-8)
        ttk.Entry(self.root, textvariable=self.base_borrow_rate).grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Low Slope (Borrow Rate)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.low_slope_borrow = tk.DoubleVar(value=1.585489599e-9)
        ttk.Entry(self.root, textvariable=self.low_slope_borrow).grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="High Slope (Borrow Rate)").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.high_slope_borrow = tk.DoubleVar(value=1.26839167935e-7)
        ttk.Entry(self.root, textvariable=self.high_slope_borrow).grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Base Supply Rate (per unit of time)").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.base_supply_rate = tk.DoubleVar(value=0)
        ttk.Entry(self.root, textvariable=self.base_supply_rate).grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="Low Slope (Supply Rate)").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.low_slope_supply = tk.DoubleVar(value=1.648909183e-9)
        ttk.Entry(self.root, textvariable=self.low_slope_supply).grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self.root, text="High Slope (Supply Rate)").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.high_slope_supply = tk.DoubleVar(value=1.14155251141e-7)
        ttk.Entry(self.root, textvariable=self.high_slope_supply).grid(row=5, column=1, padx=10, pady=5, sticky="ew")

    def create_slider(self):
        ttk.Label(self.root, text="Optimal Utilization (%)").grid(row=6, column=0, padx=10, pady=5, sticky="w")

        # Create a frame to hold the slider and its label
        slider_frame = ttk.Frame(self.root)
        slider_frame.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        
        self.u_optimal = tk.DoubleVar(value=90.0)
        self.slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.u_optimal, command=self.update_slider_label)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.slider_label = ttk.Label(slider_frame, text=f"{self.u_optimal.get()}%")
        self.slider_label.pack(side=tk.RIGHT, padx=(10, 0))

    def update_slider_label(self, value):
        self.slider_label.config(text=f"{float(value):.2f}%")
        self.update_plot()

    def update_plot(self, *args):
        base_borrow_rate = self.base_borrow_rate.get()
        low_slope_borrow = self.low_slope_borrow.get()
        high_slope_borrow = self.high_slope_borrow.get()
        base_supply_rate = self.base_supply_rate.get()
        low_slope_supply = self.low_slope_supply.get()
        high_slope_supply = self.high_slope_supply.get()
        u_optimal = self.u_optimal.get()

        utilization = np.linspace(0, 100, 100)
        borrow_rates = []
        supply_rates = []

        for U in utilization:
            # Borrow Rate Calculation
            if U <= u_optimal:
                borrow_rate = base_borrow_rate + (U * low_slope_borrow)
            else:
                borrow_rate = base_borrow_rate + (low_slope_borrow * u_optimal) + ((U - u_optimal) * high_slope_borrow)

            # Supply Rate Calculation
            if U <= u_optimal:
                supply_rate = base_supply_rate + (U * low_slope_supply)
            else:
                supply_rate = base_supply_rate + (low_slope_supply * u_optimal) + ((U - u_optimal) * high_slope_supply)
                
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