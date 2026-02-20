
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from db_config import connect

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.init_database()
        
        # Create UI
        self.create_widgets()
        
        # Load initial data
        self.load_students()
        
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = connect()
            cursor = conn.cursor()
            
            # Create students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    class_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create grades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grades (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                    subject VARCHAR(100) NOT NULL,
                    grade DECIMAL(5,2) NOT NULL,
                    max_marks DECIMAL(5,2) DEFAULT 100,
                    exam_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error initializing database: {str(e)}")
    
    def create_widgets(self):
        """Create the main UI components"""
        # Title
        title_label = tk.Label(self.root, text="Student Management System", 
                              font=("Arial", 20, "bold"), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_students_tab()
        self.create_grades_tab()
        self.create_search_tab()
        
    def create_students_tab(self):
        """Create students management tab"""
        students_frame = ttk.Frame(self.notebook)
        self.notebook.add(students_frame, text="Students")
        
        # Input frame
        input_frame = ttk.LabelFrame(students_frame, text="Student Information", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Student form fields
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Email:").grid(row=0, column=2, sticky='w', pady=2)
        self.email_entry = ttk.Entry(input_frame, width=30)
        self.email_entry.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Class:").grid(row=1, column=0, sticky='w', pady=2)
        self.class_entry = ttk.Entry(input_frame, width=30)
        self.class_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Phone:").grid(row=1, column=2, sticky='w', pady=2)
        self.phone_entry = ttk.Entry(input_frame, width=30)
        self.phone_entry.grid(row=1, column=3, padx=5, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(buttons_frame, text="Add Student", command=self.add_student).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Update Student", command=self.update_student).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete Student", command=self.delete_student).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Clear Fields", command=self.clear_student_fields).pack(side='left', padx=5)
        
        # Students list frame
        list_frame = ttk.LabelFrame(students_frame, text="Students List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for students
        self.students_tree = ttk.Treeview(list_frame, columns=('ID', 'Name', 'Email', 'Class', 'Phone'), show='headings')
        self.students_tree.heading('ID', text='ID')
        self.students_tree.heading('Name', text='Name')
        self.students_tree.heading('Email', text='Email')
        self.students_tree.heading('Class', text='Class')
        self.students_tree.heading('Phone', text='Phone')
        
        # Configure column widths
        self.students_tree.column('ID', width=50)
        self.students_tree.column('Name', width=150)
        self.students_tree.column('Email', width=200)
        self.students_tree.column('Class', width=100)
        self.students_tree.column('Phone', width=120)
        
        # Bind selection event
        self.students_tree.bind('<<TreeviewSelect>>', self.on_student_select)
        
        # Scrollbar for students tree
        students_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=students_scrollbar.set)
        
        self.students_tree.pack(side='left', fill='both', expand=True)
        students_scrollbar.pack(side='right', fill='y')
        
    def create_grades_tab(self):
        """Create grades management tab"""
        grades_frame = ttk.Frame(self.notebook)
        self.notebook.add(grades_frame, text="Grades")
        
        # Input frame
        input_frame = ttk.LabelFrame(grades_frame, text="Grade Information", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        # Student selection
        ttk.Label(input_frame, text="Student:").grid(row=0, column=0, sticky='w', pady=2)
        self.student_combo = ttk.Combobox(input_frame, width=30, state='readonly')
        self.student_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Subject:").grid(row=0, column=2, sticky='w', pady=2)
        self.subject_entry = ttk.Entry(input_frame, width=30)
        self.subject_entry.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Grade:").grid(row=1, column=0, sticky='w', pady=2)
        self.grade_entry = ttk.Entry(input_frame, width=30)
        self.grade_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Max Marks:").grid(row=1, column=2, sticky='w', pady=2)
        self.max_marks_entry = ttk.Entry(input_frame, width=30)
        self.max_marks_entry.insert(0, "100")
        self.max_marks_entry.grid(row=1, column=3, padx=5, pady=2)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(buttons_frame, text="Add Grade", command=self.add_grade).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Update Grade", command=self.update_grade).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Delete Grade", command=self.delete_grade).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Clear Fields", command=self.clear_grade_fields).pack(side='left', padx=5)
        
        # Grades list frame
        list_frame = ttk.LabelFrame(grades_frame, text="Grades List", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for grades
        self.grades_tree = ttk.Treeview(list_frame, columns=('ID', 'Student', 'Subject', 'Grade', 'Max Marks', 'Percentage'), show='headings')
        self.grades_tree.heading('ID', text='ID')
        self.grades_tree.heading('Student', text='Student')
        self.grades_tree.heading('Subject', text='Subject')
        self.grades_tree.heading('Grade', text='Grade')
        self.grades_tree.heading('Max Marks', text='Max Marks')
        self.grades_tree.heading('Percentage', text='Percentage')
        
        # Configure column widths
        self.grades_tree.column('ID', width=50)
        self.grades_tree.column('Student', width=150)
        self.grades_tree.column('Subject', width=120)
        self.grades_tree.column('Grade', width=80)
        self.grades_tree.column('Max Marks', width=80)
        self.grades_tree.column('Percentage', width=80)
        
        # Bind selection event
        self.grades_tree.bind('<<TreeviewSelect>>', self.on_grade_select)
        
        # Scrollbar for grades tree
        grades_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.grades_tree.yview)
        self.grades_tree.configure(yscrollcommand=grades_scrollbar.set)
        
        self.grades_tree.pack(side='left', fill='both', expand=True)
        grades_scrollbar.pack(side='right', fill='y')
        
        # Load students for combobox
        self.load_students_combo()
        
    def create_search_tab(self):
        """Create search and filter tab"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search & Filter")
        
        # Search frame
        search_input_frame = ttk.LabelFrame(search_frame, text="Search Options", padding=10)
        search_input_frame.pack(fill='x', padx=10, pady=5)
        
        # Search by student name
        ttk.Label(search_input_frame, text="Search by Name:").grid(row=0, column=0, sticky='w', pady=2)
        self.search_name_entry = ttk.Entry(search_input_frame, width=30)
        self.search_name_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(search_input_frame, text="Search", command=self.search_by_name).grid(row=0, column=2, padx=5)
        
        # Filter by class
        ttk.Label(search_input_frame, text="Filter by Class:").grid(row=1, column=0, sticky='w', pady=2)
        self.filter_class_combo = ttk.Combobox(search_input_frame, width=30)
        self.filter_class_combo.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(search_input_frame, text="Filter", command=self.filter_by_class).grid(row=1, column=2, padx=5)
        
        # Filter by subject
        ttk.Label(search_input_frame, text="Filter by Subject:").grid(row=2, column=0, sticky='w', pady=2)
        self.filter_subject_combo = ttk.Combobox(search_input_frame, width=30)
        self.filter_subject_combo.grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(search_input_frame, text="Filter", command=self.filter_by_subject).grid(row=2, column=2, padx=5)
        
        # Reset button
        ttk.Button(search_input_frame, text="Reset All", command=self.reset_filters).grid(row=3, column=1, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(search_frame, text="Search Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for search results
        self.search_tree = ttk.Treeview(results_frame, columns=('Student', 'Email', 'Class', 'Subject', 'Grade', 'Percentage'), show='headings')
        self.search_tree.heading('Student', text='Student')
        self.search_tree.heading('Email', text='Email')
        self.search_tree.heading('Class', text='Class')
        self.search_tree.heading('Subject', text='Subject')
        self.search_tree.heading('Grade', text='Grade')
        self.search_tree.heading('Percentage', text='Percentage')
        
        # Configure column widths
        self.search_tree.column('Student', width=150)
        self.search_tree.column('Email', width=180)
        self.search_tree.column('Class', width=100)
        self.search_tree.column('Subject', width=120)
        self.search_tree.column('Grade', width=80)
        self.search_tree.column('Percentage', width=80)
        
        # Scrollbar for search tree
        search_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=search_scrollbar.set)
        
        self.search_tree.pack(side='left', fill='both', expand=True)
        search_scrollbar.pack(side='right', fill='y')
        
        # Load filter options
        self.load_filter_options()
    
    # Student operations
    def add_student(self):
        """Add a new student"""
        if not self.validate_student_input():
            return
        
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO students (name, email, class_name, phone)
                VALUES (%s, %s, %s, %s)
            ''', (self.name_entry.get(), self.email_entry.get(), 
                  self.class_entry.get(), self.phone_entry.get()))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Student added successfully!")
            self.clear_student_fields()
            self.load_students()
            self.load_students_combo()
            
        except psycopg2.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding student: {str(e)}")
    
    def update_student(self):
        """Update selected student"""
        selected_item = self.students_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a student to update")
            return
        
        if not self.validate_student_input():
            return
        
        try:
            student_id = self.students_tree.item(selected_item[0])['values'][0]
            
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE students SET name=%s, email=%s, class_name=%s, phone=%s
                WHERE id=%s
            ''', (self.name_entry.get(), self.email_entry.get(), 
                  self.class_entry.get(), self.phone_entry.get(), student_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Student updated successfully!")
            self.clear_student_fields()
            self.load_students()
            self.load_students_combo()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating student: {str(e)}")
    
    def delete_student(self):
        """Delete selected student"""
        selected_item = self.students_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            try:
                student_id = self.students_tree.item(selected_item[0])['values'][0]
                
                conn = connect()
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM students WHERE id=%s', (student_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Student deleted successfully!")
                self.clear_student_fields()
                self.load_students()
                self.load_students_combo()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting student: {str(e)}")
    
    def validate_student_input(self):
        """Validate student input fields"""
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "Name is required")
            return False
        if not self.email_entry.get().strip():
            messagebox.showerror("Error", "Email is required")
            return False
        if not self.class_entry.get().strip():
            messagebox.showerror("Error", "Class is required")
            return False
        return True
    
    def clear_student_fields(self):
        """Clear all student input fields"""
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.class_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
    
    def on_student_select(self, event):
        """Handle student selection"""
        selected_item = self.students_tree.selection()
        if selected_item:
            values = self.students_tree.item(selected_item[0])['values']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, values[2])
            self.class_entry.delete(0, tk.END)
            self.class_entry.insert(0, values[3])
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, values[4] if values[4] else "")
    
    def load_students(self):
        """Load students into the treeview"""
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name, email, class_name, phone FROM students ORDER BY name')
            students = cursor.fetchall()
            
            for student in students:
                self.students_tree.insert('', 'end', values=student)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading students: {str(e)}")
    
    # Grade operations
    def add_grade(self):
        """Add a new grade"""
        if not self.validate_grade_input():
            return
        
        try:
            student_id = self.student_combo.get().split(' - ')[0]
            
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO grades (student_id, subject, grade, max_marks)
                VALUES (%s, %s, %s, %s)
            ''', (student_id, self.subject_entry.get(), 
                  float(self.grade_entry.get()), float(self.max_marks_entry.get())))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Grade added successfully!")
            self.clear_grade_fields()
            self.load_grades()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error adding grade: {str(e)}")
    
    def update_grade(self):
        """Update selected grade"""
        selected_item = self.grades_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a grade to update")
            return
        
        if not self.validate_grade_input():
            return
        
        try:
            grade_id = self.grades_tree.item(selected_item[0])['values'][0]
            student_id = self.student_combo.get().split(' - ')[0]
            
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE grades SET student_id=%s, subject=%s, grade=%s, max_marks=%s
                WHERE id=%s
            ''', (student_id, self.subject_entry.get(), 
                  float(self.grade_entry.get()), float(self.max_marks_entry.get()), grade_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Grade updated successfully!")
            self.clear_grade_fields()
            self.load_grades()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating grade: {str(e)}")
    
    def delete_grade(self):
        """Delete selected grade"""
        selected_item = self.grades_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a grade to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this grade?"):
            try:
                grade_id = self.grades_tree.item(selected_item[0])['values'][0]
                
                conn = connect()
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM grades WHERE id=%s', (grade_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Grade deleted successfully!")
                self.clear_grade_fields()
                self.load_grades()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting grade: {str(e)}")
    
    def validate_grade_input(self):
        """Validate grade input fields"""
        if not self.student_combo.get():
            messagebox.showerror("Error", "Please select a student")
            return False
        if not self.subject_entry.get().strip():
            messagebox.showerror("Error", "Subject is required")
            return False
        try:
            grade = float(self.grade_entry.get())
            max_marks = float(self.max_marks_entry.get())
            if grade < 0 or max_marks <= 0:
                messagebox.showerror("Error", "Grade and max marks must be positive numbers")
                return False
        except ValueError:
            messagebox.showerror("Error", "Grade and max marks must be valid numbers")
            return False
        return True
    
    def clear_grade_fields(self):
        """Clear all grade input fields"""
        self.student_combo.set('')
        self.subject_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.max_marks_entry.delete(0, tk.END)
        self.max_marks_entry.insert(0, "100")
    
    def on_grade_select(self, event):
        """Handle grade selection"""
        selected_item = self.grades_tree.selection()
        if selected_item:
            values = self.grades_tree.item(selected_item[0])['values']
            # Find and set the student in combo
            for i, value in enumerate(self.student_combo['values']):
                if value.startswith(str(values[0])):
                    self.student_combo.current(i)
                    break
            self.subject_entry.delete(0, tk.END)
            self.subject_entry.insert(0, values[2])
            self.grade_entry.delete(0, tk.END)
            self.grade_entry.insert(0, values[3])
            self.max_marks_entry.delete(0, tk.END)
            self.max_marks_entry.insert(0, values[4])
    
    def load_students_combo(self):
        """Load students into the combobox"""
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name FROM students ORDER BY name')
            students = cursor.fetchall()
            
            student_list = [f"{student[0]} - {student[1]}" for student in students]
            self.student_combo['values'] = student_list
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading students: {str(e)}")
    
    def load_grades(self):
        """Load grades into the treeview"""
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT g.id, s.name, g.subject, g.grade, g.max_marks,
                       ROUND((g.grade / g.max_marks) * 100, 2) as percentage
                FROM grades g
                JOIN students s ON g.student_id = s.id
                ORDER BY s.name, g.subject
            ''')
            grades = cursor.fetchall()
            
            for grade in grades:
                self.grades_tree.insert('', 'end', values=grade)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading grades: {str(e)}")
    
    # Search and filter operations
    def search_by_name(self):
        """Search students by name"""
        search_term = self.search_name_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a name to search")
            return
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.name, s.email, s.class_name, g.subject, g.grade,
                       ROUND((g.grade / g.max_marks) * 100, 2) as percentage
                FROM students s
                LEFT JOIN grades g ON s.id = g.student_id
                WHERE s.name ILIKE %s
                ORDER BY s.name, g.subject
            ''', (f'%{search_term}%',))
            
            results = cursor.fetchall()
            
            for result in results:
                self.search_tree.insert('', 'end', values=result)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error searching: {str(e)}")
    
    def filter_by_class(self):
        """Filter students by class"""
        class_name = self.filter_class_combo.get()
        if not class_name:
            messagebox.showwarning("Warning", "Please select a class to filter")
            return
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.name, s.email, s.class_name, g.subject, g.grade,
                       ROUND((g.grade / g.max_marks) * 100, 2) as percentage
                FROM students s
                LEFT JOIN grades g ON s.id = g.student_id
                WHERE s.class_name = %s
                ORDER BY s.name, g.subject
            ''', (class_name,))
            
            results = cursor.fetchall()
            
            for result in results:
                self.search_tree.insert('', 'end', values=result)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering: {str(e)}")
    
    def filter_by_subject(self):
        """Filter grades by subject"""
        subject = self.filter_subject_combo.get()
        if not subject:
            messagebox.showwarning("Warning", "Please select a subject to filter")
            return
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.name, s.email, s.class_name, g.subject, g.grade,
                       ROUND((g.grade / g.max_marks) * 100, 2) as percentage
                FROM students s
                JOIN grades g ON s.id = g.student_id
                WHERE g.subject = %s
                ORDER BY s.name
            ''', (subject,))
            
            results = cursor.fetchall()
            
            for result in results:
                self.search_tree.insert('', 'end', values=result)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering: {str(e)}")
    
    def reset_filters(self):
        """Reset all filters and show all data"""
        self.search_name_entry.delete(0, tk.END)
        self.filter_class_combo.set('')
        self.filter_subject_combo.set('')
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Show all students and grades
        try:
            conn = connect()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.name, s.email, s.class_name, g.subject, g.grade,
                       ROUND((g.grade / g.max_marks) * 100, 2) as percentage
                FROM students s
                LEFT JOIN grades g ON s.id = g.student_id
                ORDER BY s.name, g.subject
            ''')
            
            results = cursor.fetchall()
            
            for result in results:
                self.search_tree.insert('', 'end', values=result)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
    
    def load_filter_options(self):
        """Load options for filter comboboxes"""
        try:
            conn = connect()
            cursor = conn.cursor()
            
            # Load classes
            cursor.execute('SELECT DISTINCT class_name FROM students ORDER BY class_name')
            classes = cursor.fetchall()
            self.filter_class_combo['values'] = [class_name[0] for class_name in classes]
            
            # Load subjects
            cursor.execute('SELECT DISTINCT subject FROM grades ORDER BY subject')
            subjects = cursor.fetchall()
            self.filter_subject_combo['values'] = [subject[0] for subject in subjects]
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading filter options: {str(e)}")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()