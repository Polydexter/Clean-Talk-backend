# CleanTalk - CS50W Capstone project

## Overview
‘Clean Talk’ is my capstone project for the CS50W course. It is a mobile responsive chat application with decoupled frontend and backend solutions. Its core functionality consists in real time messaging between authenticated users. 

## Distinctiveness & Complexity
The core messaging functionality of the project does not overlap with the ‘Network’ post features or 'E-Commerce' comments (since my project is based on the websocket protocol).  While grounded in the course’s materials, this application goes beyond the scope of the previously assigned projects. Frontend and backend apps interact using API, real time messaging is implemented with websockets, and authentication flow is implemented using JSON web tokens (JWT) with refresh tokens rotation. None of these subjects were treated in any of the assignments during the course. Creating the application implied getting familiar with technologies beyond the scope of the course and required several weeks of study and development.


## Technologies
Frontend is implemented with [ReactJS](https://reactjs.org/) framework and backend – with  [Django](https://www.djangoproject.com/).  API is built with Djangorestframework, websocket connections are handled with [Django Channels](https://channels.readthedocs.io/en/stable/#). The Django application is set up with [PostgreSQL](https://www.postgresql.org/) as its database engine, and Django Channels use [Redis](https://redis.io/) for exchanging data between channels. Authentication is implemented with JSON web tokens (JWT) with rotating refresh tokens. On the backend I used [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) library to handle generation and validation of tokens. On the frontend I used [Axios](https://axios-http.com/docs/intro) library as my http-client to handle requests to API, including fetching messaging history and refreshing tokens. I used [React Router](https://reactrouter.com/en/main) for managing routes.
CSS is implemented with the [Bootstrap](https://getbootstrap.com/) framework and the [React Bootstrap](https://react-bootstrap.github.io/) library.

## File structure
There are two two main folders in the root directory of the project – Frontend and Backend. 

Backend file structure corresponds to the default Django project layout with two applications installed. 
The *‘users’* application handles everything concerning users. Its models.py module contains a custom User model as well as a custom User Manager. Both of these enable the application to use email as a primary authentication field. Serializers.py contain serializers for registering users and providing user details. The app also contains a serializer which adds a custom claim (‘username’) inside the JWT tokens. Views.py contains API views for registering a user and for listing all the available users. There is also a custom view for obtaining JWT tokens which enables custom claims mentioned above.
The *‘conversation’* app is responsible for the messaging functionality. Firstly, it has channelsmiddleware.py with a custom middleware which enables authentication of the websocket connections. In models.py it has models for conversations and for messages. Since a conversation is a collection of messages, only the Message objects need to be serialized and sent to the front. Therefore the serializer  for messages is stored inside the ‘api’ subdirectory of the app.

Frontend file structure extends default layout of a Vite React project, made with create-vite service. All of my custom code is stored in the src directory. Src directory contains 4 subdirectories: components, contexts, routes and services. 
Routes: contain four routes of the application: registration, login, conversations (list of all the users to whom one can talk to) and chat (for one particular conversation).
Components: Navbar component, Message component and ProtectedRoute component. The latter is used to wrap protected routes. The application has two protected routes: Conversations and Chat.
Contexts: contains a single file - AuthContext, which provides methods for handling authentication and authorisation.
Services: contain two files with methods used in different parts of the application. AutHeader helps to properly configure HTTP headers with access tokens. AuthService provides a range of auxiliary methods which allow to keep context methods short and concise. Auth service handles local storage management and refreshing tokens procedure.

## Launching
In order to launch the application locally you need to have Python and PiP already installed. As well as NPM package manager for Node. 
- clone the github repository
- Install dependencies
> Dependencies can be installed by running the below commands from Backend and Frontend respective directories.
> For backend:
> `pip3 install -r requirements.txt`
> For the frontend:
> `npm install`
- run Redis and PostgreSQL locally.
- create .env file in the root directory of the Backend project and set all the environment variables specified in settings  (SECRET_KEY, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, REDIS_HOST, REDIS_PORT, FRONTEND_DOMAIN)
