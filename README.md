# Chello Backend

Welcome to the **Chello Backend**, the core of Chello—a task management and prioritization service designed to streamline your productivity.

## Features

- **Task Management**: Create, update, and organize tasks effortlessly.
- **Dependencies and Subtasks**: Manage complex workflows by setting dependencies and breaking down tasks into subtasks.
- **Prioritization**: Focus on what matters most with built-in prioritization logic.

## Technology Stack

- **Programming Language**: Python
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite with SQLAlchemy
- **API**: RESTful API for seamless integration with the frontend and iOS app

## API Endpoints

Here are some key endpoints (based on `main.py`):

- `POST /login`: User login to retrieve access and refresh tokens
- `PATCH /set-password/`: Set a new password for an employee
- `GET /get-id/`: Retrieve the logged-in user's details
- `POST /refresh`: Refresh access and refresh tokens
- `POST /create-new-employee`: Register a new employee
- `POST /register-account`: Register a new account
- `GET /employees/get-employees`: Retrieve a list of employees
- `GET /projects/get-projects`: Retrieve projects assigned to the logged-in user
- `POST /projects/create`: Create a new project
- `GET /projects/{project_id}/`: Retrieve tasks for a specific project
- `PUT /projects/{project_id}/tasks`: Retrieve tasks within a project for a specific user
- `GET /verify-login/`: Verify user login and retrieve user details
- `WebSocket /ws`: Real-time updates for database tables

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, feedback, or feature ideas, feel free to reach out through the repository’s issue tracker.

---

Happy coding and organizing with Chello!
