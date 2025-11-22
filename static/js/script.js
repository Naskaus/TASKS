document.addEventListener('DOMContentLoaded', () => {
    // State
    let state = {
        categories: [],
        people: [],
        notes: [],
        currentWeekStart: getLastFriday(new Date())
    };

    // DOM Elements
    const matrixBody = document.getElementById('matrix-body');
    const monthYearDisplay = document.getElementById('month-year-display');
    const weekRangeDisplay = document.getElementById('week-range-display');
    const dayHeaders = document.querySelectorAll('.col-day');

    // Init
    init();

    function init() {
        state.currentWeekStart = getLastFriday(new Date());
        fetchInitData();
        setupEventListeners();
    }

    async function fetchInitData() {
        try {
            const response = await fetch('/api/init');
            const data = await response.json();
            state.categories = data.categories;
            state.people = data.people;
            await fetchNotes();
            renderMatrix();
        } catch (error) {
            console.error('Error fetching init data:', error);
        }
    }

    async function fetchNotes() {
        const start = formatDate(state.currentWeekStart);
        const end = formatDate(addDays(state.currentWeekStart, 6));
        try {
            const response = await fetch(`/api/notes?start_date=${start}&end_date=${end}`);
            state.notes = await response.json();
        } catch (error) {
            console.error('Error fetching notes:', error);
        }
    }

    // --- Rendering ---
    function renderMatrix() {
        updateHeaderDates();
        matrixBody.innerHTML = '';

        state.categories.forEach((cat, catIndex) => {
            const tasks = cat.tasks;
            const renderTasks = tasks.length > 0 ? tasks : [null];

            renderTasks.forEach((task, index) => {
                const tr = document.createElement('tr');
                tr.className = catIndex % 2 === 0 ? 'row-even' : 'row-odd';

                // Category Cell
                if (index === 0) {
                    const catCell = document.createElement('td');
                    catCell.className = 'category-cell';
                    catCell.rowSpan = renderTasks.length;
                    catCell.innerHTML = `
                        <div class="category-label" style="background-color: ${cat.color}; border-color: ${cat.color}" onclick="editCategory(${cat.id})">
                            ${cat.name} <i class="fas fa-pen" style="font-size: 0.8em; opacity: 0.5; margin-left: 5px;"></i>
                        </div>
                        <button class="add-task-btn" data-category-id="${cat.id}">+ ADD</button>
                    `;
                    // Attach event listener after rendering
                    const addBtn = catCell.querySelector('.add-task-btn');
                    if (addBtn) addBtn.addEventListener('click', () => window.addTask(cat.id));
                    tr.appendChild(catCell);
                }

                // Who Cell
                const whoCell = document.createElement('td');
                whoCell.innerHTML = renderPersonSelect(task);
                tr.appendChild(whoCell);

                // Task Cell
                const taskCell = document.createElement('td');
                let taskNotesHtml = '';

                if (task) {
                    // Collect notes for preview
                    for (let i = 0; i < 4; i++) {
                        const date = addDays(state.currentWeekStart, i);
                        const dateStr = formatDate(date);
                        const note = state.notes.find(n => n.task_id === task.id && n.date === dateStr);
                        if (note && note.content.trim() !== '') {
                            const dayName = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][date.getDay()];
                            taskNotesHtml += `<div class="task-note-preview"><span class="note-date">(${dayName} ${date.getDate()})</span> ${note.content}</div>`;
                        }
                    }

                    taskCell.innerHTML = `
                        <div class="task-input-container">
                            <div class="task-main-row">
                                <input type="checkbox" class="task-checkbox" ${task.done ? 'checked' : ''} onchange="toggleTask(${task.id}, this.checked)">
                                <textarea class="task-text-input ${task.done ? 'done' : ''}" onblur="updateTaskText(${task.id}, this.value)" rows="1">${task.text}</textarea>
                                <i class="fas fa-trash" data-task-id="${task.id}" style="cursor:pointer; color:#444; font-size:10px;"></i>
                            </div>
                            <div class="task-notes-container">
                                ${taskNotesHtml}
                            </div>
                        </div>
                    `;
                    // Attach delete event listener
                    const deleteIcon = taskCell.querySelector('.fa-trash');
                    if (deleteIcon) deleteIcon.addEventListener('click', () => window.deleteTask(task.id));
                } else {
                    taskCell.innerHTML = '<span style="color:#444; font-style:italic; font-size:11px;">No tasks</span>';
                }
                tr.appendChild(taskCell);

                // Day Cells (4 days instead of 7)
                for (let i = 0; i < 4; i++) {
                    const dayCell = document.createElement('td');
                    dayCell.className = 'note-cell';

                    if (task) {
                        const date = addDays(state.currentWeekStart, i);
                        const dateStr = formatDate(date);
                        const note = state.notes.find(n => n.task_id === task.id && n.date === dateStr);
                        dayCell.innerHTML = `<textarea class="note-textarea" data-task-id="${task.id}" data-date="${dateStr}" onblur="saveNote(this)">${note ? note.content : ''}</textarea>`;
                    }
                    tr.appendChild(dayCell);
                }

                matrixBody.appendChild(tr);
            });
        });
    }

    function renderPersonSelect(task) {
        if (!task) return '';
        let options = '<option value="">--</option>';
        state.people.forEach(p => {
            const selected = task.person_id === p.id ? 'selected' : '';
            options += `<option value="${p.id}" ${selected}>${p.name}</option>`;
        });
        return `<select class="who-select" onchange="updateTaskPerson(${task.id}, this.value)">${options}</select>`;
    }

    function updateHeaderDates() {
        const start = state.currentWeekStart;
        const end = addDays(start, 6);
        const monthNames = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"];
        monthYearDisplay.textContent = `${monthNames[start.getMonth()]} ${start.getFullYear()}`;
        const daysShort = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        weekRangeDisplay.textContent = `${daysShort[start.getDay()]} ${start.getDate()} - ${daysShort[end.getDay()]} ${end.getDate()}`;

        dayHeaders.forEach((th, index) => {
            const date = addDays(start, index);
            th.textContent = `${daysShort[date.getDay()].toUpperCase()} ${date.getDate()}`;
            const today = new Date();
            if (date.toDateString() === today.toDateString()) {
                th.classList.add('is-today');
            } else {
                th.classList.remove('is-today');
            }
        });
    }

    // --- Actions ---
    window.addTask = async (categoryId) => {
        const text = prompt("New Task Description:");
        if (!text) return;
        try {
            await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category_id: categoryId, text: text })
            });
            fetchInitData();
        } catch (error) {
            console.error(error);
            alert("Error adding task");
        }
    };

    window.editCategory = async (id) => {
        const cat = state.categories.find(c => c.id === id);
        if (!cat) return;
        const newName = prompt("Edit Category Name:", cat.name);
        if (newName !== null && newName !== cat.name) {
            try {
                await fetch(`/api/categories/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: newName })
                });
                fetchInitData();
            } catch (error) {
                console.error(error);
                alert("Error updating category");
            }
        }
    };

    window.toggleTask = async (id, done) => {
        await updateTask(id, { done });
        const input = document.querySelector(`textarea[onblur="updateTaskText(${id}, this.value)"]`);
        if (input) {
            if (done) input.classList.add('done');
            else input.classList.remove('done');
        }
    };

    window.updateTaskText = async (id, text) => {
        await updateTask(id, { text });
    };

    window.updateTaskPerson = async (id, personId) => {
        await updateTask(id, { person_id: personId || null });
    };

    async function updateTask(id, payload) {
        try {
            await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } catch (error) {
            console.error(error);
        }
    }

    window.deleteTask = async (id) => {
        if (!confirm("Delete task?")) return;
        try {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            fetchInitData();
        } catch (error) {
            console.error(error);
            alert("Error deleting task");
        }
    };

    window.saveNote = async (textarea) => {
        const taskId = textarea.dataset.taskId;
        const date = textarea.dataset.date;
        const content = textarea.value;
        try {
            await fetch('/api/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_id: taskId, date, content })
            });
            const existing = state.notes.find(n => n.task_id == taskId && n.date == date);
            if (existing) existing.content = content;
            else state.notes.push({ task_id: taskId, date, content });
        } catch (error) {
            console.error(error);
        }
    };

    // --- Helpers ---
    function getLastFriday(d) {
        d = new Date(d);
        const day = d.getDay();
        const diff = (day + 2) % 7;
        const date = new Date(d);
        date.setDate(d.getDate() - diff);
        return date;
    }

    function addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    function setupEventListeners() {
        document.getElementById('prev-week').addEventListener('click', () => {
            state.currentWeekStart = addDays(state.currentWeekStart, -7);
            renderMatrix();
            fetchNotes().then(renderMatrix);
        });

        document.getElementById('next-week').addEventListener('click', () => {
            state.currentWeekStart = addDays(state.currentWeekStart, 7);
            renderMatrix();
            fetchNotes().then(renderMatrix);
        });

        document.getElementById('today-btn').addEventListener('click', () => {
            state.currentWeekStart = getLastFriday(new Date());
            renderMatrix();
            fetchNotes().then(renderMatrix);
        });

        const catModal = document.getElementById('category-modal');
        const teamModal = document.getElementById('team-modal');

        document.getElementById('cat-btn').addEventListener('click', () => {
            renderManageList('category-list', state.categories, deleteCategory);
            catModal.style.display = 'flex';
        });

        document.getElementById('team-btn').addEventListener('click', () => {
            renderManageList('team-list', state.people, deletePerson);
            teamModal.style.display = 'flex';
        });

        document.querySelectorAll('.close-modal').forEach(b => {
            b.addEventListener('click', () => {
                catModal.style.display = 'none';
                teamModal.style.display = 'none';
            });
        });

        document.getElementById('save-btn').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/backup');
                const data = await response.json();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'seb_ops_backup.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (error) {
                console.error(error);
                alert("Error backing up data");
            }
        });

        document.getElementById('load-btn').addEventListener('click', () => {
            document.getElementById('restore-file-input').click();
        });

        document.getElementById('restore-file-input').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = async (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    const res = await fetch('/api/restore', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    if (res.ok) {
                        alert('Restore successful!');
                        location.reload();
                    } else {
                        alert('Restore failed.');
                    }
                } catch (error) {
                    console.error(error);
                    alert('Invalid backup file.');
                }
            };
            reader.readAsText(file);
        });

        document.getElementById('pdf-btn').addEventListener('click', () => {
            // Open PDF in new tab (fullscreen)
            const week_start = formatDate(state.currentWeekStart);
            const pdfUrl = `/api/export-pdf?week_start=${week_start}`;
            window.open(pdfUrl, '_blank');
        });

        document.getElementById('category-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('cat-name').value;
            const color = document.getElementById('cat-color').value;
            try {
                await fetch('/api/categories', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, color })
                });
                fetchInitData();
                catModal.style.display = 'none';
                document.getElementById('category-form').reset();
            } catch (error) {
                console.error(error);
                alert("Error creating category");
            }
        });

        document.getElementById('team-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('person-name').value;
            try {
                await fetch('/api/people', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                fetchInitData();
                teamModal.style.display = 'none';
                document.getElementById('team-form').reset();
            } catch (error) {
                console.error(error);
                alert("Error adding person");
            }
        });
    }

    function renderManageList(elementId, items, deleteFn) {
        const list = document.getElementById(elementId);
        list.innerHTML = '';
        items.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${item.name}</span> <i class="fas fa-trash"></i>`;
            li.querySelector('i').onclick = () => deleteFn(item.id);
            list.appendChild(li);
        });
    }

    window.deleteCategory = async (id) => {
        if (!confirm("Delete category?")) return;
        try {
            await fetch(`/api/categories/${id}`, { method: 'DELETE' });
            fetchInitData();
            document.getElementById('category-modal').style.display = 'none';
        } catch (error) {
            console.error(error);
            alert("Error deleting category");
        }
    };

    window.deletePerson = async (id) => {
        if (!confirm("Delete person?")) return;
        try {
            await fetch(`/api/people/${id}`, { method: 'DELETE' });
            await fetchInitData();
            // Re-render the team list to update the modal
            renderManageList('team-list', state.people, deletePerson);
        } catch (error) {
            console.error(error);
            alert("Error deleting person");
        }
    };
});
