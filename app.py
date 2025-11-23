import os
import json
from datetime import datetime, timedelta
from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file
from models import db, Category, Person, Task, Note
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/app')
def app_main():
    return render_template('index.html')

# --- API: INIT ---
@app.route('/api/init', methods=['GET'])
def get_init_data():
    # Return hierarchical data for the matrix
    categories = Category.query.order_by(Category.order).all()
    people = Person.query.all()
    
    # We want tasks grouped by category
    cats_data = []
    for cat in categories:
        c_dict = cat.to_dict()
        # Tasks are already ordered by 'order' due to relationship definition
        c_dict['tasks'] = [t.to_dict() for t in cat.tasks]
        cats_data.append(c_dict)
        
    return jsonify({
        'categories': cats_data,
        'people': [p.to_dict() for p in people]
    })

# --- API: CATEGORIES ---
@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    # Auto-increment order
    max_order = db.session.query(db.func.max(Category.order)).scalar() or 0
    new_cat = Category(name=data['name'], color=data['color'], order=max_order + 1)
    db.session.add(new_cat)
    db.session.commit()
    return jsonify(new_cat.to_dict()), 201

@app.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    cat = Category.query.get_or_404(id)
    data = request.json
    if 'name' in data: cat.name = data['name']
    if 'color' in data: cat.color = data['color']
    if 'order' in data: cat.order = data['order']
    db.session.commit()
    return jsonify(cat.to_dict())

@app.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})

# --- API: PEOPLE ---
@app.route('/api/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    return jsonify([p.to_dict() for p in people])

@app.route('/api/people', methods=['POST'])
def create_person():
    data = request.json
    new_person = Person(name=data['name'])
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.to_dict()), 201

@app.route('/api/people/<int:id>', methods=['DELETE'])
def delete_person(id):
    person = Person.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    return jsonify({'success': True})

# --- API: TASKS ---
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    # Auto-increment order within category
    max_order = db.session.query(db.func.max(Task.order)).filter_by(category_id=data['category_id']).scalar() or 0
    
    new_task = Task(
        category_id=data['category_id'],
        text=data['text'],
        person_id=data.get('person_id'),
        order=max_order + 1
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.json
    if 'text' in data: task.text = data['text']
    if 'done' in data: task.done = data['done']
    if 'person_id' in data: task.person_id = data['person_id']
    if 'order' in data: task.order = data['order']
    db.session.commit()
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})

# --- API: NOTES ---
@app.route('/api/notes', methods=['GET'])
def get_notes():
    # Return notes for a specific range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Note.query
    if start_date and end_date:
        query = query.filter(Note.date >= start_date, Note.date <= end_date)
    
    notes = query.all()
    return jsonify([n.to_dict() for n in notes])

@app.route('/api/notes', methods=['POST'])
def upsert_note():
    data = request.json
    task_id = data['task_id']
    date = data['date']
    content = data['content']
    
    note = Note.query.filter_by(task_id=task_id, date=date).first()
    if note:
        note.content = content
    else:
        note = Note(task_id=task_id, date=date, content=content)
        db.session.add(note)
    
    db.session.commit()
    return jsonify(note.to_dict())

# --- API: BACKUP / RESTORE ---
@app.route('/api/backup', methods=['GET'])
def backup_db():
    data = {
        'categories': [c.to_dict() for c in Category.query.all()],
        'people': [p.to_dict() for p in Person.query.all()],
        'tasks': [t.to_dict() for t in Task.query.all()],
        'notes': [n.to_dict() for n in Note.query.all()]
    }
    return jsonify(data)

@app.route('/api/restore', methods=['POST'])
def restore_db():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    try:
        Note.query.delete()
        Task.query.delete()
        Person.query.delete()
        Category.query.delete()
        
        for c_data in data.get('categories', []):
            cat = Category(name=c_data['name'], color=c_data['color'], order=c_data.get('order', 0))
            cat.id = c_data['id']
            db.session.add(cat)
            
        for p_data in data.get('people', []):
            p = Person(name=p_data['name'])
            p.id = p_data['id']
            db.session.add(p)
            
        for t_data in data.get('tasks', []):
            t = Task(
                category_id=t_data['category_id'],
                person_id=t_data['person_id'],
                text=t_data['text'],
                done=t_data['done'],
                order=t_data.get('order', 0)
            )
            t.id = t_data['id']
            db.session.add(t)
            
        for n_data in data.get('notes', []):
            n = Note(
                task_id=n_data['task_id'],
                date=n_data['date'],
                content=n_data['content']
            )
            n.id = n_data['id']
            db.session.add(n)
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# --- API: PDF EXPORT ---
@app.route('/api/export-pdf', methods=['GET'])
def export_pdf():
    """Generate a print-friendly PDF with Category, Who?, and Task columns"""
    try:
        # Get current week info from query params or default to current week
        week_start_str = request.args.get('week_start')
        if week_start_str:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d')
        else:
            # Default to last Friday
            today = datetime.now()
            day = today.weekday()
            diff = (day + 2) % 7
            week_start = today - timedelta(days=diff)
        
        week_end = week_start + timedelta(days=6)
        
        # Fetch all categories with tasks
        categories = Category.query.order_by(Category.order).all()
        people_dict = {p.id: p.name for p in Person.query.all()}
        
        # Fetch notes for the current week
        notes = Note.query.filter(
            Note.date >= week_start.strftime('%Y-%m-%d'),
            Note.date <= week_end.strftime('%Y-%m-%d')
        ).all()
        notes_by_task = {}
        for note in notes:
            if note.task_id not in notes_by_task:
                notes_by_task[note.task_id] = []
            notes_by_task[note.task_id].append(note)
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               topMargin=0.5*inch, bottomMargin=0.5*inch,
                               leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        month_style = ParagraphStyle(
            'MonthStyle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#d63384'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        week_style = ParagraphStyle(
            'WeekStyle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.darkgray,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        category_style = ParagraphStyle(
            'CategoryStyle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            leftIndent=0
        )
        
        task_style = ParagraphStyle(
            'TaskStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            leftIndent=20,
            spaceAfter=4
        )
        
        note_style = ParagraphStyle(
            'NoteStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#3498db'),
            leftIndent=20
        )
        
        # Header with just Month and Week
        month_names = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
                      "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
        month_text = f"{month_names[week_start.month - 1]} {week_start.year}"
        elements.append(Paragraph(month_text, month_style))
        
        days_short = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        week_text = f"{days_short[week_start.weekday()]} {week_start.day} - {days_short[week_end.weekday()]} {week_end.day}"
        elements.append(Paragraph(week_text, week_style))
        
        # Content - Categories and Tasks
        for category in categories:
            if len(category.tasks) == 0:
                continue
                
            # Category header
            elements.append(Paragraph(category.name.upper(), category_style))
            
            # Tasks under this category
            for task in category.tasks:
                # Task line with WHO? and text
                who = people_dict.get(task.person_id, '--')
                task_text = f"<b>[{who}]</b> {task.text}"
                if task.done:
                    task_text = f"<strike>{task_text}</strike>"
                elements.append(Paragraph(task_text, task_style))
                
                # Note previews for this task
                if task.id in notes_by_task:
                    for note in notes_by_task[task.id]:
                        if note.content.strip():
                            note_date = datetime.strptime(note.date, '%Y-%m-%d')
                            day_name = days_short[note_date.weekday()]
                            note_text = f"({day_name} {note_date.day}) {note.content}"
                            elements.append(Paragraph(note_text, note_style))
                
                elements.append(Spacer(1, 0.1*inch))
        
        # Footer - App name small at bottom
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceBefore=20
        )
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("SEB OPS SYSTEM v5", footer_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF from buffer
        buffer.seek(0)
        
        # Generate filename with date
        filename = f"SEB_OPS_{week_start.strftime('%Y-%m-%d')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=False
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
