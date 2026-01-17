# Project Overview

This project is a Python application designed to demonstrate the use of the `fastmcp` library. It implements a simple client-server architecture where a server exposes a remote procedure call (RPC) and a client consumes it.

**Key Technologies:**

*   **Python:** The core programming language.
*   **FastMCP:** A library for creating and consuming RPCs.

**Architecture:**

The project is divided into two main components:

*   `app/my_server.py`: This file defines and runs a `fastmcp` server. It exposes a single tool named `greet` that takes a name as input and returns a greeting.
*   `app/my_client.py`: This file contains a `fastmcp` client that connects to the server, calls the `greet` tool with the name "Ford", and prints the result.

# Building and Running

**1. Install Dependencies:**

This project uses `uv` to manage dependencies. To install them, run:

```bash
uv pip install -r app/requirements.txt
```

**2. Running the Server:**

To start the `fastmcp` server, run the following command from the root of the project:

```bash
python app/my_server.py
```

The server will start on `http://localhost:8000`.

**3. Running the Client:**

To run the client and call the `greet` tool on the server, execute the following command in a separate terminal:

```bash
python app/my_client.py
```

The client will connect to the server, call the `greet` tool, and print the response to the console.

# Development Conventions

*   **Linting:** This project uses `ruff` for code linting. To check the code for any linting errors, run:

    ```bash
    ruff check .
    ```
