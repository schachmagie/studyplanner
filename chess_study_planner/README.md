# Chess Study Planner

A comprehensive web application for planning and tracking chess study sessions.

## Features

- User authentication (register/login)
- Weekly study planning
- Daily study tracking
- History review
- Responsive design
- Secure password storage
- SQLite database integration

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chess-study-planner.git
   cd chess-study-planner
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python app.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application at `http://localhost:5000`

## Configuration

The application uses SQLite by default. To use a different database:

1. Update the `get_db_connection()` function in `app.py`
2. Install the appropriate database driver
3. Update the connection string

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.