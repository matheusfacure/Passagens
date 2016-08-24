from skyscanner.skyscanner import Flights

flights_service = Flights('APIKey')
result = flights_service.get_result(
	country='BR',
	currency='BRL',
	locale='pt-BR',
	originplace='GIG-sky',
	destinationplace='GRU-sky',
	outbounddate='2016-09-13',
	inbounddate='2016-09-20',
	adults=1).parsed

print(result)