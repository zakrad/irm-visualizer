# Interest Rate Model Visualizer

## Formulas

```math
\text{Borrow Rate} =
\begin{cases}
\text{Base Borrow Rate} + (U \times \text{Low Slope Borrow Rate}) & \text{if } U \leq U_{optimal} \\
\text{Base Borrow Rate} + (\text{Low Slope Borrow Rate} \times U_{optimal}) + \left( (U - U_{optimal}) \times \text{High Slope Borrow Rate} \right) & \text{if } U > U_{optimal}
\end{cases}
```

```math
\text{Supply Rate} = \text{Borrow Rate} \times \left(\frac{U}{100}\right) \times (1 - \text{Reserve Factor})
```

Separated visualiser use the same formula for borrow and supply.

## Installation

- Clone the Repository:

```bash
git clone https://github.com/zakrad/irm-visualizer.git
cd IRM-plotter
```

- Create a Virtual Environment and Activate (Optional):

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

- Install Required Libraries:

```bash
pip install matplotlib numpy mplcursors
```

- Run the Application:

```bash
python jump_rate_app.py
python separated_rate_app.py
```
