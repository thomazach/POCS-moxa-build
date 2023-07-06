
import time

# in order to run first run the weather analysis program
# as a background process, then start this, they should then
# communicate in order to produce the result of safe





WEATHER_RESULTS_TXT = '../weather_results.txt'
def main():
    # this is main

    while True: 
        weather_results_file_object = open(WEATHER_RESULTS_TXT, 'r+')

        weather_results_file_object.write('go\n') # tell weather do the thing
        time.sleep(1)
        weather_results = weather_results_file_object.readline()
        if weather_results == 'true\n':
            print('Safe to use')

            # when it is safe to go we need to send 
            break
        else:
            print('not safe')

            # Things aren't safe so the mount needs to be told to cry
            break



if __name__ == "__main__":
    main()
