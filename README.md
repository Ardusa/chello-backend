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
- `PATCH /set-password`: Set a new password for an account
- `GET /verify-login/`: Verify user login and retrieve user details
- `POST /refresh`: Refresh access and refresh tokens
- `PUT /accounts/register-account`: Register a new account
- `GET /accounts/get-accounts`: Retrieve a list of accounts
- `GET /accounts/{account_id}`: Retrieve details of a specific account
- `PUT /accounts/settings`: Update account settings
- `POST /projects/create`: Create a new project
- `PATCH /projects/{project_id}/`: Edit an existing project
- `GET /projects/{project_id}/`: Retrieve tasks for a specific project
- `DELETE /projects/{project_id}`: Delete a project
- `GET /projects/get-projects`: Retrieve projects assigned to the logged-in user
- `POST /tasks/create-task`: Create a new task
- `DELETE /tasks/{task_id}`: Delete a task
- `GET /tasks/{task_id}`: Retrieve details of a specific task
- `WebSocket /ws`: Real-time updates for database tables

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, feedback, or feature ideas, feel free to reach out through the repository’s issue tracker.

---

Happy coding and organizing with Chello!
