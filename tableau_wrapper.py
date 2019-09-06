#!/usr/bin/env python3

import tableauserverclient as TSC
from getpass import getpass
import os
import time
import argparse
import pick


def publish(resource_type, project_name, path, mode, server_url=None, username=None, password=None, server=None):
    """
    Publish a datasource
    params: resource_type (type of the resource (workbook/datasource) to publish)
            project_name (name of the project the datasource is stored in/should be stored in) REQUIRED
            path (path of the datasource to publish)
            mode (CreateNew, Overwrite, Append)
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            server (the server object if authenticated previosly)
    return: ID of the published datasource
    error:  NameError if resource_type is neither workbook nor datasource
    """

    # check if the either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server)
    # if resource is a datasource create new object and publish
    if resource_typ == "datasource":
        project_id = None
        # Use the project id to create new datsource_item
        new_resource = TSC.DatasourceItem(project_id)
        # publish data source (specified in file_path)
        new_resource = server.datasources.publish(
                        new_resource, path, mode)
    # if resource is workbook create new object and publish
    elif resource_type == "workbook":
        project_id = get_filtered_result(server, project_name, "project").id
        # create new workbook
        new_resource = TSC.WorkbookItem(project_id)
        # publish workbook
        new_resource = server.workbooks.publish(new_resource, path, mode=mode, as_job=False)
    # raise error if resource_type id neither workbook nor datasource
    else:
        raise NameError("Invalid resource_type")
    return (new_resource.id)


def refresh(resource_name, project_name, resource_type, server_url=None, username=None, password=None, path=None, server=None):
    """
    Refresh a workbook or datasource
    params: resource_name (name of the workbook to download) REQUIRED
            project_name (name of the project the workbook is stored in) REQUIRED
            resource_type (workbook or datasource) REQUIRED
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            path (path to download the image to)
            server (the server object if authenticated previosly)
    return: ID of the refreshed workbook
    error:  NameError if resource_type is neither workbook nor datasource
    """

    # check if the either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server)
    # if resource is a workbook get the id and refresh
    if resource_type == 'workbook':
        resource_id = None
        workbook = server.workbooks.refresh(resource_id)
    # if resource is a datasource get the id and refresh
    elif resource_type == 'datasoure':
        resource_id = None
        workbook = server.datasources.refresh(resource_id)
    # raise error if resource_type id neither workbook nor datasource
    else:
        raise NameError("Invalid resource_type")
    return (resource_id)


def download(resource_type, resource_name, project_name, server_url=None, username=None, password=None, path=None, server=None, include_extract=True):
    """
    Downloads the datasource or workbook
    params: resource_type (type of the resource (workbook/datasource) to download) REQUIRED
            resource_name (name of the resource to download) REQUIRED
            project_name (name of the project the resource is stored in) REQUIRED
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            path (path to download the resource to)
            server (the server object if authenticated previosly)
            include_extract (boolean if extract should be included in the download, by default True)
    return: path of the downloaded resource
    error:  NameError if resource_type is neither workbook nor datasource
    """
    path = os.getcwd() + "/" + "testiii"
    # check if either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server_url, server)
    # if resource is a workbook get the id and download
    if resource_type == "workbook":
        # get id
        resource_id = get_resource_id(resource_type, resource_name, project_name, server)
        # download datasource
        file_path = server.workbooks.download(resource_id)
    # if resource is a datasource get the id and download
    elif resource_type == "datasource":
        # get id
        resource_id  = None
        # download datasource
        file_path = server.datasources.download(resource_id, path, include_extract)
    # raise error if resource_type id neither workbook nor datasource
    else:
        raise NameError("Invalid resource_type")
    return (file_path)


def download_view_image(resource_name, project_name, server_url=None, username=None, password=None, path=None, server=None, resolution="high"):
    """
    Downloads the view
    params: resource_name (name of the workbook to download) REQUIRED
            project_name (name of the project the workbook is stored in) REQUIRED
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            path (path to download the image to)
            server (the server object if authenticated previosly)
            resolution (resultion of the image)
    return: path of the downloaded image
    """

    # check if the either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server)
    # get id
    resource_id, resource_object = None
    # request for high resolution
    if resolution == 'high':
        imageresolution=TSC.ImageRequestOptions.Resolution.High
    # request for medium resolution
    if resolution == 'medium':
        imageresolution=TSC.ImageRequestOptions.Resolution.Medium
    # request for low resolution
    if resolution == 'low':
        imageresolution=TSC.ImageRequestOptions.Resolution.Low
    # make request
    image_req_option = TSC.ImageRequestOptions(imageresolution)
    server.views.populate_image(resource_object, image_req_option)
    # write to disk
    with open(path, "wb") as image_file:
            image_file.write(resource_object.image)
    return (path)


def download_view_csv():
    print("work in progress")


def download_view_pdf(resource_name, project_name, server_url=None, username=None, password=None, path=None, server=None, orientation='portrait', filter_key=None, filter_value=None):
    """
    Download the view
    params: resource_name (name of the workbook to download) REQUIRED
            project_name (name of the project the workbook is stored in) REQUIRED
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            path (path to download the image to)
            server (the server object if authenticated previosly)
            orientation (orientation of the pdf (landscape/portrait))
            filter_key (the key the view should get filtered on)
            filter_value (the value for the key)
    return: path of the downloaded pdf
    """

    # check if the either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server_url, server)
    # get id
    resource_id, resource_object = None
    # set landscape orientation for the pdf
    if orientation == 'landscape':
        orientation_req = TSC.PDFRequestOptions.Orientation.Landscape
    # set portrait orientation for the pdf
    if orientation == 'portrait':
        orientation_req = TSC.PDFRequestOptions.Orientation.Portrait
    # set the PDF request options
    pdf_req_option = TSC.PDFRequestOptions(page_type=TSC.PDFRequestOptions.PageType.A4, orientation=orientation_req)
    # (optional) set a view filter
    if filter_key and filter_value:
        pdf_req_option.vf(filter_key, filter_value)
    # retrieve the PDF for a view
    server.views.populate_pdf(view_item, pdf_req_option)
    file_path = server.workbooks.download(
                resource_id, path, include_extract=extract,
                no_extract=None)
    return (file_path)


def check_credentials_authenticate(username=None, password=None, server_url=None, server=None):
    """
    Authenticates with credentials if server object None
    params: username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            server_url (url of the server)
            server (the server object if authenticated previosly)
    return: server object
    error:  TypeError if credentials are missing (either the server object or username and password)
    """

    # check if the either all the necessary credentials or the server object are there
    if server is None and (server_url or username or password) is None:
        raise TypeError
    # if no server object got passed in authenticate with the credentials
    if server is None:
        server = authenticate(server_url, username, password)
    return (server)


def authenticate(server_url, username, password):
    """
    Authenticates with the server
    params: server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
    return: server object
    error:  AuthenticationError if authentication failed
    """

    try:
        tableau_auth = TSC.TableauAuth(username, password)
        server = TSC.Server(server_url)
        server.use_server_version()
        server.auth.sign_in(tableau_auth)
        print("Authentication successful.")
        return (server)
    except:
        print("Authentification failed.")
        raise AuthenticationError


def get_project_id(project_name):
    # set the filter request
    options = TSC.RequestOptions()
    options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                    TSC.RequestOptions.Operator.Equals,
                                    project_name))
    filtered_result, _ = server.projects.get(req_options=options)
    # return the last object in the list (if there are multiple)
    return (filtered_result.pop().id)


def get_resource_id(resource_type, resource_name, project_name, server):
    # set the filter request
    options = TSC.RequestOptions()
    options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                    TSC.RequestOptions.Operator.Equals,
                                    resource_name))
    """options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                    TSC.RequestOptions.Operator.Equals,
                                    project_name))"""
    if resource_type == 'workbook':
        filtered_result, _ = server.workbooks.get(req_options=options)
    if resource_type == 'view':
        filtered_result, _ = server.workbooks.get(req_options=options)
   
    # return the last object in the list (if there are multiple)
    return (filtered_result.pop().id)


# DELETE
def download_datasource(resource_name, project_name, server_url=None, username=None, password=None, path=None, server=None, include_extract=True):
    """
    Downloads the datasource
    params: resource_name (name of the workbook to download) REQUIRED
            project_name (name of the project the workbook is stored in) REQUIRED
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            path (path to download the image to)
            server (the server object if authenticated previosly)
            include_extract (boolean if extract should be included in the download
    return: path of the downloaded datasource
    """

    # check if the either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server_url, server)
    # get id
    resource_id = None
    # download datasource
    file_path = server.datasources.download(resource_id, path, include_extract)
    return (file_path)


# DELETE
def download_workbook(resource_name, project_name, server_url=None, username=None, password=None, path=None, server=None, include_extract=True):
    """
    Downloads the workbook
    params: resource_name (name of the workbook to download) REQUIRED
            project_name (name of the project the workbook is stored in) REQUIRED
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            path (path to download the workbook to)
            server (the server object if authenticated previosly)
            include_extract (boolean if extract should be included in the download
    return: path of the downloaded workbook
    """

    # check if either all the necessary credentials or server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server_url, server)
    # get id
    resource_id = None
    # send request
    file_path = server.workbooks.download(
                resource_id, path, include_extract=include_extract)
    return (file_path)


# DELETE
def publish_workbook(project_name, path, mode, server_url=None, username=None, password=None, server=None):
    """
    Publish a workbook
    params: project_name (name of the project the workbook should be stored in) REQUIRED
            path (path to the workbook to publish)
            mode (CreateNew, Overwrite, Append)
            server_url (the url of the server to connect with)
            username (username of the user to authenticate with)
            password (password of the user to authenticate with)
            server (the server object if authenticated previosly)
    return: ID of the published workbook
    """

    # check if the either all the necessary credentials or the server object are there and authenticate if necessary
    server = check_credentials_authenticate(username, password, server_url, sever)
    # get project id
    project_id = None
    # create new workbook
    new_workbook = TSC.WorkbookItem(project_id)
    # publish workbook
    new_workbook = server.workbooks.publish(new_workbook, path, as_job=False, mode=mode)
    return (new_workbook.id)


def get_object_list(server, object_type):
    """Get a lists of all the objects (workbooks, views, projects or datasources) on the server"""
    if object_type == "workbook":
        all_objects, pagination_item = server.workbooks.get()
    elif object_type == "datasource":
        all_objects, pagination_item = server.datasources.get()
    elif object_type == "project":
        all_objects, pagination_item = server.projects.get()
    elif object_type == "view":
        all_objects, pagination_item = server.views.get()
    return (all_objects)


def pick_object(all_objects, object_type):
    """Waits for the user to pick one of the objects"""
    all_objects_name = [single_object.name for single_object in all_objects]
    option, index = pick.pick(all_objects_name, title="Choose a {}:".format(object_type), indicator='->')
    return (all_objects[index], all_objects[index].id, all_objects[index].name)


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
                        help='workbook/view/datasource')
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


def get_filtered_result(server, filter_by, category):
    # set the filter request
    options = TSC.RequestOptions()
    options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                    TSC.RequestOptions.Operator.Equals,
                                    filter_by))
    # send the request
    if category == "project":
        filtered_result, _ = server.projects.get(req_options=options)
    elif category == "view":
        filtered_result, _ = server.views.get(req_options=options)
    elif category == "workbook":
        filtered_result, _ = server.workbooks.get(req_options=options)
    elif category == "datasource":
        filtered_result, _ = server.datasources.get(req_options=options)
    # return the last object in the list (if there are multiple)
    return (filtered_result.pop())


def main():
    # parse the passed arguments
    args = parse_arguments()
    # authenticate
    server = None
    while (server is None):
        # get credentials from user
        server_url = input("Server: ")
        username = str(input("Username: "))
        username = str(input("Username: "))
        password = getpass()
        server = authenticate(server_url, username, password)
    # if the user didn't set the flags they will get prompted
    # to choose an action (download, publish, refresh)
    if args.download is None and args.publish is None and args.refresh is False:
        set_action_type(server, args)
    # if the user chose 'download'
    if args.download:
        # if user didn't specify what type of object they want to
        # download they'll get prompted to choose from a list
        if args.object_type is None:
            args.object_type, _ = pick.pick(['workbook', 'view', 'datasource'],
                    title='What do you want to download?', indicator='->')
        if args.object_name is None:
            # get list of all the objects on the server of chosen type
            all_objects = get_object_list(server, args.object_type)
            # let user select one of the objects
            selected_object, args.object_id, args.object_name = pick_object(all_objects, args.object_type)
        else:
            selected_object = get_filtered_result(server, args.object_name, args.object_type)
            args.object_id = selected_object.id
        download(server, args, selected_object)
    # if the user chose 'publish'
    elif args.publish:
        publish(server, args)
    # if the user chose 'refresh'
    elif args.refresh:
        refresh(server, args)
    server.auth.sign_out()


def test():
    server = authenticate("Ss", "Ss", "Ss")
    file_path = download("workbook", "goodreads", "Default", server=server)
    print(filepath)


if __name__ == "__main__":
    test()
