import random
import json
import plotly
import plotly.graph_objects as go
from flask import Flask, render_template, jsonify

app = Flask(__name__)

COLORS = {
    'primary': '#D4B896',
    'secondary': '#E8D0B3',
    'accent1': '#F5E6D3',
    'accent2': '#C9A982',
    'pastel_pink': '#F8C8C8',
    'pastel_green': '#C8E6C9',
    'pastel_peach': '#FFDAB9',
    'pastel_lavender': '#E6E6FA',
    'pastel_mint': '#A7FFEB',
    'background': '#FFF8F0',
    'text': '#5D4037',
    'grid': '#E0D3C2'
}

current_data = None


def generate_random_data():
    global current_data

    random.seed()
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

    data_types = {
        'Продажи': (50, 300),
        'Затраты': (30, 200),
        'Прибыль': (20, 150),
        'Клиенты': (100, 600),
        'Конверсия': (5, 25),
        'Оборот': (1000, 5000)
    }

    selected_indicators = random.sample(list(data_types.keys()), 4)

    data = {'Месяц': months}
    for indicator in selected_indicators:
        min_val, max_val = data_types[indicator]
        data[indicator] = [random.randint(min_val, max_val) for _ in range(12)]

    current_data = data
    return data


def create_bar_chart(data, chart_type='grouped'):


    fig = go.Figure()
    categories = data['Месяц']
    columns = [col for col in data.keys() if col != 'Месяц']


    bar_colors = [
        COLORS['primary'],
        COLORS['pastel_green'],
        COLORS['pastel_peach'],
        COLORS['pastel_pink']
    ]

    for i, column in enumerate(columns):
        fig.add_trace(go.Bar(
            name=column,
            x=categories,
            y=data[column],
            marker_color=bar_colors[i % len(bar_colors)],
            text=data[column],
            textposition='outside',
            textfont=dict(color=COLORS['text'], size=11),
            hovertemplate=f'<b>{column}</b>: %{{y}}<br>Месяц: %{{x}}<extra></extra>'
        ))


    if chart_type == 'stacked':
        barmode = 'stack'
        title_suffix = ' (сложенная)'
    elif chart_type == 'percentage':
        barmode = 'stack'
        title_suffix = ' (в процентах)'
        fig.update_layout(barmode='stack', barnorm='percent')
    else:
        barmode = 'group'
        title_suffix = ' (группированная)'


    fig.update_layout(
        title=dict(
            text=f'<b>Динамика показателей по месяцам{title_suffix}</b>',
            font=dict(size=22, color=COLORS['text'], family='Arial'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='<b>Месяцы</b>',
            titlefont=dict(size=14, color=COLORS['text']),
            tickfont=dict(size=12, color=COLORS['text']),
            tickangle=-45,
            gridcolor=COLORS['grid'],
            linecolor=COLORS['accent2'],
            showgrid=True
        ),
        yaxis=dict(
            title='<b>Значения</b>',
            titlefont=dict(size=14, color=COLORS['text']),
            tickfont=dict(size=12, color=COLORS['text']),
            gridcolor=COLORS['grid'],
            linecolor=COLORS['accent2'],
            showgrid=True
        ),
        barmode=barmode,
        bargap=0.15,
        bargroupgap=0.1,
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['accent1'],
        font=dict(family='Arial, sans-serif'),
        hoverlabel=dict(
            bgcolor='white',
            font_size=12,
            font_family='Arial'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=COLORS['text']),
            bgcolor=COLORS['secondary'],
            bordercolor=COLORS['accent2'],
            borderwidth=1
        ),
        margin=dict(l=60, r=60, t=100, b=100)
    )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def generate_table_html(data):
    categories = data['Месяц']
    columns = [col for col in data.keys() if col != 'Месяц']

    table_html = '<table class="data-table" id="dataframe"><thead><tr>'

    table_html += '<th>Месяц</th>'
    for col in columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead><tbody>'

    for i, month in enumerate(categories):
        row_class = "even" if i % 2 == 0 else "odd"
        table_html += f'<tr class="{row_class}">'
        table_html += f'<td class="month-cell">{month}</td>'
        for col in columns:
            table_html += f'<td>{data[col][i]}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table>'
    return table_html


@app.route('/')
def index():
    return render_template('index.html', colors=COLORS)


@app.route('/generate_data')
def generate_data():

    data = generate_random_data()
    return jsonify({
        'success': True,
        'message': 'Данные успешно сгенерированы!',
        'data': data,
        'indicators': [col for col in data.keys() if col != 'Месяц']
    })


@app.route('/get_chart/<chart_type>')
def get_chart(chart_type):

    global current_data

    if not current_data:
        current_data = generate_random_data()

    graph_json = create_bar_chart(current_data, chart_type)
    table_html = generate_table_html(current_data)

    return jsonify({
        'graph_json': graph_json,
        'table_html': table_html,
        'chart_type': chart_type
    })


@app.route('/get_table')
def get_table():

    global current_data

    if not current_data:
        current_data = generate_random_data()

    table_html = generate_table_html(current_data)

    return jsonify({
        'table_html': table_html
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)