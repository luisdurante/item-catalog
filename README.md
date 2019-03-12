# Udacity's Item Catalog Project
This is the second Udacity's Back-end Developer Nanodegree project. 
The project consists in creating an Item Catalog with the knowledge acquired in the course, using CRUD Operations, Authentication and Authorization system by logging in with providers like Google or Facebook and Creating JSON Endpoints.

## Project Functionalities
In this project you can:
-  Log in with facebook(Using the test users);
- See all items avaiable searching by category;
- Create a new item;
- Edit an item you created;
- Delete an item you created.

## How to run it
- #### Download [Vagrant][Vagrant] and [Virtual Box][VM]
- #### Set up Vagrant 
    Using the terminal, go to the folder and type 'vagrant up' and a linux OS will be installed. After that, run the command 'vagrant ssh' to log in to the Virtual Machine.
 - #### Go to the vagrant folder and run the database
	In your **VM** go to the **Vagrant** folder typing the command:
	>cd /vagrant
- #### Running the database  
	You can do it by running the command:
	 >`python database_setup.py`
- #### Add the catalog categories
	To add the categories to the system you need to execute another file, run it typing: 
	 >`python itemsmenu.py`
- #### Run the program
	Ok, everything is set! Now just run the project:
	>`python project.py`
	
## IMPORTANT!
Unfortunately, this is a test app, so facebook doesn't let you log in with your account, you have to be Test User to do so. However, I created three test users in order to log in:
- Email: gsfadhvndo_1549648428@tfbnw.net Password: udacity
- Email: vqpcneuhrc_1549648429@tfbnw.net Password: udacity
- Email: knddtvusev_1548376565@tfbnw.net Password: udacity

## JSON ENDPOINTS
The application provides information in JSON, to access it you need to change de url path to:
- localhost:8000/categories/JSON to see the categories;
- localhost:8000/items/JSON to see the items in the catalog;
- localhost:8000/(category_id)/(item_id)/JSON to see an specific item.




[Vagrant]: <https://www.vagrantup.com/downloads.html>
[VM]: <https://www.virtualbox.org/wiki/Downloads>

