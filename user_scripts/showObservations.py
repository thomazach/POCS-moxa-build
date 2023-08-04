#!/usr/bin/python3

# TODO: make function
def main(args):

    if args.showAll:
        queue = obs_scheduler.getTargetQueue()
        while queue != []:
            print(obs_scheduler.heapq.heappop(queue))
    elif args.index:
        observationList = obs_scheduler.getTargetList()
        observationList.sort()
        print(observationList[args.index])
    else:
        queue = obs_scheduler.getTargetQueue()
        counter = 0
        while queue != [] and counter < 10:
            print(obs_scheduler.heapq.heappop(queue))
            counter += 1

if __name__ == "__main__":

    import os
    import sys 
    sys.path.append(os.getcwd())

    import argparse
    parser = argparse.ArgumentParser(description='Shows list of observations')
    observationsAmount = parser.add_mutually_exclusive_group()
    observationsAmount.add_argument('--showAll', required=False, action='store_true', help='Whether or not to show all observations. Default is first 10')
    observationsAmount.add_argument('--index', metavar='###', required=False, help='Shows observation at given index')

    args = parser.parse_args()
    from observational_scheduler import obs_scheduler
    main()