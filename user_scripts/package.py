#!/usr/bin/python3

def main(args):

    PARENT_DIR = os.path.realpath(__file__).replace('/user_scripts/package.py', '')
    PACKAGE_RECORD_FILE = f"{PARENT_DIR}/packages/package_locations.yaml"

    # Currently the "update" argument just removes and reinstalls the package, 
    # this bool is used to silence non-error output from remove and install.
    isUpdate = False

    def install(packageName):
            
            if args.install_from_directory:
                packagePath = args.install_from_directory
            
            logger.info(f"Attempting to install {packageName}")
            logger.debug(f'isUpdate = {isUpdate}')

            with open(PACKAGE_RECORD_FILE, "r") as f:
                allPackages = safe_load(f)
            logger.debug("Loaded list of all packages.")

            if allPackages is None:
                allPackages = {}

            try:
                _ = allPackages[packageName]
                logger.error("Can't install a package that is already installed.")
                print(bcolors.FAIL + "Package is already installed. Did you mean --update?" + bcolors.ENDC)
                return
            except KeyError:
                pass

            if not args.install_from_directory:

                # TODO: Remove on merge of standard package
                print(f"""\
{bcolors.PURPLE}
                                                                ---------- Feature Not Implemented Statement ----------
{bcolors.FAIL}
    There are no standard packages that are ready for full release as of 9/24/2023. If you're interested in testing packages early, contact the developers of the package. 
    If you believe this is a mistake, check the POCS-moxa-build github to see if your using an old version. If you're running an old version, update on the command line using {bcolors.ENDC}
    $ cd POCS-moxa-build
    $ git stash
    $ git pull {bcolors.FAIL}
    The update process will change your settings.yaml file, and it will need to be setup again using the panoptes-CLI. You will also need to select your active schedule file 
    again using the schedule panoptes-CLI command.
{bcolors.ENDC}""")
                return

                match packageName:
                # TODO: Should be using wget with a tar balled github release to create a temporary repo 
                # somewhere (probably the home directory), once the package is there, set the 
                # packagePath variable and the system will then copy paste it to the correct 
                # location and record the file positions.
                    case "panoptes3d":
                        logger.debug("Found install case: panoptes3d")
                        # download tar ball
                        logger.info("Unpacking tar file.")
                        os.system("cd ~; tar -xzf panoptes_package.tar.gz; rm panoptes_package.tar.gz")
                        packagePath = "~/panoptes_package"
                    case "panoptes3d-vr":
                        packagePath = "~/panoptespackage"
                    case _:
                        print(bcolors.FAIL + "Invalid package name." + bcolors.ENDC)
                        return
                
            logger.info(f"Adding {packageName}'s files to the POCS-moxa-build folder tree.")
            out = subprocess.run(f"cp -r -v {packagePath}/* {PARENT_DIR}", shell=True, stdout=subprocess.PIPE)

            if not args.install_from_directory:
                os.system(f"cd ~; rm -r -d {packagePath}")

            out = out.stdout.decode('utf-8').replace(" ", "")
            out = out.replace("'", "")

            startIndex = None
            filePaths = []
            while not startIndex == -1:
                startIndex = out.find("->")

                if startIndex == -1:
                    break

                out = out[startIndex+2:]
                endIndex = out.find("\n")
                filePaths.append(out[0:endIndex])
            
            filePaths.sort(key=lambda string : -1 * len(string)) # Sort by string length to allow the rm -d option to delete empty directories on uninstall
            logger.debug(f"filePaths =\n {filePaths}")

            allPackages[packageName] = filePaths      

            with open(PACKAGE_RECORD_FILE, "w") as f:
                dump(allPackages, f)
            logger.info("Saved install locations of new files.")
            
            if not isUpdate:
                print(f"{bcolors.OKGREEN}Installed {packageName}{bcolors.ENDC}")

    def remove(packageName):

        logger.info(f"Attempting to remove {packageName}")
        logger.debug(f'isUpdate = {isUpdate}')

        with open(PACKAGE_RECORD_FILE, "r") as f:
            allPackages = safe_load(f)
        logger.debug("Loaded list of all packages.")

        try:
            filesToRemove = allPackages[packageName]
        except KeyError:
            logger.error("Can't remove a package that is not installed.")
            print(bcolors.FAIL + "Package not installed. Note that CLI commands and package names are not necessarily the same." + bcolors.ENDC)
            return
        
        for file in filesToRemove:
            logger.debug(f"Removed: {file}")
            subprocess.run(["rm", "-d", file])
        
        if not isUpdate:
            print(f"{bcolors.OKGREEN}Removed {packageName}!{bcolors.ENDC}")

        logger.debug(f"Removing {packageName} from list of installed packages/files.")
        allPackages.pop(packageName)

        with open(PACKAGE_RECORD_FILE, "w") as f:
            dump(allPackages, f)
        logger.info(f"Removed {packageName} and its file history.")
    
    if args.install:

        packageName = args.install[0].lower()
        install(packageName)

    if args.remove:

        packageName = args.remove[0].lower()
        remove(packageName)

    if args.update:

        isUpdate = True

        packageName = args.update[0].lower()
        remove(packageName)
        install(packageName)
        print(f"{bcolors.OKGREEN}Succesfully updated {packageName}!{bcolors.ENDC}")
    
    if args.show:

        with open(PACKAGE_RECORD_FILE, "r") as f:
            allPackages = safe_load(f)
        logger.debug("Loaded list of all packages.")
        
        print("\n-------------- Currently Installed Packages --------------")
        for key in list(allPackages.keys()):
            print(bcolors.OKCYAN + key + bcolors.ENDC)

if __name__ == "__main__":
    import argparse
    import subprocess
    import os
    import sys

    from yaml import safe_load, dump
    from schedule import bcolors

    parentDir = os.path.realpath(__file__).replace('/user_scripts/package.py', '')
    sys.path.append(parentDir)

    from logger.astro_logger import astroLogger
    logger = astroLogger(enable_color=True)

    parser = argparse.ArgumentParser(description='Install or remove third-party standard panoptes packages.', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--install', '-i', action='store', nargs=1, type=str, metavar="<package name>", help='''\
    Install a standard panoptes package from your system. Only install packages from developers you trust.
    Example:
                        >> package --install panoptes3d
                        
    ''')
    parser.add_argument('--remove', '--uninstall', '-r', action='store', nargs=1, type=str, metavar="<package name>", help='''\
    Remove a standard panoptes package from your system. Only install packages from developers you trust.
    Example:
                        >> package --remove panoptes3d
                        
    ''')
    parser.add_argument('--show', '-s', '-ls', action='store_true',
                        help='''List the names of installed packages.''')
    
    parser.add_argument('--update', action='store', nargs=1, type=str, metavar="<package name>", help='''\
    Upgrade a standard panoptes package. Has the same effect as removing a package and reinstalling it.
    Example:
                        >> package --update panoptes3d''')
    parser.add_argument('--install_from_directory', '--from_directory', '-from_dir', action='store', type=str, metavar="<path to directory>", help='''\
    Install any package from a user specified directory that has already been unzipped. This argument only has an effect if 
    it is run with the either the --install or --update argument. When run with --install NAME, NAME can be any string and 
    will be the keyword used to manage the package. 
    Example:
                        >> package --install custom_package_name --from_directory /path/to/package
                        >> package --upgrade custom_package_name --from_directory /path/to/package
    WARNING:
    NAME should not be the same as any panoptes standard package name, 
    otherwise the standard package(s) with shared names can not be installed, and will be met with an unclear error message:
    "Package is already installed. Did you mean --update?". If you were to run --update, the custom package will be deleted
    and the standard package will take its place.
    ''')

    args = parser.parse_args()
    main(args)
