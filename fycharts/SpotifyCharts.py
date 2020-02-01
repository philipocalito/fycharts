import json
import threading

from queue import Queue

from .crawler_base import SpotifyChartsBase
from .compute_dates import returnDatesAndRegions
from .compute_dates import whatDates
from .log_config import logger
from .write_to_outputs import writeToCSV
from .write_to_outputs import writeToSQLTable

from .exceptions import FyChartsException



def validateFile(fileName):
	if(".csv" in fileName):
			file = fileName
			return file
	else:
		raise FyChartsException("ONLY CSV FILES ALLOWED!!!")

	

# Class definition
class SpotifyCharts(SpotifyChartsBase):
	def __init__(self):
		SpotifyChartsBase.__init__(self)
		self.csv_data_queue = Queue()
		self.db_data_queue = Queue()

	def __write_to_csv_from_queue(self, data_q):
		""" Reads a dataframe from the queue, then writes to CSV
		"""
		try:
			work = True
			while work:
				data = data_q.get(block = True)
				if data is None:
					work = False
					return
				else:
					df = data["df"]
					j = data["j"]
					file = data["out_file"]

					writeToCSV(j, file, df)
		except Exception as e:
			raise RuntimeError(e)

	def __write_to_db_from_queue(self, data_q):
		""" Reads a dataframe from the queue, then writes to SQL table
		"""
		try:
			work = True
			while work:
				data = data_q.get(block = True)
				if data is None:
					work = False
					return
				else:
					df = data["df"]
					conn = data["conn"]
					data_type = data["data_type"]

					writeToSQLTable(data_type, conn, df)
		except Exception as e:
			raise RuntimeError(e)

	def top200Weekly(self, output_file = None, output_db = None, start = None, end = None, region = None):
		"""Write to file the charts data for top 200 weekly
		Params:
			output_file - Name of CSV file to write the data to
			output_db - A connection object to any database supported by SQLAlchemy (https://docs.sqlalchemy.org/en/13/dialects/#included-dialects)
			start - Start of range (YYYY-MM-DD) as string
			end - End of range (YYYY-MM-DD) as string
			region - Region (or a list of regions) to get data for

		* Any parameter passed as None, means ALL data since the beginning up to now
		"""
		file = validateFile(output_file)
		data = returnDatesAndRegions(start, end, region, isWeekly = True, isViral = False)

		dates = data["dates"]
		regions = data["region"]

		if(output_file is not None):
			a_thread = threading.Thread(target = self.__write_to_csv_from_queue, args = (self.csv_data_queue,))
			a_thread.start()
		if(output_db is not None):
			adb_thread = threading.Thread(target = self.__write_to_db_from_queue, args = (self.db_data_queue,))
			adb_thread.start()

		if(output_file is None and output_db is None):
			raise FyChartsException("Please provide at least one output destination")

		j = 0
		while(j < len(dates)):
			if((j + 1) == len(dates)): 
				break
			theRange = dates[j]+"--"+dates[j+1]

			k = j
			for region in regions:
				df = super().helperTop200Weekly(theRange, region)
				if(output_file is not None):
					dict_for_csv = {"df": df, "out_file": file, "j": k}
					self.csv_data_queue.put(dict_for_csv)
				if(output_db is not None):
					dict_for_db = {"df": df, "conn": output_db, "data_type": "top200Weekly"}
					self.db_data_queue.put(dict_for_db)

				k = k + 1
			j = j + 1
		self.csv_data_queue.put(None)
		self.db_data_queue.put(None)

	def top200Daily(self, output_file = None, output_db = None, start = None, end = None, region = None):
		"""Write to file the charts data for top 200 daily
		Params:
			output_file - Name of CSV file to write the data to
			output_db - A connection object to any database supported by SQLAlchemy (https://docs.sqlalchemy.org/en/13/dialects/#included-dialects
			start - Start of range (YYYY-MM-DD) as string
			end - End of range (YYYY-MM-DD) as string
			region - Region (or a list of regions) to get data for

		* Any parameter passed as None, means ALL data since the beginning up to now
		"""
		file = validateFile(output_file)
		data = returnDatesAndRegions(start, end, region, isWeekly = False, isViral = False)

		dates = data["dates"]
		regions = data["region"]

		if(output_file is not None):
			b_thread = threading.Thread(target = self.__write_to_csv_from_queue, args = (self.csv_data_queue,))
			b_thread.start()
		if(output_db is not None):
			bdb_thread = threading.Thread(target = self.__write_to_db_from_queue, args = (self.db_data_queue,))
			bdb_thread.start()

		if(output_file is None and output_db is None):
			raise FyChartsException("Please provide at least one output destination")

		j = 0
		while(j < len(dates)):
			theRange = dates[j]

			k = j
			for region in regions:
				df = super().helperTop200Daily(theRange, region)
				if(output_file is not None):
					dict_for_csv = {"df": df, "out_file": file, "j": k}
					self.csv_data_queue.put(dict_for_csv)
				if(output_db is not None):
					dict_for_db = {"df": df, "conn": output_db, "data_type": "top200Daily"}
					self.db_data_queue.put(dict_for_db)
				k = k + 1

			j = j + 1
		self.csv_data_queue.put(None)
		self.db_data_queue.put(None)

	def viral50Weekly(self, output_file = None, output_db = None, start = None, end = None, region = None):
		"""Write to file the charts data for viral 50 weekly
		Params:
			output_file - Name of CSV file to write the data to
			output_db - A connection object to any database supported by SQLAlchemy (https://docs.sqlalchemy.org/en/13/dialects/#included-dialects
			start - Start of range (YYYY-MM-DD) as string
			end - End of range (YYYY-MM-DD) as string
			region - Region (or a list of regions) to get data for

		* Any parameter passed as None, means ALL data since the beginning up to now
		"""
		file = validateFile(output_file)
		data = returnDatesAndRegions(start, end, region, isWeekly = True, isViral = True)

		dates = data["dates"]
		regions = data["region"]

		if(output_file is not None):
			c_thread = threading.Thread(target = self.__write_to_csv_from_queue, args = (self.csv_data_queue,))
			c_thread.start()
		if(output_db is not None):
			cdb_thread = threading.Thread(target = self.__write_to_db_from_queue, args = (self.db_data_queue,))
			cdb_thread.start()

		if(output_file is None and output_db is None):
			raise FyChartsException("Please provide at least one output destination")

		j = 0
		while(j < len(dates)):
			if((j) == len(dates)): 
				break
			theRange = dates[j]+"--"+dates[j]

			k = j
			for region in regions:
				df = super().helperViral50Weekly(theRange, region)
				if(output_file is not None):
					dict_for_csv = {"df": df, "out_file": file, "j": k}
					self.csv_data_queue.put(dict_for_csv)
				if(output_db is not None):
					dict_for_db = {"df": df, "conn": output_db, "data_type": "viral50Weekly"}
					self.db_data_queue.put(dict_for_db)
				k = k + 1

			j = j + 1
		self.csv_data_queue.put(None)
		self.db_data_queue.put(None)

	def viral50Daily(self, output_file = None, output_db = None, start = None, end = None, region = None):
		"""Write to file the charts data for viral 50 daily
		Params:
			output_file - Name of CSV file to write the data to
			output_db - A connection object to any database supported by SQLAlchemy (https://docs.sqlalchemy.org/en/13/dialects/#included-dialects
			start - Start of range (YYYY-MM-DD) as string
			end - End of range (YYYY-MM-DD) as string
			region - Region (or a list of regions) to get data for

		* Any parameter passed as None, means ALL data since the beginning up to now
		"""
		file = validateFile(output_file)
		data = returnDatesAndRegions(start, end, region, isWeekly = False, isViral = True)

		dates = data["dates"]
		regions = data["region"]

		if(output_file is not None):
			d_thread = threading.Thread(target = self.__write_to_csv_from_queue, args = (self.csv_data_queue,))
			d_thread.start()
		if(output_db is not None):
			ddb_thread = threading.Thread(target = self.__write_to_db_from_queue, args = (self.db_data_queue,))
			ddb_thread.start()

		if(output_file is None and output_db is None):
			raise FyChartsException("Please provide at least one output destination")

		j = 0
		while(j < len(dates)):
			theRange = dates[j]

			k = j
			for region in regions:
				df = super().helperViral50Daily(theRange, region)
				if(output_file is not None):
					dict_for_csv = {"df": df, "out_file": file, "j": k}
					self.csv_data_queue.put(dict_for_csv)
				if(output_db is not None):
					dict_for_db = {"df": df, "conn": output_db, "data_type": "viral50Daily"}
					self.db_data_queue.put(dict_for_db)

				k = k + 1

			j = j + 1
		self.csv_data_queue.put(None)
		self.db_data_queue.put(None)

	# ====== UTILITY FUNCTIONS ======
	def validDates(self, start, end, desired):
		""" Returns a table of valid dates from a start date to an end date provided, for the specific data desired
		Params:
			start - Start date of range (YYYY-MM-DD) as string
			end - End date of range (YYYY-MM-DD) as string
			desired - A string specifying the kind of data desired
				Accepts:
					* top200Daily
					* top200Weekly
					* viral50Daily
					* viral50Weekly
		"""
		theDates = whatDates(start, end, desired)
		print(json.dumps(theDates, indent = 4))


		


		






