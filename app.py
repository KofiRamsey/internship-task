import os
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_temporal_graph(df):
    month_num = range(1, len(df) + 1)

    # Plot the data as a double bar graph
    plt.figure(figsize=(12, 5))  # Increase the figure size
    bar_width = 0.4
    spacing = 0  # Additional spacing between the bars
    font_size = 6  # Font size for the bar labels

    plt.bar([num + spacing for num in month_num], df['Income'], label='Income', color='green', width=bar_width)
    plt.bar([num + bar_width + spacing * 2 for num in month_num], df['Expense'], label='Expense', color='red',
            width=bar_width)

    for i, income in enumerate(df['Income']):
        plt.text(month_num[i] + spacing, income, f'{income:.2f}', ha='center', va='bottom', color='black', rotation=0,
                 fontsize=font_size)

    for i, expense in enumerate(df['Expense']):
        plt.text(month_num[i] + bar_width + spacing * 2, expense, f'{expense:.2f}', ha='center', va='bottom',
                 color='black', rotation=0, fontsize=font_size)

    plt.xlabel('Month')
    plt.ylabel('Amount (Rands)')
    plt.title('Income and Expenses in the Last 12 Months')
    plt.legend()

    plt.xticks([num + bar_width + spacing for num in month_num], df['Month'], rotation=45)

    # Save the graph as a base64-encoded string
    buffer = BytesIO()
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()

    return graph_base64


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            df = pd.read_excel(file_path)

            graph_data = generate_temporal_graph(df)

            return render_template('graph.html', graph_data=graph_data)


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
