#!/usr/bin/env python3

import tableauserverclient as TSC
from getpass import getpass
import os
import time
import argparse
import pick


def authenticate(args):
    """Authenticate with server"""
    if args.server_url is None:
        server_url = input("Server: ")
        args.server_url = server_url
    if args.username is None:
        username = str(input("Username: "))
        args.username = username
    password = getpass()
    tableau_auth = TSC.TableauAuth(args.username, password)
    server = TSC.Server(args.server_url)
    server.use_server_version()
    try:
        server.auth.sign_in(tableau_auth)
        return (True, server)
    except:
        print("Authentification failed.")
        args.username = None
        return (False, server)


def get_object_list(server, args):
    """Get a lists of all the objects (workbooks, views, projects or datasources) on the server"""
    if args.object_type == "workbook":
        all_objects, pagination_item = server.workbooks.get()
    elif args.object_type == "datasource":
        all_objects, pagination_item = server.datasources.get()
    elif args.object_type == "project":
        all_objects, pagination_item = server.projects.get()
    elif args.object_type == "view":
        all_objects, pagination_item = server.views.get()
    return (all_objects)


def pick_object(all_objects, args):
    """Waits for the user to pick one of the objects"""
    all_objects_name = [single_object.name for single_object in all_objects]
    option, index = pick.pick(all_objects_name, title="Choose a {}:".format(args.object_type), indicator='->')
    args.object_id = all_objects[index].id
    args.object_name = all_objects[index].name
    return (all_objects[index])


def select_one(all_objects, args):
    """Waits for the user to choose one of the objects"""
    objects_enum = enumerate(all_objects, start=1)
    for index, data in objects_enum:
        print("{}: {}".format(index, data.name))
    selected_index = int(input("\nPlease enter the number of the {}:\n".format(args.object_type)))
    args.object_id = all_objects[selected_index - 1].id
    args.object_name = all_objects[selected_index - 1].name
    return (all_objects[selected_index - 1])


def download(server, args, selected_object):
    """Downloads the selected object"""
    # set filepath for downloading the file
    if args.download is True:
        args.download = os.getcwd() + "/" + args.object_name
    if args.object_type == "workbook":
        args.download += ".twbx"
        file_path = server.workbooks.download(
                args.object_id, filepath=args.download, include_extract=True,
                no_extract=None)
    elif args.object_type == "datasource":
        file_path = server.datasources.download(
                args.object_id, filepath=args.download, include_extract=True,
                no_extract=None)
    elif args.object_type == "view":
        args.download += ".jpeg"
        image_req_option = TSC.ImageRequestOptions(
                imageresolution=TSC.ImageRequestOptions.Resolution.High)
        server.views.populate_image(selected_object, image_req_option)
        with open(args.download, "wb") as image_file:
            image_file.write(selected_object.image)
    print("\nDownloaded the file to {0}.".format(args.download))


def publish(server, args):
    if args.project_name is None and args.project_id is None:
        args.object_type = "project"
        all_objects = get_object_list(server, args)
        pick_object(all_objects, args)
        args.project_id = args.object_id
    if args.project_name and args.project_id is None:
        options = TSC.RequestOptions()
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                        TSC.RequestOptions.Operator.Equals,
                                        args.project_name))
        filtered_projects, _ = server.projects.get(req_options=options)
        # Result can either be a matching project or an empty list
        if filtered_projects:
            project = filtered_projects.pop()
            args.project_id = project.id
        else:
            print("No project named '{}' found".format(filter_project_name))
    if args.project_id:
        new_workbook = TSC.WorkbookItem(args.project_id)
        new_workbook = server.workbooks.publish(new_workbook, args.publish, as_job=False, mode='CreateNew')
        print("Workbook published. ID: {0}".format(new_workbook.id))


def refresh(server, args):
    if args.object_id is None and args.object_name is None:
        args.object_type = "workbook"
        all_objects = get_object_list(server, args)
        pick_object(all_objects, args)
    if args.object_name and args.object_id is None:
        options = TSC.RequestOptions()
        options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                        TSC.RequestOptions.Operator.Equals,
                                        args.object_name))
        filtered_projects, _ = server.workbooks.get(req_options=options)
        # Result can either be a matching project or an empty list
        if filtered_projects:
            filtered_objects_name = [single_object.name for single_object in filtered_objects]
            _, index = pick.pick(filtered_objects_name, title="Pick the {} you want to refresh".format(args.object_type))
            args.object_id = filtered_objects[index].id
        else:
            print("No object named '{}' found".format(args.object_name))
    if args.object_id:
        workbook = server.workbooks.refresh(args.object_id)
        if args.object_name is None:
            args.object_name = server.workbooks.get_by_id(args.object_id).name
        print("\nThe data of workbook {0} is refreshed.".format(args.object_name))


def set_action_type(server, args):
    """Lets user choose between different actions"""
    action, index = pick.pick(['download', 'publish', 'refresh'],
            title="What action would you like to perform?", indicator='->')
    if action == "download":
        args.download = True
    elif action == "publish":
        args.publish = input("Please enter the path of the file you would like to publish:\n")
    elif action == "refresh":
        args.refresh = True


def parse_arguments():
    """gives the user the ability to pass arguments when running the application"""
    parser = argparse.ArgumentParser(description='Simple application to interact with data on a tableau server')
    # mutually exclusive group of arguments with action type
    # (refresh, download, publish)
    group_required = parser.add_mutually_exclusive_group(required=False)
    group_required.add_argument('--refresh', '-r', action='store_true')
    group_required.add_argument('--publish', '-p', required=False,
                        help='filepath of the file to publish')
    group_required.add_argument('--download', '-d', required=False,
                        help='filepath to save the file returned',
                        nargs='?', action='store', const=True)
    parser.add_argument('--server-url', '-s', required=False,
                        help='server address')
    parser.add_argument('--object-type', '-o', required=False,
                        help='type of object')
    parser.add_argument('--object-id', '-i', required=False,
                        help='id of the objects')
    parser.add_argument('--site-id', '-si', required=False,
                        help='content url for site the view is on')
    parser.add_argument('--username', '-u', required=False,
                        help='username to sign into server')
    parser.add_argument('--object-name', '-on', required=False,
                        help='name of object to download')
    # mutually exclusive group of arguments about project info
    group_project = parser.add_mutually_exclusive_group(required=False)
    group_project.add_argument('--project-id', '-pid', required=False,
                        help='project id where file gets publish in')
    group_project.add_argument('--project-name', '-n', required=False,
                        help='project name where file gets publish in')
    parser.add_argument('--logging-level', '-l',
                        choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    args = parser.parse_args()
    return (args)


def main():
    args = parse_arguments()
    authenticated = False
    while (authenticated is False):
        authenticated, server = authenticate(args)
    # if the user didn't set the flags they will get prompted
    # to choose an action (download, publish, refresh)
    if args.download is None and args.publish is None and args.refresh is False:
        set_action_type(server, args)
    if args.download:
        # id user didn't specify what type of object they want to
        # download they'll get prompted to choose from a list
        if args.object_type is None:
            args.object_type, _ = pick.pick(['workbook', 'view', 'datasource'],
                    title='What do you want to download?', indicator='->')
        all_objects = get_object_list(server, args)
        selected_object = pick_object(all_objects, args)
        download(server, args, selected_object)
    elif args.publish:
        args.object_type = "projects"
        publish(server, args)
    elif args.refresh:
        refresh(server, args)
    server.auth.sign_out()


if __name__ == "__main__":
    main()
