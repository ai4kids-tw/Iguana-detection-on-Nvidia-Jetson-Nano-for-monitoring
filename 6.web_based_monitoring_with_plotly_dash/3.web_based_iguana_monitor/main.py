#!/usr/bin/env python3

################################################################################
# Copyright (c) 2021, AI4Kids CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

import time
import logging

import cv2
from flask import Flask, Response
import dash
import plotly
import plotly.graph_objs as go
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import mysql.connector
import pandas as pd
from configparser import ConfigParser

from layout import get_html_body
from exceptions import (RtspConfigFileNotFoundError,
                        DatabaseConfigFileNotFoundError)


class RtspStreamer(object):
    """This class is to receive video frames from Rtsp protocols in real-time.
    The video frames will be display on our web-based monitor.
    """

    def __init__(self, log_path, rtsp_addr):
        """
        Initialzeing function

        Parameters:
            log_path (string): The path where the log should be saved.
            rtsp_addr (string): The Rtsp address from Deepstream's output on Jetson Nano.
        """
        # Saveing log to file
        logging.basicConfig(handlers=[logging.FileHandler(log_path, 'w', 'utf-8')],
                            level=logging.DEBUG)
        try:
            self.stream = cv2.VideoCapture(rtsp_addr)
        except cv2.error as e:
            logging.error('Initializing RTSP stream error:' + e)

    def get_frame(self):
        """Return image frame from RTSP stream for monitoring purpose.
        If the given RTSP stream is not valid, return a default image instead."""
        if self.stream.isOpened():
            success, image = self.stream.read()
            if image is None:
                image = cv2.imread('assets/stream_not_found.png')
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        else:
            image = cv2.imread('assets/stream_not_found.png')
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()

def gen(streamer):
    """Generates image to display on monitor.

    Parameters:
        streamer (RtspStreamer): An instance of RtspStreamer.
    Outputs:
        frame: An image to show on monitor.
    """
    while True:
        frame = streamer.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def get_rtsp_address(path_config='./config/rtsp.ini'):
    rtsp_configure_parser = ConfigParser()
    is_config_file_existed = rtsp_configure_parser.read(path_config)
    if not is_config_file_existed:
        raise RtspConfigFileNotFoundError(path_config)
    return rtsp_configure_parser.get('GENERAL', 'RTSP_ADDR')

def fetch_graph_data(path_config='./config/db_server.ini'):
    db_configure_parser = ConfigParser()
    is_config_file_existed = db_configure_parser.read(path_config)
    if not is_config_file_existed:
        raise DatabaseConfigFileNotFoundError(path_config)

    connection = mysql.connector.connect(
        host=db_configure_parser.get('General', 'DB_HOST'),  # 主機名稱
        database=db_configure_parser.get('General', 'STR_DB'),  # 資料庫名稱
        user=db_configure_parser.get('OWNER', 'USR'),  # 帳號
        password=db_configure_parser.get('OWNER', 'PWD'))  # 密碼

    db_cursor = connection.cursor()
    db_cursor.execute('SELECT * FROM iguana_detection')
    table_rows = db_cursor.fetchall()
    df = pd.DataFrame(table_rows, columns=['local_time', 'num_iguana_detected'])
    return df

# Server
server = Flask(__name__)
@server.route('/video_feed')
def video_feed():
    global streamer
    return Response(gen(streamer),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# RTSP streamer
streamer = RtspStreamer('./log/test.log', get_rtsp_address())
# Dash app
app = dash.Dash(server=server,
                external_stylesheets=[dbc.themes.FLATLY])
# Setup for monitor's UI
app.layout = get_html_body(app)

# Callback function to show live-video on monitor
# when Rtsp stream is connected
@app.callback(Output('rtsp-streaming-process', 'children'),
              Input('rtsp-stream', 'complete'))
def update_streaming(complete):
    """Shows a progressbar for 5 seconds until the RTSP stream is fully prepared.
    """
    if not complete:
        time.sleep(5)

    return html.Img(id='rtsp-stream',
                    src="/video_feed",
                    style={'width': '100%'})


# Callback function to update graph every n intervals.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    # Get only the data in 60 seconds.
    df = fetch_graph_data().tail(60)
    X = df['local_time']
    Y = df['num_iguana_detected']
    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )
    return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                                yaxis=dict(range=[min(Y), max(Y)]), )}

if __name__ =='__main__':
    app.run_server()

