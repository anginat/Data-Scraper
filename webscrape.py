from urllib.request import Request, urlopen
#from bs4 import BeautifulSoup
import json
import requests
import traceback
import time
#from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
import logging
import pandas
import tqdm

start = time.clock()

#Create and configure logger
logging.basicConfig(filename="webscrape_py_log.log", format='%(asctime)s %(message)s', filemode='w+')
#Creating an object
logger=logging.getLogger()
#Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

try:
	# Global object "data" to store JSON data
	#data = []
	
	# Utility function to create new JSON file locally
	def create_JSON_file(file_path, data):
		#file = open(file_path, 'w+', encoding="utf-8")
		with open(file_path, 'w+') as outfile:
			print("File object opened for: "+file_path)
			print("Data writing started at: "+file_path)
			json.dump(data, outfile)
		#file.write(str(data))
			print("Data writing finished at: "+file_path)
		#file.close()
			print("File object closed for: "+file_path)
		
	# Web Scraper funtion to scrape data for defined webpage link
	def web_scraper(data, page_no):
		for i in range(page_no):
			print("-------------------------------------------------------------------------------")
			logger.info("-------------------------------------------------------------------------------")
			pbar = tqdm.tqdm(total=100)
			loop_start_time = time.clock()
			# specify the url
			webpage_link = "https://www.myntra.com/web/v2/search/data/men-jeans?f=&p="+str(i+1)+"&rows=48"
			print("Web page link created: "+str(webpage_link))
			logger.info("Web page link created: "+str(webpage_link))
			# query the website and return the html to the variable ‘webpage’
			#webpage = urllib.request.urlopen(webpage_link)
			#proxies = {'http': 'http://103.14.232.30:8080'}
			req = Request(webpage_link, headers={'User-Agent': 'Mozilla/5.0'})
			#req.set_proxy('182.75.71.178:8080', 'http')
			response_webpage = urlopen(req).read().decode('utf-8')
			response_webpage = json.loads(response_webpage)
			products = response_webpage["data"]["results"]["products"]
			#print("Products JSON created for page: "+str(i+1))
			#logger.info("Products JSON created for page: "+str(i+1))
			if products:
				#print("Products added to list for page: "+str(i+1))
				#logger.info("Products added to list for page: "+str(i+1))
				#pbar2 = tqdm.tqdm(total=len(products))
				for j in range(len(products)):
					style_id = products[j]['styleid']
					best_price_link = "https://www.myntra.com/web/offers/"+str(style_id)
					#print("Best price link created: "+str(best_price_link))
					req = Request(best_price_link, headers={'User-Agent': 'Mozilla/5.0'})
					response_price_json = json.loads(urlopen(req).read().decode('utf-8'))
					products[j].update(response_price_json)
					#print(data[i]["bestPrice"]["price"]["discounted"])
				#pbar2.update()
				data.update(response_webpage)
				print("All Data including Best Price for "+str(len(products))+" products added to main data list for page: "+str(i+1))
				logger.info("All Data including Best Price for "+str(len(products))+" products added to main data list for page: "+str(i+1))
				#print(i+1)
			else:
				logger.error("!!!!!!!!!!!! All products are stored now. No More Data Available. !!!!!!!!!!!!!!!!")
				print("!!!!!!!!!!!! All products are stored now. No More Data Available. !!!!!!!!!!!!!!!!")
				break
			#print("All Products updated for page: "+str(i+1))
			print("Execution time taken for above loop = "+str(time.clock() - loop_start_time)+" seconds")
			pbar.update()
			print("-------------------------------------------------------------------------------")
		return data
	
	# Auxiliary function for ThreadPool (Not in Use)
	def foo(data):
		return web_scraper(data, range(4))
	
	# Main Driver function
	if __name__ == '__main__':
		
		manager = multiprocessing.Manager()
		results = manager.dict()
		
		processes = []
		page_no = [0,1,2,3,4]
		cpus = multiprocessing.cpu_count()
		for cpu in range(cpus-2):
			process = multiprocessing.Process(target=web_scraper, args=(results, cpu))
			process.start()
			processes.append(process)
		
		for process in processes:
			process.join()
		
		
		'''
		pool = ThreadPool(4)
		data = {}
		results = pool.map(web_scraper, 1)
		pool.close()
		pool.join()
		# above pooling......below single call
		data = {}
		results = web_scraper(data)
		'''
		
		file_path = 'C:/Users/Alpha/Desktop/myntra_jeans_2.json'
		create_JSON_file(file_path, results.copy())
		#print(data[0]["data"]["results"]["products"][0]["bestPrice"]["price"]["discounted"])
		print("********************* Execution Successfully Finished *************************")
		print("Execution time: "+str(time.clock() - start)+" seconds")
		
		f = open("C:/Users/Alpha/Desktop/myntra_jeans_2.json", "r")
		f_data = f.read()
		json_data = json.loads(f_data)
		df = pandas.DataFrame([json_data])
		df.to_clipboard(index=False,header=False)
		print("Copied to clipboard")
		#print(format(json_data)[0]["data"]["results"]["products"][0]["bestPrice"]["price"]["discounted"])
		
except Exception as e:
	print("Exception occurred: "+str(e))
	traceback.print_exc()
	logger.exception("Exception occurred on main handler")
	raise
	print("Execution time after exception: "+str(time.clock() - start)+" seconds")