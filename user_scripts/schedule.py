#!/usr/bin/python3
# TODO: add pretty colors to the text

def main(args):

    # TODO: FIX PATHS ALL SINGLE FORWARD SLASH
    #conf_files = os.path.realpath(__file__).replace('user_scripts/schedule.py', '/conf_files/settings.yaml')
    conf_files = os.path.realpath(__file__).replace(r'user_scripts\schedule.py', r'conf_files')

    yesOrNo = lambda x: x == 'y' or x == 'Y' or x == 'yes' or x == 'Yes'

    def edit_schedule(schedule):
        # Coded quickly, improvements welcome
        # If the user inputs an invalid setting this kicks them out of the command and doesnt let them continue editing

        settingType = {'user_note': str,'priority': int, 'ra': str, 'dec': str, 'cmd': str,
                       'take_images': bool, 'num_captures': int, 'exposure_time': int}

        response = 'y'
        while True:
            if yesOrNo(response):
                print("List of targets in this schedule:")
                for target in schedule.keys():
                    print(target)
                targetToEdit = input("What target do you want to edit? ")
                if any(validTarget == targetToEdit for validTarget in schedule.keys()):
                    print(f"List of settings for {targetToEdit}:")
                    for setting in schedule[targetToEdit].keys():
                        print(setting)
                    settingToEdit = input("What setting do you want to change? ")
                    if any(validSetting == settingToEdit for validSetting in schedule[targetToEdit]):
                        if settingToEdit == 'primary_cam' or settingToEdit == 'secondary_cam':
                            print(f"List of {settingToEdit} settings:")
                            for setting in schedule[targetToEdit][settingToEdit].keys():
                                print(setting)
                            childSetting = input("What setting do you want to change? ")
                            if any(validSetting == childSetting for validSetting in schedule[targetToEdit][settingToEdit].keys()):
                                childArg = _betterInput(f"What value would you like to change {childSetting} to? ", settingType[childSetting])
                                schedule[targetToEdit][settingToEdit][childSetting] = childArg
                        else:
                            arg = _betterInput(f"What value would you like to change {settingToEdit} to? ", settingType[settingToEdit]) 
                            schedule[targetToEdit][settingToEdit] = arg
        
            else:
                break
            
            response = input("Would you like to edit a target? (y/n) ")
        
        return schedule

    def _betterInput(prompt, Type = str, default = None):
        #TODO: Implement the mountCommand class so that I can also have it 
        #      handled here

        result = None
        while result == None:
            userInput = input(prompt) or default
            if userInput:
                try:
                    result = Type(userInput)
                except TypeError as error:
                    print('=INVALID= Your input was not of type ', Type)
                    userInput = None
                except Exception as error:
                    print('=ERROR= ', error)
                    userInput = None
        return result

    def makeObservationDict():

        #TODO: Handle bad inputs

        def _makeCameraArr():
            camera = {}
            camera['num_captures'] = None
            camera['exposure_time'] = None
            camera['take_images'] = yesOrNo(input('Do you want this camera to take images [y/n]: '))
            if camera['take_images']:
                camera['num_captures'] = _betterInput('Enter # of images to capture: ', Type=int, default=1)
                camera['exposure_time'] = _betterInput('Enter exposure time per image in seconds: ', Type=int, default=1)
            return camera

        note = _betterInput('Enter user note [leave blank if none]: ', default='None')
        priority = _betterInput('Input the priority of the observation as a positive whole number: ', Type=int, default=0)
        ra = _betterInput('Input the ra in hours minutes seconds (00 42 44): ', default='00 42 44')
        dec = _betterInput('Input the dec in degrees minutes seconds (-41 16 09): ', default='+41 16 09')
        cmd = _betterInput('Input the command [leave blank for slew]: ', default='slew to target')
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
        # TODO: FIX PATHS ALL SINGLE FORWARD SLASH
        with open(f"{conf_files}\settings.yaml", "r") as f:
            settings = yaml.safe_load(f)
        activeFileName = settings["TARGET_FILE"]
        with open(f"{conf_files}\\targets\{activeFileName}") as f:
            activeSchedule = yaml.safe_load(f)

        print("---------------   Summary of active schedule   ---------------")
        print(f"File name: {activeFileName}              Number of targets: {len(activeSchedule.keys())}")
        print("Target names:")
        for name in activeSchedule.keys():
            print(f"{name}")
        
        while True:
            doDetails = input("List detailed information about a target? (y/n) ")
            if yesOrNo(doDetails):
                targetName = input("Enter the name of the target: ")
                if any(targets in targetName for targets in activeSchedule.keys()):
                    print(f"Notes: {activeSchedule[targetName]['user_note']}")
                    print(f"Priority: {activeSchedule[targetName]['priority']}")
                    print(f"Position RA/DEC: {activeSchedule[targetName]['ra']}   {activeSchedule[targetName]['dec']}")
                    print("Primary Camera Settings:")
                    for setting in activeSchedule[targetName]['primary_cam'].keys():
                        print(f"{setting}: {activeSchedule[targetName]['primary_cam'][setting]}")
                    print("Secondary Camera Settings:")
                    for setting in activeSchedule[targetName]['secondary_cam'].keys():
                        print(f"{setting}: {activeSchedule[targetName]['primary_cam'][setting]}")
            else:
                break
    
    # TODO: Test on unix system
    if args.list_target_files:
        #out = os.popen(f"ls {conf_files}/targets/*.yaml").replace(f'{conf_files}/targets/', ' ').replace('\n', '').split()
        out = ['observations.yaml', 'test_fields.yaml'] # TODO: Placeholder for above^ DELETE before merge
        print("Available schedule files:")
        for scheduleFile in out:
            print(scheduleFile)

    if args.select:
        try:

            with open(f"{conf_files}\\settings.yaml", "r") as f: # TODO: Replace backslashes with forward slash
                settings = yaml.safe_load(f)
            settings['TARGET_FILE'] = args.select[0].replace(' ', '')
            with open(f"{conf_files}\\settings.yaml", "w") as f: # TODO: Replace backslashes with forward slash
                yaml.dump(settings, f)

        except Exception as error:
            print("=ERROR=", error)
    
    if args.new:

        if ".yaml" not in args.new[0]:
            print("=ERROR= Specified file name must have suffix '.yaml'")
        else:
            filePath = f"{conf_files}/targets/{args.new[0].replace(' ', '')}"
            #os.system(f"touch {filePath}") # TODO: UNCOMMENT before commit

            keepGettingObservations = True
            observationsDict = {}
            while keepGettingObservations:
                name = str(input('Name of the observation: '))
                attributes = makeObservationDict()
                observationsDict[name] = attributes
                keepGettingObservations = yesOrNo(input('Add another target? [y/n]: '))
            
            with open(filePath, "w") as f:
                yaml.dump(observationsDict, f)

    if args.edit:

        try:
            with open(f"{conf_files}\\targets\\{args.edit[0].replace(' ', '')}", "r") as f: # TODO: Replace backslashes with forward slash
                schedule = yaml.safe_load(f)
        except Exception as e:
            print("=ERROR= ", e)

        schedule = edit_schedule(schedule)
        with open(f"{conf_files}\\targets\\{args.edit[0].replace(' ', '')}", "w") as f:
            yaml.dump(schedule, f)

if __name__ == "__main__":
    import argparse
    import yaml
    import os

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
    
    args = parser.parse_args(['-h'])
    main(args)
    