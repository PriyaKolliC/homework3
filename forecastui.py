from flask import render_template, abort
from flask import Flask, request,redirect
from flask_restful import Resource, Api
from flask_restplus import Api, Resource, fields
from json import dumps
import csv, json, ast
import pandas as pd
from flask_api import status
from tempfile import NamedTemporaryFile
import os
import numpy as np
from datetime import datetime,timedelta
from dateutil.parser import parse

app = Flask(__name__)
api = Api(app,version='1.0', title='Sample API',
    description='Weather Forecast API',)
	
@app.route('/hmw3/weather/',methods=['GET'])
def Historical():
	return render_template('hmw3.html')


@api.route('/weather/historical/')
class Historical(Resource):
	def get(self):
		csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')

		fieldnames = ("DATE","TMAX","TMIN")
		reader = csv.DictReader( csvfile, fieldnames)
		next(reader)
		out = []
		for row in reader:
			input = row["DATE"]
			input_dict = {"DATE":input}
			out.append(input_dict)
		csvfile.close()
		#out = json.dumps(out)
		return out
	
	resource_fields = api.model('Resource', {
    'DATE': fields.String,
	'TMAX': fields.Float,
	'TMIN': fields.Float,
	})
	
	@api.expect(resource_fields)
	def post(self):
		data = json.loads(request.data)
		input_date = data['DATE']
		TMAX = data['TMAX']
		TMIN = data['TMIN']
		
		csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
		outputfile = open('/home/ubuntu/cchomework3/output.csv','w',newline='')	
		fieldnames = ("DATE","TMAX","TMIN")
		
		reader = csv.DictReader( csvfile, fieldnames)
		writer = csv.DictWriter(outputfile,fieldnames)
		header = next(reader)
		writer.writerow(header)
		out = []
		exists = 0
		row_new = {}
		for row in reader:
			input = row["DATE"]
			if input == input_date:
				row["TMAX"] = TMAX
				row["TMIN"] = TMIN
				exists = 1
			row_new = {"DATE":row["DATE"],"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
			writer.writerow(row_new)
			
		outputfile.close()
		csvfile.close()
		##os.remove('/home/ubuntu/weatherui/dailyweather.csv')
		os.rename('/home/ubuntu/cchomework3/output.csv','/home/ubuntu/cchomework3/dailyweather.csv')
		if exists == 0:
			csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
			fieldnames = ("DATE","TMAX","TMIN")
			final_list = []
			reader = csv.DictReader( csvfile, fieldnames)
			header = next(reader)
			csvfile2 = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
			reader2 = csv.DictReader( csvfile2, fieldnames)
			header2 = next(reader2)
			check_point = 0
			for row in reader:
				if row["DATE"] < input_date:
					check_point = 0
					row = {"DATE":row["DATE"],"TMAX":row["TMAX"],"TMIN":row["TMIN"]}
					final_list.append(row)
					next(reader2)
				else:
					check_point = 1
					next(reader2)
					row2 = {"DATE":input_date,"TMAX":TMAX,"TMIN":TMIN}
					final_list.append(row2)
					row = {"DATE":row["DATE"],"TMAX":row["TMAX"],"TMIN":row["TMIN"]}
					final_list.append(row)
					for row in reader2:
						row = {"DATE":row["DATE"],"TMAX":row["TMAX"],"TMIN":row["TMIN"]}
						final_list.append(row)
					break
			if check_point == 0:
				row = {"DATE":input_date,"TMAX":TMAX,"TMIN":TMIN}
				final_list.append(row)
				
			with open('/home/ubuntu/cchomework3/dailyweather.csv','w',newline='') as add_file:
				print('file opened')
				writer = csv.DictWriter(add_file,fieldnames)
				writer.writerow(header)
				for i in range(0,len(final_list)):
					writer.writerow(final_list[i])
		
		input_dict = {"DATE":input_date}
		input_dict = {"DATE":input_date}
		return input_dict,status.HTTP_201_CREATED

@api.route('/weather/historical/<date_info>')
class Historical_Get_Date(Resource):
	def get(self,date_info):
		csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
		fieldnames = ("DATE","TMAX","TMIN")
		reader = csv.DictReader( csvfile, fieldnames)
		next(reader)
		out = []
		for row in reader:
			input = row["DATE"]
			if input == str(date_info):
				input_dict = {"DATE":input,"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
				print(input_dict)
				#input_dict = json.dumps(input_dict)
				return input_dict
		csvfile.close()
		return abort(404)

	def delete(self,date_info):
		print(date_info)
		csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
		outputfile = open('/home/ubuntu/cchomework3/output.csv','w',newline='')
		
		fieldnames = ("DATE","TMAX","TMIN")
		reader = csv.DictReader( csvfile, fieldnames)
		writer = csv.DictWriter(outputfile,fieldnames)
		
		header = next(reader)
		writer.writerow(header)
		out = []
		exists = 0
		row_new = {}
		for row in reader:
			input = row["DATE"]
			if input == date_info:
				exists = 1
			else:
				row_new = {"DATE":row["DATE"],"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
				writer.writerow(row_new)
			
		outputfile.close()
		csvfile.close()
		##os.remove('/home/ubuntu/weatherui/dailyweather.csv')
		os.rename('/home/ubuntu/cchomework3/output.csv','/home/ubuntu/cchomework3/dailyweather.csv')
		
		input_dict = {"DATE":date_info}
		#input_dict = json.dumps(input_dict)
		
		if exists == 0:
			return abort(404)
		else:	
			return input_dict

@api.route('/weather/forecast/<date_info>')
class Forecast(Resource):
	def get(self,date_info):
		csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
		fieldnames = ("DATE","TMAX","TMIN")
		
		reader = csv.DictReader( csvfile, fieldnames)
		header = next(reader)
		count = 0
		appended_row_count = 0
		exists = 0
		for row in reader:
			if row["DATE"] == date_info:
				count = 1
				exists = 1
			else:
				count = count + 1
		csvfile.close()
		
		csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
		reader = csv.DictReader( csvfile, fieldnames)
		header = next(reader)
		forecast_list=[]
		
		if exists == 1:
			if count < 7:
				print('date exists and count < 7')
				for row in reader:
					if row["DATE"] == date_info:
						row = {"DATE":row["DATE"],"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
						forecast_list.append(row)
						appended_row_count = appended_row_count + 1
						while appended_row_count < count:
							row = next(reader)
							row = {"DATE":row["DATE"],"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
							forecast_list.append(row)
							date_info = row["DATE"]
							appended_row_count = appended_row_count + 1
	
				extra_dates = get_extra_dates(date_info,7-appended_row_count)
				
				
				for i in range(0,7-appended_row_count):
					icsvfile = open('/home/ubuntu/cchomework3/dailyweather.csv', 'r')
					ireader = csv.DictReader( icsvfile, fieldnames)
					iheader = next(ireader)
					date_count = 0
					t_max = 0
					t_min = 0
					print("date " + str(i+1))
					for row in ireader:
						if row["DATE"][4:] == (extra_dates[i])[4:]:
							#print("TMAX " + row["TMAX"])
							#print("TMIN " + row["TMIN"])
							
							t_max = t_max + float(row["TMAX"])
							t_min = t_min + float(row["TMIN"])
							date_count = date_count + 1
					row = {"DATE":extra_dates[i],"TMAX":round(t_max/date_count,2),"TMIN":round(t_min/date_count,2)}
					forecast_list.append(row)
				print(forecast_list)
				
			else:
				print('date exists and count > 7')
				count = 7
				for row in reader:
					if row["DATE"] == date_info:
						row = {"DATE":row["DATE"],"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
						forecast_list.append(row)
						count = count - 1
						while count > 0:
							row = next(reader)
							row = {"DATE":row["DATE"],"TMAX":float(row["TMAX"]),"TMIN":float(row["TMIN"])}
							forecast_list.append(row)
							count = count - 1 
		else:
			print('date doesnt exist')
			extra_dates = [date_info]
			extra_dates.extend(get_extra_dates(date_info,6))
			t_max = 0
			t_min = 0
			date_count = 0
			for i in range(0,len(extra_dates)):
				t_max = 0
				t_min = 0
				date_count = 0
				csvfile = open('/home/ubuntu/cchomework3/dailyweather.csv','r')
				reader = csv.DictReader(csvfile,fieldnames)
				header = next(reader)
				for row in reader:
					if row["DATE"][4:] == (extra_dates[i])[4:]:
						t_max = t_max + float(row["TMAX"])
						t_min = t_min + float(row["TMIN"])
						date_count = date_count + 1
				row = {"DATE":extra_dates[i],"TMAX":round(t_max/date_count,2),"TMIN":round(t_min/date_count,2)}
				forecast_list.append(row)
			print(forecast_list)
				
		return forecast_list
def get_extra_dates(date_info,count):
	year = date_info[0:4]
	month = date_info[4:6]
	day = date_info[6:8]
	first_date = year + '-' + month + '-' + day
	first_date = datetime.strptime(first_date, '%Y-%m-%d').date()
	extra_dates=[]
	next_date = first_date
	
	for i in range(0,count):
		next_date = next_date + timedelta(days=1)
		extra_dates.append((str(next_date)).replace('-',''))
	return extra_dates
	
if __name__ == '__main__':
    app.run(debug=True)
