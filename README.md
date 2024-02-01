# Game Hub

Welcome to the Flask Game Hub! This is a simple web application that allows you to manage and review games. Follow the instructions below to get started.

## Usage

### Running the Flask App

1. Ensure you are in the project directory.

2. Run the Flask app:

    ```bash
    flask run
    ```

3. Open your web browser and go to [http://localhost:5000](http://localhost:5000).

### Default Users

The application comes with pre-configured user for testing purposes.

- **Owner Account:**
  - Username: owner
  - Password: owner12
  - Role: Admin
  - Allows you to add new games to the hub.

### Database

If you want to start fresh or encounter any issues, you can delete the `database.db` file and create a new one:

```bash
rm database.db
touch database.db
```
 During the initial run, the admin's user (owner) will be automatically created.

## Features

- **Add New Games:**
  - Log in with the admin's account (owner is the provided user).
  - Navigate to the "Add Game" section to add new games to the hub.

- **User Authentication:**
  - Sign up as a new normal user if needed (or login with the provided admin user - owner).

- **Game Reviews:**
  - Logged-in users can add reviews to games.
