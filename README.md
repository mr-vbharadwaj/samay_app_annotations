# Annotation Manager

Annotation Manager is a Django-based web application designed to manage image annotations efficiently. It supports a robust workflow for uploading images, creating annotations, verifying them, and presenting the final results, with features tailored for different user roles.

## Features

- **User Roles**:

  - **Admin**: Manages the system and user accounts.
  - **Annotator**: Creates annotations on uploaded images.
  - **Verifier**: Verifies annotations for accuracy.
  - **Viewer**: Views completed and verified annotations.

- **Image Management**:

  - Upload and organize images into datasets.
  - Secure storage and access control for uploaded images.

- **Annotation Workflow**:

  - Create and edit annotations, including keypoint data.
  - Assign annotations for verification.
  - Approval and feedback loop for annotations.

- **Comment System**:

  - Annotators and verifiers can add comments to annotations. (Future Enhancement)

- **Dashboards**:

  - Role-specific dashboards for streamlined workflows.

---

## Installation and Setup

### Prerequisites

Ensure the following software is installed on your system:

- Python 3.10 or higher
- Django 4.0 or higher
- Virtualenv (optional but recommended)

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/annotations_manager.git
   cd annotations_manager
   git checkout newBranch
   ```

2. Create a virtual environment (optional):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/MacOS
   venv\Scripts\activate    # For Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser (This is the admin who can create user accounts):
     
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Access the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Project Structure

The following is the structure of the project:

```
annotations_manager
├─ .vscode/                # IDE configuration files
│  └─ settings.json
├─ .gitignore
├─ annotations_manager/    # Core project settings
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ __init__.py
├─ core/                     # Main application logic
│  ├─ admin.py               # Admin panel configurations
│  ├─ apps.py                # App configuration
│  ├─ decorators.py          # Custom decorators
│  ├─ forms.py               # Django forms
│  ├─ keypoint_prediction.py # Code for key point prediction
│  ├─ middleware.py          # Custom middleware
│  ├─ models.py              # Database models
│  ├─ templates/             # HTML templates
│  │  ├─ base.html           # Base template
│  │  └─ core
│  │     ├─ admin_dashboard.html
│  │     ├─ annotator_dashboard.html
│  │     ├─ create_annotation.html
│  │     ├─ create_user.html
│  │     ├─ dashboard.html
│  │     ├─ edit_annotation.html
│  │     ├─ login.html
│  │     ├─ upload_image.html
│  │     ├─ verifier_dashboard.html
│  │     ├─ verify_annotation.html
│  │     └─ viewer_dashboard.html
│  ├─ urls.py              # Application-specific URL routes
│  ├─ views.py             # Views and request handlers
│  └─ migrations/          # Database migration files
├─ db.sqlite3              # SQLite database (default, replaceable)
├─ manage.py               # Django management script
├─ media/                  # Uploaded files
│  ├─ images/              # Uploaded images
│  ├─ pending_verifications/ # Annotation files (JSON) and images
│  └─ verified_annotations/
├─ static/                 # Static files (CSS, JS, etc.)
│  ├─ css/
│  └─ js/
├─ templates/              # Error pages
│  ├─ 404.html
│  └─ 500.html
└─ README.md               # Project documentation
├─ requirements.txt
├─ templates
│  ├─ 404.html
│  └─ 500.html
└─ weights
   └─ best26.pt
```

---

## Usage

### User Roles

- **Admin**:

  - Create and manage user accounts.
  - Monitor the system through the admin dashboard.

- **Annotator**:

  - Access images for annotation.
  - Submit annotations for verification.

- **Verifier**:

  - Review and approve/reject annotations.
  - Provide feedback to annotators.

- **Viewer**:
  - View verified annotations and corresponding images.

### Annotation Workflow

1. **Upload Images**: Admin uploads images to the system.
2. **Annotate**: Annotators create annotations and submit them for verification.
3. **Verify**: Verifiers review the annotations, approve or provide feedback.
4. **View Results**: Verified annotations are accessible to viewers.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions or support, contact [your-email@example.com](mailto:your-email@example.com).
