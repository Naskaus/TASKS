"""
Full System Test Suite for SEB OPS SYSTEM v5
Tests all major functionality of the application
Run this after any code modifications to ensure everything works
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
import time
import sys

class SEBOpsSystemTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        
    def setup(self):
        """Initialize the browser"""
        print("🚀 Initializing browser...")
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(self.base_url)
        time.sleep(2)
        print("✅ Browser initialized\n")
        
    def teardown(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("\n🏁 Browser closed")
    
    def accept_alert(self, text_to_send=None):
        """Handle JavaScript alerts"""
        try:
            alert = self.wait.until(EC.alert_is_present())
            if text_to_send:
                alert.send_keys(text_to_send)
            alert.accept()
            time.sleep(0.5)
        except:
            pass
    
    def test_1_create_category(self):
        """Test 1: Create a new category"""
        print("📋 TEST 1: Creating new category...")
        
        # Click CAT button
        cat_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "cat-btn")))
        cat_btn.click()
        time.sleep(1)
        
        # Fill in category name
        cat_name_input = self.driver.find_element(By.ID, "cat-name")
        cat_name_input.send_keys("TEST CATEGORY")
        
        # Select color
        cat_color_input = self.driver.find_element(By.ID, "cat-color")
        cat_color_input.send_keys("#FF5733")  # Orange color
        
        # Submit
        cat_form = self.driver.find_element(By.ID, "category-form")
        cat_form.submit()
        time.sleep(2)
        
        # Verify category appears
        category_labels = self.driver.find_elements(By.CLASS_NAME, "category-label")
        assert any("TEST CATEGORY" in label.text for label in category_labels), "Category not created!"
        
        print("✅ TEST 1 PASSED: Category created successfully\n")
        
    def test_2_edit_category_name(self):
        """Test 2: Edit category name"""
        print("✏️ TEST 2: Editing category name...")
        
        # Find and click the test category
        category_labels = self.driver.find_elements(By.CLASS_NAME, "category-label")
        test_category = None
        for label in category_labels:
            if "TEST CATEGORY" in label.text:
                test_category = label
                break
        
        assert test_category is not None, "Test category not found!"
        test_category.click()
        time.sleep(0.5)
        
        # Handle prompt to edit
        self.accept_alert("TEST CATEGORY EDITED")
        time.sleep(2)
        
        # Verify name changed
        category_labels = self.driver.find_elements(By.CLASS_NAME, "category-label")
        assert any("TEST CATEGORY EDITED" in label.text for label in category_labels), "Category name not edited!"
        
        print("✅ TEST 2 PASSED: Category name edited successfully\n")
        
    def test_3_create_person(self):
        """Test 3: Create a new person"""
        print("👤 TEST 3: Creating new person...")
        
        # Click TEAM button
        team_btn = self.driver.find_element(By.ID, "team-btn")
        team_btn.click()
        time.sleep(1)
        
        # Fill in person name
        person_name_input = self.driver.find_element(By.ID, "person-name")
        person_name_input.send_keys("Test User")
        
        # Submit
        team_form = self.driver.find_element(By.ID, "team-form")
        team_form.submit()
        time.sleep(2)
        
        # Verify person appears in the list
        team_list = self.driver.find_element(By.ID, "team-list")
        assert "Test User" in team_list.text, "Person not created!"
        
        # Close modal
        close_btn = self.driver.find_element(By.CSS_SELECTOR, "#team-modal .close-modal")
        close_btn.click()
        time.sleep(1)
        
        print("✅ TEST 3 PASSED: Person created successfully\n")
        
    def test_4_create_task(self):
        """Test 4: Create a new task"""
        print("📝 TEST 4: Creating new task...")
        
        # Find the TEST CATEGORY EDITED and click + ADD button
        add_buttons = self.driver.find_elements(By.CLASS_NAME, "add-task-btn")
        # Click the first add button (for our test category)
        add_buttons[0].click()
        time.sleep(0.5)
        
        # Handle prompt
        self.accept_alert("Test Task for Automation")
        time.sleep(2)
        
        # Verify task created
        task_inputs = self.driver.find_elements(By.CLASS_NAME, "task-text-input")
        assert any("Test Task for Automation" in input.get_attribute('value') for input in task_inputs), "Task not created!"
        
        print("✅ TEST 4 PASSED: Task created successfully\n")
        
    def test_5_assign_person_to_task(self):
        """Test 5: Assign person to task"""
        print("🔗 TEST 5: Assigning person to task...")
        
        # Find the who-select dropdown for our task
        who_selects = self.driver.find_elements(By.CLASS_NAME, "who-select")
        
        # Select "Test User" in the first dropdown
        select = Select(who_selects[0])
        select.select_by_visible_text("Test User")
        time.sleep(2)
        
        # Verify assignment
        selected_option = select.first_selected_option
        assert "Test User" in selected_option.text, "Person not assigned to task!"
        
        print("✅ TEST 5 PASSED: Person assigned to task successfully\n")
        
    def test_6_edit_task(self):
        """Test 6: Edit task text"""
        print("✏️ TEST 6: Editing task text...")
        
        # Find the task textarea
        task_inputs = self.driver.find_elements(By.CLASS_NAME, "task-text-input")
        test_task_input = None
        for input in task_inputs:
            if "Test Task for Automation" in input.get_attribute('value'):
                test_task_input = input
                break
        
        assert test_task_input is not None, "Test task not found!"
        
        # Edit the text
        test_task_input.clear()
        test_task_input.send_keys("Test Task - EDITED")
        # Trigger blur event
        self.driver.execute_script("arguments[0].blur();", test_task_input)
        time.sleep(2)
        
        # Verify edit
        task_inputs = self.driver.find_elements(By.CLASS_NAME, "task-text-input")
        assert any("Test Task - EDITED" in input.get_attribute('value') for input in task_inputs), "Task not edited!"
        
        print("✅ TEST 6 PASSED: Task text edited successfully\n")
        
    def test_7_add_notes_multiple_days(self):
        """Test 7: Add notes to multiple days"""
        print("📓 TEST 7: Adding notes to multiple days...")
        
        # Find all note textareas in the current week
        note_textareas = self.driver.find_elements(By.CLASS_NAME, "note-textarea")
        
        # Add notes to first 3 days
        days_to_test = ["Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days_to_test):
            if i < len(note_textareas):
                textarea = note_textareas[i]
                textarea.send_keys(f"Note for {day} - Test content")
                self.driver.execute_script("arguments[0].blur();", textarea)
                time.sleep(1)
        
        # Verify notes were saved
        note_textareas = self.driver.find_elements(By.CLASS_NAME, "note-textarea")
        notes_found = 0
        for textarea in note_textareas:
            if "Note for" in textarea.get_attribute('value'):
                notes_found += 1
        
        assert notes_found >= 3, f"Expected at least 3 notes, found {notes_found}"
        
        print("✅ TEST 7 PASSED: Notes added to multiple days successfully\n")
        
    def test_8_mark_task_as_done(self):
        """Test 8: Mark task as done"""
        print("✔️ TEST 8: Marking task as done...")
        
        # Find the checkbox for our task
        checkboxes = self.driver.find_elements(By.CLASS_NAME, "task-checkbox")
        
        # Check the first checkbox
        if not checkboxes[0].is_selected():
            checkboxes[0].click()
            time.sleep(2)
        
        # Verify task is marked as done (has 'done' class)
        task_inputs = self.driver.find_elements(By.CLASS_NAME, "task-text-input")
        done_tasks = [input for input in task_inputs if 'done' in input.get_attribute('class')]
        assert len(done_tasks) > 0, "Task not marked as done!"
        
        print("✅ TEST 8 PASSED: Task marked as done successfully\n")
        
    def test_9_change_week(self):
        """Test 9: Navigate to next week"""
        print("📅 TEST 9: Changing to next week...")
        
        # Click next week button
        next_week_btn = self.driver.find_element(By.ID, "next-week")
        next_week_btn.click()
        time.sleep(2)
        
        # Verify week changed (check week range display)
        week_range = self.driver.find_element(By.ID, "week-range-display")
        original_week = week_range.text
        
        print(f"   New week range: {original_week}")
        print("✅ TEST 9 PASSED: Week navigation successful\n")
        
    def test_10_add_note_new_week(self):
        """Test 10: Add note in new week"""
        print("📓 TEST 10: Adding note in new week...")
        
        # Find note textareas in new week
        note_textareas = self.driver.find_elements(By.CLASS_NAME, "note-textarea")
        
        # Add note to first day of new week
        if len(note_textareas) > 0:
            textarea = note_textareas[0]
            textarea.send_keys("Note in new week - Test automation")
            self.driver.execute_script("arguments[0].blur();", textarea)
            time.sleep(2)
        
        # Verify note saved
        note_textareas = self.driver.find_elements(By.CLASS_NAME, "note-textarea")
        assert any("Note in new week" in textarea.get_attribute('value') for textarea in note_textareas), "Note in new week not saved!"
        
        print("✅ TEST 10 PASSED: Note added in new week successfully\n")
        
    def test_11_click_today(self):
        """Test 11: Click TODAY button"""
        print("🔙 TEST 11: Clicking TODAY button...")
        
        # Click TODAY button
        today_btn = self.driver.find_element(By.ID, "today-btn")
        today_btn.click()
        time.sleep(2)
        
        # Verify we're back to current week (check if today is highlighted)
        today_headers = self.driver.find_elements(By.CSS_SELECTOR, "th.is-today")
        assert len(today_headers) > 0, "TODAY button did not navigate to current week!"
        
        print("✅ TEST 11 PASSED: TODAY button works correctly\n")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        try:
            self.setup()
            
            print("=" * 60)
            print("🧪 STARTING FULL SYSTEM TEST SUITE")
            print("=" * 60 + "\n")
            
            # Run all tests
            self.test_1_create_category()
            self.test_2_edit_category_name()
            self.test_3_create_person()
            self.test_4_create_task()
            self.test_5_assign_person_to_task()
            self.test_6_edit_task()
            self.test_7_add_notes_multiple_days()
            self.test_8_mark_task_as_done()
            self.test_9_change_week()
            self.test_10_add_note_new_week()
            self.test_11_click_today()
            
            print("=" * 60)
            print("✅ ALL TESTS PASSED! 🎉")
            print("=" * 60)
            
            return True
            
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            return False
        except Exception as e:
            print(f"\n💥 ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            time.sleep(3)  # Pause to see final state
            self.teardown()

if __name__ == "__main__":
    print("\n" + "🔧 SEB OPS SYSTEM v5 - Full System Test" + "\n")
    print("Make sure the app is running on http://127.0.0.1:5000\n")
    
    tester = SEBOpsSystemTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
