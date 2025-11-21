import unittest
import requests
import time
import subprocess
import sys
import os

BASE_URL = "http://127.0.0.1:5000"

class TestSebOpsAPI(unittest.TestCase):
    def setUp(self):
        # Ensure the server is up
        try:
            requests.get(BASE_URL)
        except requests.exceptions.ConnectionError:
            self.fail("Server is not running. Please start app.py first.")

    def test_01_init_empty(self):
        print("\nTesting Initial State...")
        response = requests.get(f"{BASE_URL}/api/init")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue('categories' in data)
        self.assertTrue('people' in data)

    def test_02_create_category(self):
        print("\nTesting Create Category...")
        payload = {"name": "Test Category", "color": "#ff0000"}
        response = requests.post(f"{BASE_URL}/api/categories", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], "Test Category")
        self.assertTrue('id' in data)
        self.__class__.cat_id = data['id']

    def test_03_create_person(self):
        print("\nTesting Create Person...")
        payload = {"name": "Test Person"}
        response = requests.post(f"{BASE_URL}/api/people", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['name'], "Test Person")
        self.__class__.person_id = data['id']

    def test_04_create_task(self):
        print("\nTesting Create Task...")
        if not hasattr(self.__class__, 'cat_id'):
            self.skipTest("Skipping task creation: No category created")
        
        payload = {"category_id": self.__class__.cat_id, "text": "Test Task"}
        response = requests.post(f"{BASE_URL}/api/tasks", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['text'], "Test Task")
        self.__class__.task_id = data['id']

    def test_05_update_task(self):
        print("\nTesting Update Task (Assign Person)...")
        if not hasattr(self.__class__, 'task_id') or not hasattr(self.__class__, 'person_id'):
            self.skipTest("Skipping task update: Missing task or person")

        payload = {"person_id": self.__class__.person_id, "done": True}
        response = requests.put(f"{BASE_URL}/api/tasks/{self.__class__.task_id}", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['person_id'], self.__class__.person_id)
        self.assertEqual(data['done'], True)

    def test_06_verify_init_structure(self):
        print("\nTesting Matrix Data Structure...")
        response = requests.get(f"{BASE_URL}/api/init")
        data = response.json()
        
        # Find our category
        cat = next((c for c in data['categories'] if c['id'] == self.__class__.cat_id), None)
        self.assertIsNotNone(cat)
        
        # Check nested tasks
        self.assertTrue('tasks' in cat)
        self.assertEqual(len(cat['tasks']), 1)
        self.assertEqual(cat['tasks'][0]['id'], self.__class__.task_id)

    def test_07_notes(self):
        print("\nTesting Notes...")
        if not hasattr(self.__class__, 'task_id'):
            self.skipTest("Skipping notes: No task")
            
        date_str = "2025-01-01"
        payload = {"task_id": self.__class__.task_id, "date": date_str, "content": "Test Note"}
        
        # Create/Update Note
        response = requests.post(f"{BASE_URL}/api/notes", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Fetch Notes
        response = requests.get(f"{BASE_URL}/api/notes?start_date={date_str}&end_date={date_str}")
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['content'], "Test Note")

if __name__ == '__main__':
    unittest.main()
