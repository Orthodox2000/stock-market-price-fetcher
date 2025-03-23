import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Set your Alpha Vantage API Key
API_KEY = "API KEY FROM https://www.alphavantage.co/"

# Toggle state for hourly/daily prices
show_daily = True

# Fetch stock data
def fetch_data(symbol, daily=True):
    try:
        # Fetch company overview
        overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={API_KEY}"
        overview_response = requests.get(overview_url)
        overview_data = overview_response.json()

        # Fetch price data (Daily or Hourly)
        price_function = "TIME_SERIES_DAILY" if daily else "TIME_SERIES_INTRADAY"
        interval = "&interval=60min" if not daily else ""
        price_url = f"https://www.alphavantage.co/query?function={price_function}{interval}&symbol={symbol}&apikey={API_KEY}"
        
        price_response = requests.get(price_url)
        price_data = price_response.json()

        if "Error Message" in overview_data or "Error Message" in price_data:
            messagebox.showerror("Error", "Invalid Symbol or API limit reached.")
            return None, None

        return overview_data, price_data
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return None, None

# Display stock data
def display_data(symbol):
    global show_daily

    overview, price = fetch_data(symbol, show_daily)
    if not overview or not price:
        return

    # Clear previous content
    for widget in result_frame.winfo_children():
        widget.destroy()

    # Display Company Overview
    info_frame = tk.Frame(result_frame, bg="#f0f0f0")
    info_frame.pack(fill=tk.X, padx=10, pady=5)

    labels = [
        ("Company", overview.get('Name', 'N/A')),
        ("Sector", overview.get('Sector', 'N/A')),
        ("Industry", overview.get('Industry', 'N/A')),
        ("Market Cap", f"${int(overview.get('MarketCapitalization', '0')):,}"),
        ("PE Ratio", overview.get('PERatio', 'N/A')),
        ("Dividend Yield", overview.get('DividendYield', 'N/A')),
        ("52 Week High", overview.get('52WeekHigh', 'N/A')),
        ("52 Week Low", overview.get('52WeekLow', 'N/A')),
        ("Description", overview.get('Description', 'N/A'))
    ]

    for i, (label, value) in enumerate(labels):
        lbl = tk.Label(info_frame, text=f"{label}: ", font=("Helvetica", 10, "bold"), bg="#f0f0f0")
        lbl.grid(row=i, column=0, sticky="w", padx=5, pady=2)
        
        val = tk.Label(info_frame, text=value, font=("Helvetica", 10), bg="#f0f0f0", wraplength=600, justify="left")
        val.grid(row=i, column=1, sticky="w", padx=5, pady=2)

    # Extract stock prices
    if show_daily:
        timeseries = price.get("Time Series (Daily)", {})
    else:
        timeseries = price.get("Time Series (60min)", {})

    if not timeseries:
        messagebox.showerror("Error", "No data available.")
        return

    # Sort by date and get 100 entries
    dates = sorted(timeseries.keys(), reverse=True)[:100]
    closing_prices = [float(timeseries[date]["4. close"]) for date in dates]

    # Reverse for chronological order
    dates.reverse()
    closing_prices.reverse()

    # Display Chart
    fig = Figure(figsize=(9, 4), dpi=100)
    ax = fig.add_subplot(111)

    # Plot with more colors
    ax.plot(dates, closing_prices, marker='o', color='green', label='Closing Price')
    
    # Improve date formatting
    ax.set_title(f"{symbol} Price Trend (Last 100 Days)" if show_daily else f"{symbol} Hourly Price Trend")
    ax.set_xlabel('Date' if show_daily else 'Time')
    ax.set_ylabel('Price (USD)')
    ax.grid(True)

    # Reduce the number of ticks on the X-axis to avoid clutter
    ax.set_xticks(dates[::10])  # Display every 10th date
    ax.set_xticklabels([datetime.strptime(d, '%Y-%m-%d').strftime('%b %d') for d in dates[::10]], rotation=45)

    ax.legend()

    # Canvas for chart
    canvas = FigureCanvasTkAgg(fig, master=result_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=5)

    # Toggle button
    toggle_btn = tk.Button(result_frame, text="Switch to Hourly" if show_daily else "Switch to Daily", font=("Arial", 12, "bold"),
                           bg="#008CBA", fg="white", command=toggle_view)
    toggle_btn.pack(pady=10)

# Toggle between daily and hourly data
def toggle_view():
    global show_daily
    show_daily = not show_daily
    display_data(symbol_entry.get().upper())

# GUI Setup
root = tk.Tk()
root.title("Stock Market Data Viewer")
root.geometry("1000x800")
root.configure(bg="#e8f5e9")

# Header
header = tk.Label(root, text="Stock Market Info App", font=("Helvetica", 18, "bold"), bg="#4CAF50", fg="white", pady=15)
header.pack(fill=tk.X)

# Input Frame
input_frame = tk.Frame(root, bg="#e8f5e9")
input_frame.pack(pady=15)

tk.Label(input_frame, text="Enter Stock Symbol:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
symbol_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
symbol_entry.grid(row=0, column=1, padx=5, pady=5)

# Search Button
search_btn = tk.Button(input_frame, text="Search", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=lambda: display_data(symbol_entry.get().upper()))
search_btn.grid(row=0, column=2, padx=5, pady=5)

# Result Frame
result_frame = tk.Frame(root, bg="white", bd=2, relief=tk.SUNKEN)
result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Footer
footer = tk.Label(root, text="Powered by Alpha Vantage API", font=("Helvetica", 10), bg="#4CAF50", fg="white", pady=5)
footer.pack(fill=tk.X)

# Start GUI
root.mainloop()
