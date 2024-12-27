from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_key")  # Required for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///test.db")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(50), nullable=False)  # Unique for each user

    def __repr__(self):
        return f'<Task {self.id}>'

@app.before_request
def set_user_session():
    """Set a unique session ID for each user."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/', methods=['POST', 'GET'])
def index():
    """Main route for displaying tasks."""
    user_id = session['user_id']
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content, session_id=user_id)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an issue adding your task: {e}"

    else:
        tasks = Todo.query.filter_by(session_id=user_id).order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    """Delete a task."""
    user_id = session['user_id']
    task_to_delete = Todo.query.filter_by(id=id, session_id=user_id).first_or_404()

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"There was an issue deleting your task: {e}"

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    """Update a task."""
    user_id = session['user_id']
    task = Todo.query.filter_by(id=id, session_id=user_id).first_or_404()

    if request.method == 'POST':
        task.content = request.form['content']
        task.date_created = datetime.strptime(request.form['date_created'], '%Y-%m-%d')


        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an issue updating your task: {e}"
    else:
        return render_template('update.html', task=task)

if __name__ == '__main__':
    app.run(debug=True)
