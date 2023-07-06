#THIS IS CURRENTLY A MOCK NOT FUNCTIONAL
import time

WEATHER_RESULTS_TXT = '../weather_results.txt'

def main():

    weather_results_file_object = open(WEATHER_RESULTS_TXT, 'r+')

    stupidCounter = 0

    while True: 
        stupidCounter += 1
        weather_results = weather_results_file_object.readline()
        if weather_results == 'go\n':
            weather_results_file_object.write('true\n')
        else:
            time.sleep(3)

        if stupidCounter == 30:
            break

           
if __name__ == "__main__":
    main()
