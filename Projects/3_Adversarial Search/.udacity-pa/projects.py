import os
from udacity_pa import udacity

nanodegree = 'nd898'
projects = ['adversarial_search']
filenames_all = ['my_custom_player.py', 'report.pdf', 'data.pickle']

def submit(args):
    filenames = []
    for filename in filenames_all:
        if os.path.isfile(filename):
            filenames.append(filename)

    if 'my_custom_player.py' not in filenames:
        raise RuntimeError(
            "The file 'my_custom_player.py' was not found in your current directory. This " +
            "file MUST be included in every PA submission.")
    if 'report.pdf' not in filenames:
        print(
            "WARNING: Make sure your submission includes a file named 'report.pdf' if you " +
            "expect this to be your final submission in the classroom for review.")

    udacity.submit(nanodegree, projects[0], filenames, 
                   environment = args.environment,
                   jwt_path = args.jwt_path)
