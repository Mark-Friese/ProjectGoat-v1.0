"""
Database Initialization Script
Creates tables and populates with initial sample data
"""
from datetime import date, datetime
from database import engine, SessionLocal
import models
import auth
import json

def init_database():
    """Initialize database with tables and sample data"""

    # Create all tables
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("[OK] Tables created")

    # Create session
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(models.User).count() > 0:
            print("Database already contains data. Skipping initialization.")
            return

        print("Populating database with sample data...")

        # Create Users with hashed passwords
        users = [
            models.User(
                id='u1',
                name='Sarah Chen',
                email='sarah@example.com',
                password_hash=auth.hash_password('Password123!'),
                role='admin',
                availability=True,
                is_active=True,
                must_change_password=True,
                created_at=datetime.now()
            ),
            models.User(
                id='u2',
                name='Marcus Thompson',
                email='marcus@example.com',
                password_hash=auth.hash_password('Password123!'),
                role='member',
                availability=True,
                is_active=True,
                must_change_password=True,
                created_at=datetime.now()
            ),
            models.User(
                id='u3',
                name='Elena Rodriguez',
                email='elena@example.com',
                password_hash=auth.hash_password('Password123!'),
                role='member',
                availability=True,
                is_active=True,
                must_change_password=True,
                created_at=datetime.now()
            ),
            models.User(
                id='u4',
                name='James Wilson',
                email='james@example.com',
                password_hash=auth.hash_password('Password123!'),
                role='member',
                availability=False,
                is_active=True,
                must_change_password=True,
                created_at=datetime.now()
            ),
            models.User(
                id='u5',
                name='Priya Patel',
                email='priya@example.com',
                password_hash=auth.hash_password('Password123!'),
                role='viewer',
                availability=True,
                is_active=True,
                must_change_password=True,
                created_at=datetime.now()
            ),
        ]
        db.add_all(users)
        print("[OK] Users created")

        # Create Projects
        projects = [
            models.Project(
                id='p1',
                name='Website Redesign',
                description='Complete overhaul of company website',
                start_date=date(2025, 11, 1),
                end_date=date(2025, 12, 31),
                color='#3b82f6'
            ),
            models.Project(
                id='p2',
                name='Mobile App Launch',
                description='Launch new mobile application',
                start_date=date(2025, 11, 15),
                end_date=date(2026, 1, 15),
                color='#8b5cf6'
            ),
        ]
        db.add_all(projects)
        print("[OK] Projects created")

        # Create Tasks
        tasks = [
            models.Task(
                id='t1',
                title='Design new homepage layout',
                description='Create wireframes and high-fidelity mockups for the new homepage',
                status='done',
                priority='high',
                assignee_id='u1',
                start_date=date(2025, 11, 1),
                due_date=date(2025, 11, 8),
                progress=100,
                tags=json.dumps(['design', 'homepage']),
                is_blocked=False,
                is_milestone=False,
                dependencies=json.dumps([]),
                project_id='p1'
            ),
            models.Task(
                id='t2',
                title='Develop homepage components',
                description='Build React components based on approved designs',
                status='in-progress',
                priority='high',
                assignee_id='u2',
                start_date=date(2025, 11, 8),
                due_date=date(2025, 11, 20),
                progress=60,
                tags=json.dumps(['development', 'react']),
                is_blocked=False,
                is_milestone=False,
                dependencies=json.dumps(['t1']),
                story_points=8,
                project_id='p1'
            ),
            models.Task(
                id='t3',
                title='Setup CI/CD pipeline',
                description='Configure automated testing and deployment',
                status='todo',
                priority='medium',
                assignee_id='u3',
                start_date=date(2025, 11, 15),
                due_date=date(2025, 11, 30),
                progress=0,
                tags=json.dumps(['devops', 'ci-cd']),
                is_blocked=True,
                is_milestone=False,
                dependencies=json.dumps([]),
                story_points=5,
                project_id='p1'
            ),
            models.Task(
                id='t4',
                title='User authentication flow',
                description='Implement secure login and registration',
                status='review',
                priority='high',
                assignee_id='u2',
                start_date=date(2025, 11, 10),
                due_date=date(2025, 11, 25),
                progress=95,
                tags=json.dumps(['security', 'authentication']),
                is_blocked=False,
                is_milestone=True,
                dependencies=json.dumps([]),
                story_points=13,
                project_id='p2'
            ),
            models.Task(
                id='t5',
                title='Mobile UI design',
                description='Design responsive mobile interface',
                status='in-progress',
                priority='high',
                assignee_id='u1',
                start_date=date(2025, 11, 15),
                due_date=date(2025, 11, 28),
                progress=40,
                tags=json.dumps(['design', 'mobile', 'ui']),
                is_blocked=False,
                is_milestone=False,
                dependencies=json.dumps([]),
                story_points=8,
                project_id='p2'
            ),
        ]
        db.add_all(tasks)
        print("[OK] Tasks created")

        # Create Comments
        comments = [
            models.Comment(
                id='c1',
                task_id='t1',
                user_id='u1',
                text='Initial mockups are ready for review',
                timestamp=datetime(2025, 11, 7, 10, 30)
            ),
            models.Comment(
                id='c2',
                task_id='t2',
                user_id='u2',
                text='Making good progress on the component library',
                timestamp=datetime(2025, 11, 12, 14, 15)
            ),
        ]
        db.add_all(comments)
        print("[OK] Comments created")

        # Create Blocker for t3
        blocker = models.Blocker(
            id='b1',
            task_id='t3',
            description='Waiting for infrastructure team to provision servers',
            created_at=datetime(2025, 11, 16, 9, 0)
        )
        db.add(blocker)
        print("[OK] Blocker created")

        # Create Sprints
        sprints = [
            models.Sprint(
                id='s1',
                name='Sprint 1 - Foundation',
                start_date=date(2025, 11, 1),
                end_date=date(2025, 11, 14),
                goals=json.dumps(['Complete homepage design', 'Start component development']),
                task_ids=json.dumps(['t1', 't2']),
                velocity=21
            ),
            models.Sprint(
                id='s2',
                name='Sprint 2 - Implementation',
                start_date=date(2025, 11, 15),
                end_date=date(2025, 11, 28),
                goals=json.dumps(['Complete homepage', 'Setup deployment pipeline']),
                task_ids=json.dumps(['t3', 't4', 't5']),
                velocity=26
            ),
        ]
        db.add_all(sprints)
        print("[OK] Sprints created")

        # Create Risks
        risks = [
            models.Risk(
                id='r1',
                title='Budget overrun risk',
                description='Project costs may exceed allocated budget due to scope changes',
                probability='medium',
                impact='high',
                owner_id='u1',
                mitigation='Weekly budget reviews and strict change control process',
                status='open'
            ),
            models.Risk(
                id='r2',
                title='Resource availability',
                description='Key team member may be reassigned to another project',
                probability='low',
                impact='high',
                owner_id='u1',
                mitigation='Cross-training team members on critical tasks',
                status='mitigated'
            ),
        ]
        db.add_all(risks)
        print("[OK] Risks created")

        # Create Issues
        issues = [
            models.Issue(
                id='i1',
                title='Performance issue on dashboard',
                description='Dashboard loads slowly with large datasets',
                priority='high',
                assignee_id='u2',
                status='in-progress',
                related_task_ids=json.dumps(['t2']),
                created_at=datetime(2025, 11, 14, 15, 30)
            ),
            models.Issue(
                id='i2',
                title='Browser compatibility bug',
                description='Layout breaks on older Safari versions',
                priority='medium',
                assignee_id='u3',
                status='open',
                related_task_ids=json.dumps(['t1', 't5']),
                created_at=datetime(2025, 11, 16, 11, 0)
            ),
        ]
        db.add_all(issues)
        print("[OK] Issues created")

        # Commit all changes
        db.commit()
        print("\n[SUCCESS] Database initialization complete!")
        print(f"  - {len(users)} users")
        print(f"  - {len(projects)} projects")
        print(f"  - {len(tasks)} tasks")
        print(f"  - {len(comments)} comments")
        print(f"  - 1 blocker")
        print(f"  - {len(sprints)} sprints")
        print(f"  - {len(risks)} risks")
        print(f"  - {len(issues)} issues")

    except Exception as e:
        print(f"\n[ERROR] Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("ProjectGoat - Database Initialization")
    print("=" * 50)
    init_database()
