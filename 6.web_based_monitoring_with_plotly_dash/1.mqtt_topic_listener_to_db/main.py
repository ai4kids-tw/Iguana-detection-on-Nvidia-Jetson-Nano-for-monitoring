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

import logging
import json

from configparser import ConfigParser
import paho.mqtt.client as mqtt
import mysql.connector

from exceptions import (MqttBrokerConfigFileNotFoundError,
                        DatabaseConfigFileNotFoundError)


class IguanaMqttMsgToDbSaver:
    """Iguana detection inference result mounting and saving to Database.

    This class defines the utilities to subscribe to iguana detection inference result sent to a Mqtt topic by a Jetson device,
    when iguana detection inference result are published on this topic, save the message to database for visualization use.

    Attributes:
        topic_subscribe (string): The topic on Mqtt broker that we keep listening to.
        mqtt_config (string): Path of the configures file that stores settings to coeenct to a Mqtt broker.
        mqtt_conn (string): The Mqtt client.
        db_config (string): Path of the configures file that stores settings to coeenct to a mySQL Database.
    """

    def __init__(
            self,
            log_path,
            topic_subscribe,
            path_mqtt_conn_config,
            path_db_conn_config):
        """This function initializes required components to:
         1) connect to a Mqtt broker and subscribe to a particular topic
         2) Connect to a Database to save message from a subscribed Mqtt topic

         Parameters:
            log_path (string): The path of log which stores the debugging info when running this program.

            topic_subscribe (string): The topic to subscribe to receive iguana detection inference result.

            path_mqtt_conn_config (string):
                The Mqtt broker configure. The file extension should be: <filename>.ini.

            path_db_conn_config (string):
                The Database configure. The file extension should be: <filename>.ini
         """

        # Saveing log to file
        logging.basicConfig(handlers=[logging.FileHandler(log_path, 'w', 'utf-8')],
                            level=logging.DEBUG)
        # The Mqtt topic to subscribe
        self.topic_subscribe = topic_subscribe
        is_all_set = False

        # Handle non-existed database configure-file exception
        try:
            # Read DB connection configs from file
            self.db_config = self.load_db_config_file(path_db_conn_config)
        except Exception as e:
            # Logging errors
            logging.error(
                'Database Configure file parsing error. ' +
                e.__str__())

        # Handle no db-connection exception
        try:
            # Build DB connection
            self.db_conn = self.get_db_connection()
        except Exception as e:
            # Logging errors
            logging.error('Database server connecting error. ' + e.__str__())

        # Handle non-existed mqtt configure-file exception
        try:
            # Read Mqtt connection configs from file
            self.mqtt_config = self.load_mqtt_config_file(
                path_mqtt_conn_config)
        except Exception as e:
            # Logging errors
            logging.error('Mqtt Configure file parsing error. ' + e.__str__())

        # Handle no mqtt-connection exception
        try:
            # Build mqtt broker connection, setup callback behaviors
            self.mqtt_conn = self.get_mqtt_broker_connection()
            is_all_set = True
        except Exception as e:
            logging.error('Mqtt server connecting error. ' + e.__str__())

        if is_all_set:
            self.mqtt_conn.loop_forever()

    def load_mqtt_config_file(self, path_mqtt_config):
        """
        Loading the configure from the .ini file.

        Parameters:
            path_mqtt_config (string): The Mqtt broker configure: <filename>.ini.
            such has the following format:
                [OWNER]
                MQTT_USER = your_user_name
                MQTT_PASSWORD = your_password
                [General]
                MQTT_HOST = host_ip_address
                MQTT_PORT = port
                MQTT_CLIENT_ID = your_client_id
                DATABASE_FILE = database_file_name
        Output:
            mqtt_configure_parser (ConfigParser): An object stores all the configures.
        """
        mqtt_configure_parser = ConfigParser()
        is_config_file_existed = mqtt_configure_parser.read(path_mqtt_config)
        if not is_config_file_existed:
            raise MqttBrokerConfigFileNotFoundError(path_mqtt_config)
        return mqtt_configure_parser

    def load_db_config_file(self, path_db_config):
        """
            Loading the configure from the .ini file.

            Parameters:
                path_mqtt_config (string): The Mqtt broker configure: <filename>.ini.
                such has the following format:
                    [OWNER]
                    USR=your_user_name
                    PWD=your_password
                    [General]
                    DB_HOST=host_ip_address
                    STR_DB=database_name
            Output:
                mqtt_configure_parser (ConfigParser): An object stores all the configures.
        """
        db_config_parser = ConfigParser()
        is_config_file_existed = db_config_parser.read(path_db_config)
        if not is_config_file_existed:
            raise DatabaseConfigFileNotFoundError(path_db_config)
        return db_config_parser

    def get_db_connection(self):
        """Use the configures read from the .ini file to build a database connection.
        """
        return mysql.connector.connect(
            host=self.db_config.get('General', 'DB_HOST'),
            database=self.db_config.get('General', 'STR_DB'),
            user=self.db_config.get('OWNER', 'USR'),
            password=self.db_config.get('OWNER', 'PWD'))

    def get_mqtt_broker_connection(self):
        """Use the configure read from the .ini file to build a database connection.
        """
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = self.subscribe_to_mqtt_topic
        mqtt_client.on_message = self.save_message_to_db
        mqtt_client.connect(self.mqtt_config.get('General', 'MQTT_HOST'),
                            int(self.mqtt_config.get('General', 'MQTT_PORT')),
                            60)
        return mqtt_client

    def subscribe_to_mqtt_topic(
            self,
            mqtt_client,
            user_data,
            flags,
            conn_result):
        """Subscribe to a Mqtt topic which publish the iguana detection inference result.
        """
        mqtt_client.subscribe(self.topic_subscribe)

    def message_extraction(self, payload):
        """Extract the messages from Mqtt topic which was plain text.
        Pamameters:
        Output:
            local_time (string): The time when the mqtt message was sent.
            camera_id (string): The device which sent the inference result.
            num_iguana_detected (string): The number of iguanas detected.
            coords (string): The locations of iguanas in the camera frame.
        """
        message_dict = json.loads(payload)
        local_time = message_dict['local_time']
        num_iguana_detected = message_dict['0']
        return local_time, num_iguana_detected

    def insert_into_db(
            self,
            local_time,
            num_iguana_detected):
        cursor = None
        try:
            #  Save input MQTT message to DB
            cursor = self.db_conn.cursor()
            sql = 'INSERT INTO {table} '.format(table=self.db_config.get('General', 'TABLE'))
            sql += '(local_time, num_iguana_detected) VALUES (%s, %s)'
            val = (local_time, str(num_iguana_detected))
            cursor.execute(sql, val)
            self.db_conn.commit()

        except Exception as e:
            # Logging errors
            logging.error('Error saving data to database: ' + e)

        finally:
            if cursor:
                cursor.close()

    def save_message_to_db(self, mqtt_client, user_data, message):
        """Extract information from the messages and save them to database.
        Parameters:
            mqtt_client: The client is the client object, and is useful when you have multiple clients that are publishing data.
            user_data: The userdata is user defined data which isn’t normally used.
            message (string): The iguana detection inference result in plain text.
        Outputs:

        """
        payload = message.payload.decode('utf-8')
        local_time, num_iguana_detected = self.message_extraction(payload)
        self.insert_into_db(
            local_time, num_iguana_detected)


if __name__ == '__main__':
    test = IguanaMqttMsgToDbSaver('./log/test.log',
                                  'iguana_detection',
                                  './config/mqtt_server.ini',
                                  './config/db_server.ini')
