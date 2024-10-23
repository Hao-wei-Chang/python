import requests
import tkinter as tk
from tkinter import scrolledtext
from bs4 import BeautifulSoup
import html
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.ticker import MultipleLocator, MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 全局变量初始化
previous_prices = []
price = {}
max_price = {}
min_price = {}
times = {}
canvas1 = None
canvas2 = None
canvas3 = None
def new_dist():
    global price
    global previous_prices
    global max_price
    global times
    stock_symbols = [symbol_entry1.get().strip(), symbol_entry2.get().strip(), symbol_entry3.get().strip(), symbol_entry4.get().strip()]
    stock_symbols = [s for s in stock_symbols if s] 
    for key in stock_symbols:
        if key not in price:
            price[key] = []
        if key not in times:
            times[key] = []
        if key not in max_price:
            max_price[key] = 0
        if key not in min_price:
            min_price[key] = 100000000000

def scrape_data():
    stock_symbols = [symbol_entry1.get().strip(), symbol_entry2.get().strip(), symbol_entry3.get().strip(), symbol_entry4.get().strip()]
    stock_symbols = [s for s in stock_symbols if s] 

    urls = {symbol: f'https://www.google.com/finance/quote/{symbol}:TPE' for symbol in stock_symbols}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 清除文本框内容
    text_box.delete('1.0', tk.END)
    time_box.delete('1.0', tk.END)
    global price
    global max_price
    global times

    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    time_box.insert(tk.END, f"{time_str}", "time")
    for key, url in urls.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')

            # 处理数据
            divs = soup.find_all('div', class_='zzDege')
            money = soup.find_all('div', class_='YMlKec fxKbKc')
            last_money = soup.find('div', class_='P6K39c')

            text_box.insert(tk.END, f"{key}:\n", "name")

            for div, price_div in zip(divs, money):
                current_price = html.unescape(price_div.text)
                current_price_num = float(current_price.replace(',', '').replace('$', ''))

                if key in previous_prices:
                    previous_price_num = float(previous_prices[key].replace(',', '').replace('$', ''))
                    diff = current_price_num - previous_price_num
                    diff_str = f"+{diff:.2f}" if diff > 0 else f"-{abs(diff):.2f}" if diff < 0 else "0.00"
                    if current_price_num > max_price[key]:
                        max_price[key] = current_price_num
                    if current_price_num < min_price[key]:
                        min_price[key] = current_price_num

                    text_box.insert(tk.END, f"{html.unescape(div.text)}\n", "name")
                    text_box.insert(tk.END, f"前次收盤: {last_money.text if last_money else 'N/A'}\n", "price")
                    text_box.insert(tk.END, f"本日最高: ${max_price[key]:,.2f}\n", "highest")
                    text_box.insert(tk.END, f"本日最低: ${min_price[key]:,.2f}\n", "lowest")
                    text_box.insert(tk.END, f"時價: {current_price}\n", "price")

                    if diff > 0:
                        text_box.insert(tk.END, f"價差: {diff_str}\n\n", "positive")
                    elif diff < 0:
                        text_box.insert(tk.END, f"價差: {diff_str}\n\n", "negative")
                    else:
                        text_box.insert(tk.END, f"價差: {diff_str}\n\n", "neutral")
                    previous_prices[key] = current_price

                else:
                    text_box.insert(tk.END, f"{html.unescape(div.text)}\n", "name")
                    text_box.insert(tk.END, f"時價: {current_price}\n", "price")
                    text_box.insert(tk.END, "價差: 0.00\n", "neutral")
                    previous_prices[key] = current_price

                price[key].append(current_price_num)
                times[key].append(time_str)


        except requests.RequestException as e:
            text_box.insert(tk.END, f"Error fetching data from {url}: {e}\n", "error")


def update_plots():
    global canvas1, canvas2, canvas3
    stock_symbols = [symbol_entry1.get().strip(), symbol_entry2.get().strip(), symbol_entry3.get().strip(), symbol_entry4.get().strip()]
    stock_symbols = [s for s in stock_symbols if s]  # 移除空符号
    plt.close('all')

    # 清除先前的图表
    if canvas1:
        canvas1.get_tk_widget().destroy()
    if canvas2:
        canvas2.get_tk_widget().destroy()
    if canvas3:
        canvas3.get_tk_widget().destroy()
    for widget in pic_frame.winfo_children():
        widget.destroy()

    # 图表1 (仅在有stock_symbols[0]时绘制)
    if len(stock_symbols) > 0:
        fig1, ax1 = plt.subplots(figsize=(5, 3.5), dpi=100)
        ax1.plot(times[stock_symbols[0]], price[stock_symbols[0]], label=stock_symbols[0], color='blue')
        ax1.yaxis.set_major_locator(MaxNLocator(10))
        ax1.xaxis.set_visible(False)
        ax1.legend()

        canvas1 = FigureCanvasTkAgg(fig1, master=pic_frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    # 图表2 (仅在有stock_symbols[1]时绘制)
    if len(stock_symbols) > 1:
        fig2, ax2 = plt.subplots(figsize=(5, 3), dpi=100)
        ax2.plot(times[stock_symbols[1]], price[stock_symbols[1]], label=stock_symbols[1], color='green')
        ax2.yaxis.set_major_locator(MaxNLocator(10))
        ax2.xaxis.set_visible(False)
        ax2.legend()

        canvas2 = FigureCanvasTkAgg(fig2, master=pic_frame)
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=1, column=0, sticky='nsew')

    # 图表3 (仅在有stock_symbols[2]时绘制)
    if len(stock_symbols) > 2:
        fig3, ax3 = plt.subplots(figsize=(7, 3.5), dpi=100)
        ax3.plot(times[stock_symbols[2]], price[stock_symbols[2]], label=stock_symbols[2], color='yellow')
        ax3.yaxis.set_major_locator(MaxNLocator(10))
        ax3.xaxis.set_visible(False)
        ax3.legend()

        canvas3 = FigureCanvasTkAgg(fig3, master=pic_frame)
        canvas3.draw()
        canvas3.get_tk_widget().grid(row=0, column=1, sticky='nsew')

    if len(stock_symbols) > 3:
        fig4, ax4 = plt.subplots(figsize=(7, 3), dpi=100)
        ax4.plot(times[stock_symbols[3]], price[stock_symbols[3]], label=stock_symbols[3], color='red')
        ax4.yaxis.set_major_locator(MaxNLocator(10))
        ax4.xaxis.set_visible(False)
        ax4.legend()

        canvas4 = FigureCanvasTkAgg(fig4, master=pic_frame)
        canvas4.draw()
        canvas4.get_tk_widget().grid(row=1, column=1, sticky='nsew')

    # 更新滚动区域
    pic_frame.update_idletasks()
    pic_canvas.config(scrollregion=pic_canvas.bbox("all"))
    pic_canvas.update_idletasks()

    # 计划下次更新
    root.after(15000, update_plots)  # 每15秒更新一次


def scheduled_scrape():
    if not stop_flag[0]:
        new_dist()
        scrape_data()
        root.after(3000, scheduled_scrape)

def start_scraping():
    global previous_prices
    previous_prices = {}  # 清空之前的价格数据
    stop_flag[0] = False
    new_dist()
    scheduled_scrape()
    update_plots()

def stop_scraping():
    stop_flag[0] = True

root = tk.Tk()
root.title('Stock Data')
root.state('normal')
root.configure(background='#000')

# 创建主框架
main_frame = tk.Frame(root, bg='#000')
main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

# 创建按钮框架
button_frame = tk.Frame(main_frame, bg='#000')
button_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10, columnspan=2)

# 创建 Start 和 End 按钮
start_button = tk.Button(button_frame, text="Start", command=start_scraping, bg='#4CAF50', fg='white', font=('Arial', 14))
start_button.grid(row=0, column=0, padx=10)

end_button = tk.Button(button_frame, text="End", command=stop_scraping, bg='#f44336', fg='white', font=('Arial', 14))
end_button.grid(row=0, column=1, padx=10)

# 创建股票符号输入框
symbol_frame = tk.Frame(button_frame, bg='#000')
symbol_frame.grid(row=0, column=2, pady=10, sticky="w", padx=10)

symbol_label1 = tk.Label(symbol_frame, text="stock1:", bg='#000', fg='white', font=('Arial', 12))
symbol_label1.grid(row=0, column=0, padx=5)

symbol_entry1 = tk.Entry(symbol_frame, font=('Arial', 12))
symbol_entry1.grid(row=0, column=1, padx=5)

symbol_label2 = tk.Label(symbol_frame, text="stock2:", bg='#000', fg='white', font=('Arial', 12))
symbol_label2.grid(row=0, column=2, padx=5)

symbol_entry2 = tk.Entry(symbol_frame, font=('Arial', 12))
symbol_entry2.grid(row=0, column=3, padx=5)

symbol_label3 = tk.Label(symbol_frame, text="stock3:", bg='#000', fg='white', font=('Arial', 12))
symbol_label3.grid(row=1, column=0, padx=5)

symbol_entry3 = tk.Entry(symbol_frame, font=('Arial', 12))
symbol_entry3.grid(row=1, column=1, padx=5)

symbol_label4 = tk.Label(symbol_frame, text="大盤:", bg='#000', fg='white', font=('Arial', 12))
symbol_label4.grid(row=1, column=2, padx=5)

symbol_entry4 = tk.Entry(symbol_frame, font=('Arial', 12))
symbol_entry4.grid(row=1, column=3, padx=5)
symbol_entry4.insert(0, "IX0001")

time_box = tk.Text(button_frame, bg='#000', fg='white', wrap=tk.WORD, height=3, width=40)
time_box.grid(row=0, column=3, padx=(0, 10))

# 创建文本框和图表区域框架
content_frame = tk.Frame(main_frame, bg='#000')
content_frame.grid(row=1, column=0, sticky='nsew')

# 创建左侧文本框
text_box = tk.Text(content_frame, font=('Arial', 12), bg='#000', fg='white', wrap=tk.WORD, height=35, width=38)
text_box.grid(row=0, column=0, padx=(0, 10), sticky='ns')

# 创建 Canvas 组件和滚动条
pic_canvas = tk.Canvas(content_frame, bg='#012', width=1420)
pic_frame = tk.Frame(pic_canvas, bg='#000')

pic_canvas.create_window((0, 0), window=pic_frame, anchor="nw")
pic_frame.bind("<Configure>", lambda e: pic_canvas.config(scrollregion=pic_canvas.bbox("all")))

pic_canvas.grid(row=0, column=1, columnspan=2, sticky='nsew')

# 创建一个布尔标志来控制爬取的开始和停止
stop_flag = [True]

# 設置不同部分的顏色標籤
text_box.tag_config("name", foreground="white", font=('Arial', 13, 'bold'))
text_box.tag_config("price", foreground="yellow", font=('Arial', 16, 'bold'))
text_box.tag_config("positive", foreground="red", font=('Arial', 16, 'bold'))
text_box.tag_config("negative", foreground="green", font=('Arial', 16, 'bold'))
text_box.tag_config("neutral", foreground="grey", font=('Arial', 16, 'bold'))
text_box.tag_config("error", foreground="red", font=('Arial', 12, 'bold'))
time_box.tag_config("time", foreground='#73E5E3', font=('Arial', 20, 'bold'))
text_box.tag_config("highest", foreground='#FF4500', font=('Arial', 16, 'bold'))
text_box.tag_config("lowest", foreground='#3A5FCD', font=('Arial', 16, 'bold'))
# 启动主循环
root.mainloop()
