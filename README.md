# Pre-requisites:
This project was developed on Python 3.13. Make sure to check the version of your Python before running. This can be done by running separate commands in your terminal.
```
python --version (Windows)
python3 -- version(Ubuntu Linux)
```

# Running the program:
To run the program, you can use the following command in your terminal. Please make sure that the terminal is open in the root directory. 
Also, on Ubuntu, the commands will need to include python3 instead of python.

Notes:
- The server must be initiated before the client.
- The server and client and subsequent clients will all be run on different terminals.

## To Run the Server:
```
python Chat_server.py --name=<server_name> --port=<port_number>
```
<server_name> and <port_number> are to be replaced with the desired server name and port number respectively.

## To Run the Client:
```
python Chat_client.py --name=<client_name> --port=<port_number> 
```

As mentioned before, the <client_name> and <port_number> are to be replaced with the desired client name and port number respectively. Also, the port number should match the inputted port number given to the server.

## Examples:
```
Server:
python Chat_server.py --name=Server --port=9988

Clients:
python Chat_client.py --name=Client1 --port=9988
python Chat_client.py --name=Client2 --port=9988
```

# Registering / Logging in:
After the client successfully connects to the server, the client will be prompted to choose if they wish to register a new user or not.

If the client choose to register, they must input a username and password. The username must be unique. They will then be prompted to log in with a username and password.

If the client chooses not to register, they will be prompted to log in with a username and password.

Currently, the only pre-registered user in the database is username and password both admin.

