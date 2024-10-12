```
[ CRAPS - 1.0.31 ]
├───[ database ]            # This folder contains data storage and configuration files necessary for the game.
├───[ docs ]                # This folder holds documentation for the game, including user guides and development notes.
├───[ lib ]                 # This folder includes external libraries or custom libraries used in the project.
│      ├───Crypto           # A library for cryptographic functions, likely used for secure data handling.
│      ├───customtkinter    # A library for creating customized user interface components in Python applications.
│      └───pyasn1           # A library for handling ASN.1 data structures, typically used in network protocols.
├───[ src ]                 # This folder contains the main source code of the game.
│      ├───manager          # This module manages the game’s operations, such as starting, stopping, and handling player interactions.
│      ├───security         # This module includes security functions, providing encryption algorithms like AES and RSA.
│      │   ├───aes         # Implementation of the Advanced Encryption Standard (AES) for secure data encryption.
│      │   └───rsa          # Implementation of the RSA encryption algorithm, another method for secure data transmission.
│      └───server           # This module contains the main server code, processing requests from players.
├───[ test ]                # This folder includes test cases to ensure all functionalities of the game work correctly.
├─── server.py              # The main server file that likely initializes the game server and handles incoming connections.
└─── main.py                # The entry point of the application, responsible for starting the game and initializing the user interface.

```