import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
from datetime import datetime



class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables = ['users', 'events', 'event_users', 'availabilities', 'event_invites']

        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset='utf8mb4',
                                        use_unicode=True
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id
    
    

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email, password):
        """
        Creates a new user if the email doesn't already exist.
        Returns a dict with success status and a message.
        """
        existing_user = self.query("SELECT * FROM users WHERE email = %s", (email,))
        if existing_user:
            return {'success': 0, 'message': 'User already exists'}

        encrypted_password = self.onewayEncrypt(password)
        try:
            self.query(
                "INSERT INTO users (email, password) VALUES (%s, %s)", 
                (email, encrypted_password)
            )
            return {'success': 1, 'message': 'User created successfully'}
        except Exception as e:
            return {'success': 0, 'message': f'Error creating user: {e}'}




    def authenticate(self, email='me@email.com', password='password') -> dict:
        """
        Authenticates a user by email and password.
        Returns a dict with success status, message, and optionally role.
        """
        user = self.query("SELECT * FROM users WHERE email = %s", (email,))
        if not user:
            return {'success': 0, 'message': 'User does not exist'}

        encrypted_password = self.onewayEncrypt(password)

        if user[0]['password'] == encrypted_password:
            return {
                'success': 1,
                'message': 'Authentication successful',
            }

        return {'success': 0, 'message': 'Incorrect password'}


    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

#######################################################################################
# EVENT RELATED
#######################################################################################

    def createEvent(self, title, created_by,
                    start_date, end_date,
                    day_start_time, day_end_time):
        """
        Insert a new event and auto‑add the creator to event_users.
        Returns {'success':1,'event_id':..} or {'success':0,'message':...}
        """
        try:
            eid = self.query(
                """INSERT INTO events
                (title, created_by, start_date, end_date,
                    day_start_time, day_end_time)
                VALUES (%s,%s,%s,%s,%s,%s)""",
                (title, created_by, start_date, end_date,
                day_start_time, day_end_time)
            )[0]['LAST_INSERT_ID()']
            self.addUserToEvent(created_by, eid)
            return {'success': 1, 'event_id': eid}
        except Exception as e:
            return {'success': 0, 'message': f'Error creating event: {e}'}


    def addUserToEvent(self, user_id, event_id):
        try:
            self.query(
                "INSERT IGNORE INTO event_users (user_id, event_id) VALUES (%s,%s)",
                (user_id, event_id)
            )
            return {'success': 1}
        except Exception as e:
            return {'success': 0, 'message': f'Error adding user to event: {e}'}


    def getUserEvents(self, user_id, email):
        return self.query("""
            SELECT  e.event_id,
                    e.title,
                    e.start_date,
                    e.end_date,
                    u.email AS creator_email          -- <-- bring creator back
            FROM events            e
            JOIN users             u  ON u.user_id = e.created_by
            LEFT JOIN event_users  eu ON eu.event_id = e.event_id AND eu.user_id = %s
            LEFT JOIN event_invites ei ON ei.event_id = e.event_id AND ei.email   = %s
            WHERE eu.user_id IS NOT NULL OR ei.email IS NOT NULL
            GROUP BY e.event_id
        """, (user_id, email))


    def getEventMeta(self, event_id):
        res = self.query("SELECT * FROM events WHERE event_id = %s", (event_id,))
        return res[0] if res else None


    def insertAvailabilities(self, rows):
        """
        rows = list of tuples (event_id, user_id, slot_start, avail_status)
        Uses ON DUPLICATE KEY UPDATE to overwrite existing rows.
        """
        if not rows:
            return
        placeholders = ','.join(['(%s,%s,%s,%s)'] * len(rows))
        flat = [item for row in rows for item in row]
        q = (f"INSERT INTO availabilities "
            f"(event_id,user_id,slot_start,avail_status) VALUES {placeholders} "
            f"ON DUPLICATE KEY UPDATE avail_status=VALUES(avail_status)")
        self.query(q, flat)


    def getEventAvailabilities(self, event_id):
        return self.query("""
            SELECT user_id, slot_start, avail_status
            FROM availabilities
            WHERE event_id = %s
        """, (event_id,))
