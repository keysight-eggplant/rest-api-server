from flask import Flask, request, jsonify, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
import json
from sqlite3 import OperationalError
from werkzeug.utils import secure_filename
import datetime

import time

#Create an engine for connecting to SQLite3.
#Assuming salaries.db is in your app root folder

e = create_engine('sqlite:///salaries.db')
f = create_engine('sqlite:///timings.db')

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"]
)
api = Api(app)

class Departments_Meta(Resource):
    def get(self):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        query = conn.execute("select distinct DEPARTMENT from salaries")
        return {'departments': [i[0] for i in query.cursor.fetchall()]}

class Departmental_Salary(Resource):
    def get(self, department_name):
        conn = e.connect()
        query = conn.execute("select * from salaries where Department='%s'"%department_name.upper())
        #Query the result and get cursor. Dumping that data to a JSON is looked by extension
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return result

class Add_Salary_Broken(Resource):
    # add salary
    def post(self):
        # parse request POST data
        args = request.get_json()
        print(str(args))

        args.len()

class Add_Salary(Resource):
    # add salary
    def post(self):
        # parse request POST data
        args = request.get_json()

        size = sum([len(x) for x in args.values()])

        if size >= 500:
            return jsonify(result="Data size limit reached. POST data must be less than 500 characters long.")
        
        columns = "', '".join(args)
        values = "', '".join(args.values())
        sql = "insert into salaries ('" + columns + "') values ('" + values + "')"
        print("final SQL: " + sql)
        conn = e.connect()
        try:
            query = conn.execute(sql)
            res = conn.execute('select max(id) from salaries')
            unique_id = list(res)[0][0]
            print(unique_id)
            return jsonify(result="success",
                           message="Successfully added salary information.",
                           name=args['Name'],
                           id=unique_id)
        except OperationalError:
            return jsonify(result="error",
                           message="Failed to add salary. You must specify 'Name', 'Job Titles', 'Department', 'Full or Part-Time', and 'Salary or Hourly' information.")

class Update_Salary(Resource):
    # update existing salary
    def post(self):
        # parse request POST data
        args = request.get_json()

        size = sum([len(x) for x in args.values()])

        if size >= 500:
            return jsonify(result="error",
                           message="Data size limit reached. POST data must be less than 500 characters long.")

        if 'id' not in args:
            return jsonify(result="error",
                           message="Must specify target 'id' in order to update salary information.")
        unique_id = args['id']

        sql = "UPDATE [salaries] SET "

        update_cols = []

        for arg in args:
            print(arg)
            if 'id' not in arg:
                update_cols.append("[" + arg + "] = '" + args[arg] + "'")

        sql += ", ".join(update_cols)
        sql += " WHERE [id] = " + unique_id
        
        print("Update SQL: " + sql)
        conn = e.connect()
        try:
            query = conn.execute(sql)
            print(query.rowcount)
            if query.rowcount == 1:
                return jsonify(result="success",
                               message="Successfully updated salary information.",
                               id=unique_id)
            else:
                return jsonify(result="error",
                               message="Failed to update salary. Are you sure the record ID exists?",
                               id=unique_id)
        except OperationalError:
            return jsonify(result="error",
                           message="Failed to update salary. You must specify 'Name', 'Job Titles', 'Department', 'Full or Part-Time', and 'Salary or Hourly' information.")

class Slow_Webservice(Resource):
    def get(self, wait_duration):
        now = datetime.datetime.now()
        print('request received: ' + str(now))
        time.sleep(wait_duration)
        now = datetime.datetime.now()
        print('finished waiting at: ' + str(now))
        return jsonify(result="success",
                       message="Waited for " + str(wait_duration) + " seconds.")

class Add_Response_Time(Resource):
    def post(self):
        # parse request POST data
        args = request.get_json()
        #print(str(args))

        for key,values in args.items():
            app_name = values['APP_NAME']
            response_time_ui = values['RESPONSE_TIME_UI']
            response_time_net = values['RESPONSE_TIME_NET']
            created_date = values['CREATED_DATE']
              
            sql = "insert into timings ('APP_NAME', 'RESPONSE_TIME_UI', 'RESPONSE_TIME_NET', 'CREATED_DATE') \
 values ('{0}','{1}','{2}','{3}')".format(app_name,response_time_ui,response_time_net,created_date)
            print("final SQL: " + sql)
        
            conn = f.connect()
            try:
                query = conn.execute(sql)
                #print("Successfully added response time information for '%s'" % app_name)
            except OperationalError:
                print("Failed to add response time. Double-check your POST data!")

class Get_Timing(Resource):
    def get(self, app_name):
        conn = f.connect()
        query = conn.execute("SELECT RESPONSE_TIME_UI,RESPONSE_TIME_NET FROM TIMINGS WHERE ID = \
(SELECT MAX(ID) FROM TIMINGS WHERE UPPER(APP_NAME) = '%s')" % app_name.upper())
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return result

class Save_File(Resource):
    def post(self):      
        f = request.files['file']
        f.save(secure_filename(f.filename))
        return jsonify(result="success",
                       message="file uploaded successfully.")

class Set_Cookie(Resource):
    def get(self):
        response = jsonify(result="success", message="I like cookies!")
        response.set_cookie('cookie_1', value='value_1')
        response.set_cookie('cookie_2', value='value_2')
        return response

api.add_resource(Add_Salary, '/add-salary')
api.add_resource(Update_Salary, '/update-salary')
api.add_resource(Add_Salary_Broken, '/add-salary-broken')
api.add_resource(Departmental_Salary, '/department/<string:department_name>')
api.add_resource(Departments_Meta, '/departments')
api.add_resource(Slow_Webservice, '/slow-response/<int:wait_duration>')
api.add_resource(Add_Response_Time, '/add-timing')
api.add_resource(Get_Timing, '/get-timing/<string:app_name>')
api.add_resource(Save_File, '/save-file')
api.add_resource(Set_Cookie, '/set-cookie')

if __name__ == '__main__':
     app.run(host='172.31.21.19', debug=True)
