from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50), nullable=False) # css class or hex
    order = db.Column(db.Integer, default=0)
    tasks = relationship('Task', backref='category', cascade="all, delete-orphan", order_by='Task.order')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'order': self.order
        }

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = relationship('Task', backref='person')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    text = db.Column(db.String(500), nullable=False)
    done = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    notes = relationship('Note', backref='task', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'person_id': self.person_id,
            'text': self.text,
            'done': self.done,
            'order': self.order
        }

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    content = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'date': self.date,
            'content': self.content
        }
