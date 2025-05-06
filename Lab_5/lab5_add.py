import numpy as np
from scipy.signal import butter, filtfilt
import dash
from dash import Dash, html, dcc
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly.graph_objs as go

T = 10.0        
Fs0 = 100.0      
t = np.arange(0, T, 1/Fs0)

initialAmplitude = 1.0
initialFrequency = 1.0
initialPhase = 0.0
initialNoiseMean = 0.0
initialNoiseCovariance = 0.1
initialCutoffFrequency = 1.0
initialFilterOrder = 5
initialFilterType = 'Butterworth'

def generate_harmonic(t, A, f, phi):
    return A * np.sin(2*np.pi*f*t + phi)

def generate_noise(n, mean, var):
    return np.random.normal(mean, np.sqrt(var), size=n)

def butter_lowpass(sig, cutoff, fs, order):
    b, a = butter(order, cutoff/(0.5*fs), btype='low')
    return filtfilt(b, a, sig)

def custom_ma(sig, window):
    w = int(window)
    if w < 1:
        return sig
    kernel = np.ones(w) / w
    return np.convolve(sig, kernel, mode='same')

app = Dash(__name__)
app.title = "Lab5: Harmonic + Noise + Filtering"

app.layout = html.Div(
    style={'display': 'flex', 'height': '100vh', 'fontFamily': 'Arial, sans-serif'},
    children=[
        html.Div(
            style={
                'flex': '0 0 300px',
                'padding': '20px',
                'borderRight': '1px solid #ddd',
                'overflowY': 'auto'
            },
            children=[
                html.H5("Controls", style={'marginBottom': '20px'}),

                html.Label("Amplitude"),
                daq.Slider(
                    id='A', min=0.1, max=10, step=0.1, value=initialAmplitude,
                    handleLabel={"showCurrentValue": True, "label": "A"},
                    size=280, color="#0074D9", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Frequency (Hz)"),
                daq.Slider(
                    id='f', min=0.1, max=10, step=0.1, value=initialFrequency,
                    handleLabel={"showCurrentValue": True, "label": "f"},
                    size=280, color="#FF4136", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Phase (rad)"),
                daq.Slider(
                    id='phi', min=0, max=2*np.pi, step=0.1, value=initialPhase,
                    handleLabel={"showCurrentValue": True, "label": "φ"},
                    size=280, color="#2ECC40", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Noise mean"),
                daq.Slider(
                    id='noise_mean', min=-1, max=1, step=0.1, value=initialNoiseMean,
                    handleLabel={"showCurrentValue": True, "label": "μ"},
                    size=280, color="#FF851B", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Noise variance"),
                daq.Slider(
                    id='noise_var', min=0, max=1, step=0.01, value=initialNoiseCovariance,
                    handleLabel={"showCurrentValue": True, "label": "σ²"},
                    size=280, color="#B10DC9", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Cutoff frequency (Hz)"),
                daq.Slider(
                    id='cutoff', min=0.1, max=5, step=0.1, value=initialCutoffFrequency,
                    handleLabel={"showCurrentValue": True, "label": "fc"},
                    size=280, color="#FFDC00", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Filter order"),
                daq.Slider(
                    id='order', min=1, max=15, step=1, value=initialFilterOrder,
                    handleLabel={"showCurrentValue": True, "label": "n"},
                    size=280, color="#001f3f", dots=False, marks={}
                ),
                html.Br(),

                html.Label("Filter type"),
                dcc.Dropdown(
                    id='filter_type',
                    options=[
                        {'label': 'Butterworth',   'value': 'Butterworth'},
                        {'label': 'Moving Average', 'value': 'MA'}
                    ],
                    value=initialFilterType,
                    clearable=False,
                    style={'marginBottom': '20px'}
                ),

                dcc.Checklist(
                    id='show_noise',
                    options=[{'label': 'Show Noise', 'value': 1}],
                    value=[1],
                    style={'marginBottom': '20px'}
                ),

                html.Button(
                    "Reset", id='reset-button', n_clicks=0,
                    style={
                        'width': '100%', 'padding': '10px',
                        'backgroundColor': '#0074D9', 'color': 'white',
                        'border': 'none', 'borderRadius': '4px',
                        'cursor': 'pointer', 'fontSize': '16px'
                    }
                )
            ]
        ),

        html.Div(
            style={'flex': '1', 'padding': '20px', 'overflowY': 'auto'},
            children=[
                dcc.Graph(id='signal-plot', style={'height': '45vh'}),
                dcc.Graph(id='filtered-plot', style={'height': '45vh'})
            ]
        )
    ]
)

@app.callback(
    [
        Output('signal-plot',    'figure'),
        Output('filtered-plot',  'figure')
    ],
    [
        Input('A',            'value'),
        Input('f',            'value'),
        Input('phi',          'value'),
        Input('noise_mean',   'value'),
        Input('noise_var',    'value'),
        Input('cutoff',       'value'),
        Input('order',        'value'),
        Input('show_noise',   'value'),
        Input('filter_type',  'value'),
    ]
)
def update_graph(A, f, phi, nm, nv, cutoff, order, show_noise, filter_type):
    clean = generate_harmonic(t, A, f, phi)
    noise = generate_noise(len(t), nm, nv)
    sig   = clean + noise if 1 in show_noise else clean

    if filter_type == 'Butterworth':
        filt = butter_lowpass(sig, cutoff, Fs0, order)
    else:
        filt = custom_ma(sig, window=order)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=t, y=clean, name='Clean',
                              line=dict(color='blue', width=2)))
    fig1.add_trace(go.Scatter(x=t, y=sig,  name='Noisy',
                              line=dict(color='red', width=1), opacity=0.6))
    fig1.update_layout(title="Harmonic Signal + Noise",
                       xaxis_title="Time (s)", yaxis_title="Amplitude",
                       template="plotly_white")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=t, y=filt, name='Filtered',
                              line=dict(color='green', width=2)))
    fig2.update_layout(title=f"Filtered Output ({filter_type})",
                       xaxis_title="Time (s)", yaxis_title="Amplitude",
                       template="plotly_white")

    return fig1, fig2

@app.callback(
    [
        Output('A', 'value'),
        Output('f', 'value'),
        Output('phi', 'value'),
        Output('noise_mean', 'value'),
        Output('noise_var', 'value'),
        Output('cutoff', 'value'),
        Output('order', 'value'),
        Output('show_noise','value'),
        Output('filter_type','value'),
    ],
    Input('reset-button', 'n_clicks')
)
def reset_all(n_clicks):
    return [
        initialAmplitude,
        initialFrequency,
        initialPhase,
        initialNoiseMean,
        initialNoiseCovariance,
        initialCutoffFrequency,
        initialFilterOrder,
        [1],
        initialFilterType
    ]

if __name__ == '__main__':
    app.run(debug=True)
