#!/usr/bin/python3

class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main(args):

    conf_files = os.path.realpath(__file__).replace('/user_scripts/schedule.py', '/conf_files')

    yesOrNo = lambda x: x == 'y' or x == 'Y' or x == 'yes' or x == 'Yes'

    def edit_schedule(schedule):
        # Coded quickly, improvements welcome
        # If the user inputs an invalid setting this kicks them out of the command and doesnt let them continue editing

        settingType = {'user_note': str,'priority': int, 'ra': str, 'dec': str, 'cmd': str,
                       'take_images': bool, 'num_captures': int, 'exposure_time': int}

        response = 'y'
        while True:
            response = input(bcolors.WARNING + "Would you like to edit a target? (y/n) " + bcolors.ENDC)
            if yesOrNo(response):
                print("List of targets in this schedule:")
                for target in schedule.keys():
                    print(bcolors.OKCYAN + target + bcolors.ENDC)
                targetToEdit = input(f"{bcolors.WARNING}What target do you want to edit? {bcolors.ENDC}")
                if any(validTarget == targetToEdit for validTarget in schedule.keys()):
                    print(f"List of settings for {targetToEdit}:")
                    for setting in schedule[targetToEdit].keys():
                        print(bcolors.OKCYAN + setting + bcolors.ENDC)
                    settingToEdit = input(bcolors.WARNING + "What setting do you want to change? " + bcolors.ENDC)
                    if any(validSetting == settingToEdit for validSetting in schedule[targetToEdit]):
                        if settingToEdit == 'primary_cam' or settingToEdit == 'secondary_cam':
                            print(f"List of {settingToEdit} settings:")
                            for setting in schedule[targetToEdit][settingToEdit].keys():
                                print(bcolors.OKCYAN + setting + bcolors.ENDC)
                            childSetting = input(bcolors.WARNING + "What setting do you want to change? " + bcolors.ENDC)
                            if any(validSetting == childSetting for validSetting in schedule[targetToEdit][settingToEdit].keys()):
                                childArg = _betterInput(f"{bcolors.WARNING}What value would you like to change {bcolors.OKCYAN}{childSetting}{bcolors.WARNING} to? {bcolors.ENDC}", settingType[childSetting])
                                schedule[targetToEdit][settingToEdit][childSetting] = childArg
                        else:
                            arg = _betterInput(f"{bcolors.WARNING}What value would you like to change {bcolors.OKCYAN}{settingToEdit}{bcolors.WARNING} to? {bcolors.ENDC}", settingType[settingToEdit]) 
                            schedule[targetToEdit][settingToEdit] = arg
        
            else:
                break
        
        response = 'y'
        while True:
            response = yesOrNo(input(bcolors.WARNING + "Do you want to add another target? [y/n]: " + bcolors.ENDC))  
            if response == True:
                name = str(input(f'{bcolors.WARNING}Name of the observation: {bcolors.ENDC}'))
                schedule[name] = makeObservationDict()
            
            else:
                break
        
        return schedule

    def _betterInput(prompt, Type = str, default = None):

        result = None
        while result == None:
            userInput = input(bcolors.WARNING + prompt + bcolors.ENDC) or default
            if userInput:
                try:
                    result = Type(userInput)
                except TypeError as error:
                    print(bcolors.FAIL + '=INVALID= Your input was not of type ' + bcolors.ENDC, Type)
                    userInput = None
                except Exception as error:
                    print(bcolors.FAIL + '=ERROR= ' + bcolors.ENDC, error)
                    userInput = None
        return result

    def makeObservationDict():

        #TODO: Handle bad inputs

        def _makeCameraArr():
            camera = {}
            camera['num_captures'] = None
            camera['exposure_time'] = None
            camera['take_images'] = yesOrNo(input(bcolors.WARNING + 'Do you want this camera to take images [y/n]: ' + bcolors.ENDC))
            if camera['take_images']:
                camera['num_captures'] = _betterInput('Enter # of images to capture: ', Type=int, default=1)
                camera['exposure_time'] = _betterInput('Enter exposure time per image in seconds: ', Type=int, default=1)
            return camera

        note = _betterInput('Enter user note [leave blank if none]: ', default='None')
        priority = _betterInput('Input the priority of the observation as a positive whole number: ', Type=int, default=0)
        ra = _betterInput('Input the ra in hours minutes seconds (00 42 44): ', default='00 42 44')
        dec = _betterInput('Input the dec in degrees minutes seconds (-41 16 09): ', default='+41 16 09')
        cmd = 'slew to target'
        print('Primary Camera Settings: \n')
        primaryCam = _makeCameraArr()
        print('Secondary Camera Settings: \n')
        secondaryCam = _makeCameraArr()
        attributes = {}
        attributes['user_note'] = note
        attributes['priority'] = priority
        attributes['ra'] = ra
        attributes['dec'] = dec
        attributes['cmd'] = cmd
        attributes['primary_cam'] = primaryCam
        attributes['secondary_cam'] = secondaryCam
        return attributes

    if args.show_active_observation:
        with open(f"{conf_files}/settings.yaml", "r") as f:
            settings = yaml.safe_load(f)
        activeFileName = settings["TARGET_FILE"]
        with open(f"{conf_files}/targets/{activeFileName}") as f:
            activeSchedule = yaml.safe_load(f)

        print("---------------   Summary of active schedule   ---------------")
        print(f"File name: {bcolors.OKGREEN}{activeFileName}{bcolors.ENDC}              Number of targets: {bcolors.OKGREEN}{len(activeSchedule.keys())}{bcolors.ENDC}")
        print("Target names:")
        for name in activeSchedule.keys():
            print(f"{bcolors.OKCYAN}{name}{bcolors.ENDC}")
        
        while True:
            doDetails = input(f"{bcolors.WARNING}List detailed information about a target? (y/n) {bcolors.ENDC}")
            if yesOrNo(doDetails):
                targetName = input(f"{bcolors.WARNING}Enter the name of the target: {bcolors.ENDC}")
                if any(targets in targetName for targets in activeSchedule.keys()):
                    print(f"Notes: {bcolors.OKBLUE}{activeSchedule[targetName]['user_note']}{bcolors.ENDC}")
                    print(f"Priority: {bcolors.OKBLUE}{activeSchedule[targetName]['priority']}{bcolors.ENDC}")
                    print(f"Position RA/DEC: {bcolors.OKBLUE}{activeSchedule[targetName]['ra']}   {activeSchedule[targetName]['dec']}{bcolors.ENDC}")
                    print("Primary Camera Settings:")
                    for setting in activeSchedule[targetName]['primary_cam'].keys():
                        print(f"{setting}: {bcolors.OKBLUE}{activeSchedule[targetName]['primary_cam'][setting]}{bcolors.ENDC}")
                    print("Secondary Camera Settings:")
                    for setting in activeSchedule[targetName]['secondary_cam'].keys():
                        print(f"{setting}: {bcolors.OKBLUE}{activeSchedule[targetName]['secondary_cam'][setting]}{bcolors.ENDC}")
            else:
                break
    
    if args.list_target_files:
        print("Available schedule files:" + bcolors.OKCYAN)
        os.system(f'cd {conf_files}/targets; ls *.yaml')
        print(bcolors.ENDC, end='')

    if args.select:
        file = args.select[0].replace(' ', '')
        if os.path.isfile(f"{conf_files}/targets/{file}"):
            try:
                with open(f"{conf_files}/settings.yaml", "r") as f:
                    settings = yaml.safe_load(f)
                settings['TARGET_FILE'] = args.select[0].replace(' ', '')
                with open(f"{conf_files}/settings.yaml", "w") as f:
                    yaml.dump(settings, f)

            except Exception as error:
                print(f"{bcolors.FAIL}=ERROR={bcolors.ENDC}", error)
        else:
            print(f"{bcolors.FAIL}=ERROR= The file name {bcolors.OKCYAN}{file}{bcolors.FAIL} isn't a file.")
    
    if args.new:

        if ".yaml" not in args.new[0]:
            print(f"{bcolors.FAIL}=ERROR= Specified file name must have suffix '.yaml'{bcolors.ENDC}")
        else:
            filePath = f"{conf_files}/targets/{args.new[0].replace(' ', '')}"
            os.system(f"touch {filePath}")

            keepGettingObservations = True
            observationsDict = {}
            while keepGettingObservations:
                name = str(input(f'{bcolors.WARNING}Name of the observation: {bcolors.ENDC}'))
                attributes = makeObservationDict()
                observationsDict[name] = attributes
                keepGettingObservations = yesOrNo(input(f'{bcolors.WARNING}Add another target? [y/n]: {bcolors.ENDC}'))

            editRequest = yesOrNo(input(f'{bcolors.WARNING}Edit previous targets? [y/n]: {bcolors.ENDC}'))
            if editRequest == True:
                observationsDict = edit_schedule(observationsDict)
            
            with open(filePath, "w") as f:
                yaml.dump(observationsDict, f)

    if args.edit:

        try:
            with open(f"{conf_files}/targets/{args.edit[0].replace(' ', '')}", "r") as f:
                schedule = yaml.safe_load(f)
        except Exception as e:
            print(bcolors.FAIL + "=ERROR= " + bcolors.ENDC, e)

        schedule = edit_schedule(schedule)
        with open(f"{conf_files}/targets/{args.edit[0].replace(' ', '')}", "w") as f:
            yaml.dump(schedule, f)

    if args.delete:
        confirm = yesOrNo(input(f"{bcolors.FAIL}Are you sure you want to permenantly delete {args.delete[0]}? [y/n]: {bcolors.ENDC}"))
        if confirm == True:
            os.system(f"rm {conf_files}/targets/{args.delete[0].replace(' ', '')}")


if __name__ == "__main__":
    import argparse
    import yaml
    import os
    import subprocess

    parser = argparse.ArgumentParser(description='Schedule observations.', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--show_active_observation', '-show', action='store_true', help='''\
Display the active schedule that the unit will use to select targets and take pictures of.
Example:
                >> schedule -show
                        

''')
    parser.add_argument('--list_target_files', '-ls', action='store_true', help='''\
Lists available schedule files.
Example:
            >> schedule -ls
                        

''')
    parser.add_argument('--select', '-s', action='store', nargs=1, metavar='<schedule file name>.yaml', help='''\
Select a schedule file by name, making it the active schedule for the system. Does not update during automated operation.
Example:
            >> schedule --select test_fields.yaml   


''')
    parser.add_argument('--new', '--make_new_schedule', '-touch', '-n', action='store', nargs=1, metavar='<schedule file name>.yaml', help='''\
Create a new schedule file that can determine what to observe when selected as the active schedule. Targets with higher priorities are 
observed first. Follow the prompts after running the command.
Example:
            >> schedule --new test_fields.yaml
                        

''')
    parser.add_argument('--edit', '-e', '-nano', '-vm', '-vim', action='store', nargs=1, metavar='<schedule file name>.yaml', help='''\
Edit values of the specified schedule file.
Example:
            >> schedule --edit test_fields.yaml
                        

''')
    parser.add_argument('--delete', '--remove', '-rm', '-del', action='store', nargs=1, metavar='<schedule file to delete>.yaml', help='''\
Remove a specified schedule file.
Example:
            >> schedule -rm example.yaml
                        

''')
    
    args = parser.parse_args()
    main(args)
    