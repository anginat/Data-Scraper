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
logging.basicConfig(filename="webscrape_py_log.log", format='%(asctime)s %(message)s', filemode='a')
#Creating an object
logger=logging.getLogger()
#Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

try:	
	# Utility function to create new JSON file locally
	def create_JSON_file(file_path, data):
		#file = open(file_path, 'w+', encoding="utf-8")
		with open(file_path, 'w+') as outfile:
			print("File object opened for: "+file_path)
			print("Data writing started at: "+file_path)
			json.dump(data, outfile)
			print("Data writing finished at: "+file_path)
			print("File object closed for: "+file_path)
		
	# Web Scraper function to scrape data for defined webpage link
	def web_scraper(data, product_link, start_index, end_index):
		for i in range(start_index, end_index):
			print("-------------------------------------------------------------------------------")
			logger.info("-------------------------------------------------------------------------------")
			pbar = tqdm.tqdm(total=100)
			loop_start_time = time.clock()
			# specify the url
			webpage_link = "https://www.myntra.com/web/v2/search/data/"+product_link+"?f=&p="+str(i+1)+"&rows=20"
			print("Web page link created: "+str(webpage_link))
			logger.info("Web page link created: "+str(webpage_link))
			#webpage = urllib.request.urlopen(webpage_link)
			#proxies = {'http': 'http://103.14.232.30:8080'}
			req = Request(webpage_link, headers={'User-Agent': 'Mozilla/5.0'})
			#req.set_proxy('182.75.71.178:8080', 'http')
			# query the website and return the JSON to the object "response_webpage"
			response_webpage = urlopen(req).read().decode('utf-8')
			# JSON parsing
			response_webpage = json.loads(response_webpage)
			# "products" object created to update "bestPrices" later into it
			products = response_webpage["data"]["results"]["products"]
			print("Products JSON created for page: "+str(i+1))
			logger.info("Products JSON created for page: "+str(i+1))
			# checks if products are available in the "response_webpage" object or not
			if products:
				#print("Products added to list for page: "+str(i+1))
				#logger.info("Products added to list for page: "+str(i+1))
				#pbar2 = tqdm.tqdm(total=len(products))
				#data.update(response_webpage)
				# iterate through all the products to update "bestPrices" to corresponding "styleID"
				for j in range(len(products)):
					style_id = products[j]['styleid']
					best_price_link = "https://www.myntra.com/web/offers/"+str(style_id)
					#print("Best price link created: "+str(best_price_link))
					req = Request(best_price_link, headers={'User-Agent': 'Mozilla/5.0'})
					response_price_json = json.loads(urlopen(req).read().decode('utf-8'))
					# "bestPrice" is added to product being iterated
					products[j].update(response_price_json)
					#print(data[i]["bestPrice"]["price"]["discounted"])
				#pbar2.update()
				# finally "Data" is added as JSON in the list
				data.append(response_webpage)
				print("All Data including Best Price for "+str(len(products))+" products added to main data list for page: "+str(i+1))
				logger.info("All Data including Best Price for "+str(len(products))+" products added to main data list for page: "+str(i+1))
				#print(i+1)
			else:
				logger.error("!!!!!!!!!!!! All products are stored now. No More Data Available. !!!!!!!!!!!!!!!!")
				print("!!!!!!!!!!!! All products are stored now. No More Data Available. !!!!!!!!!!!!!!!!")
				break
			#print("All Products updated for page: "+str(i+1))
			print("Execution time taken for above loop = "+str(time.clock() - loop_start_time)+" seconds")
			pbar.update(100)
			print("-------------------------------------------------------------------------------")
		#return data
		
	# Main Driver function
	if __name__ == '__main__':
	
		product_link = ["mens-jeans"]
		product_loop_limit = [2]
		start_index = 0
		end_index = (product_loop_limit[0] // cpus) + 1
		
		# =========== Multiprocessing starts here ==========
		manager = multiprocessing.Manager()
		result = manager.list()
		processes = []
		cpus = multiprocessing.cpu_count()
		
		for cpu in range(cpus):
			process = multiprocessing.Process(target=web_scraper, args=(result, product_link[0], start_index, end_index))
			process.start()
			print("Process Created - "+format(process.name))
			processes.append(process)
			start_index = end_index
			end_index += end_index
			if start_index >= product_loop_limit[0]:
				#print("start_index ========= "+format(start_index))
				break
		
		for process in processes:
			print("Process joining ==== "+format(process))
			process.join()
		# =========== Multiprocessing ends here ===========
		
		#web_scraper(product_link[0], 0, 2)
		print("Length of products is ----------------> "+format(len(result[0]["data"]["results"]["products"])))
		print("Length of products is ----------------> "+format(len(result[1]["data"]["results"]["products"])))
		
		''' # pooling didn't work properly
		pool = ThreadPool(4)
		data = {}
		results = pool.map(web_scraper, 1)
		pool.close()
		pool.join()
		# above pooling......below single call
		data = {}
		results = web_scraper(data)
		'''
		
		results = [x for x in result] # converts ListProxy into pure python list
		file_path = 'C:/Users/Alpha/Desktop/'+product_link[0]+'.json'
		create_JSON_file(file_path, results)
		#print(data[0]["data"]["results"]["products"][0]["bestPrice"]["price"]["discounted"])
		print("********************* Execution Successfully Finished *************************")
		print("Service Execution time: "+str(time.clock() - start)+" seconds")
		
		f = open("C:/Users/Alpha/Desktop/"+product_link[0]+".json", "r")
		f_data = f.read()
		json_data = json.loads(f_data)
		
except Exception as e:
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Exception occurred ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ")
	print(e)
	traceback.print_exc()
	logger.exception("Exception occurred on main handler")
	raise
	print("Service Execution time after exception: "+str(time.clock() - start)+" seconds")