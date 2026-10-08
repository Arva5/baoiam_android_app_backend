"""
Seed 9 LMS courses with realistic dummy data, Cloudflare R2 video keys,
playable fallback URLs, modules, lectures, what_you_learn, and key_features.

Courses included:
1. Complete Python Bootcamp
2. Udaan 90
3. Success Fusion
4. Business Analytics Fundamentals
5. Advanced Python Web Development
6. Business Analytics with Python
7. UI/UX Design Fundamentals
8. Unpublished Draft Course
9. Full Stack JavaScript (ID: 9)

Usage:
  python manage.py seed_dummy_courses
  python manage.py seed_dummy_courses --reset
  python manage.py seed_dummy_courses --reset --r2-base-url https://pub-xxxxxxxx.r2.dev
"""
import os
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from courses.models import Category, ContentItem, Course, CourseEnrollment, CourseModule, Lesson

SAMPLE_BASE = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample"
PDF_SAMPLE = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

COURSES_DATA = [
    {
        "id": 9,
        "title": "Full Stack JavaScript",
        "slug": "full-stack-javascript",
        "short_code": "FSJ",
        "subtitle": "MERN stack development",
        "description": "Master MongoDB, Express, React, and Node.js. Build complete full-stack web applications from scratch with modern best practices, state management, and cloud deployment.",
        "thumbnail_url": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Sarah Johnson",
        "category_id": 3,
        "category_name": "Technology",
        "level": "intermediate",
        "rating": Decimal("4.50"),
        "reviews_count": 342,
        "duration_hours": Decimal("60.0"),
        "price": Decimal("129.99"),
        "discounted_price": Decimal("89.99"),
        "is_featured": True,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "Build full-stack web applications with React, Node.js, Express, and MongoDB",
            "Design RESTful APIs, implement authentication with JWT and role-based authorization",
            "State management with Redux Toolkit and React Query",
            "Deploy applications with CI/CD on Cloudflare and AWS"
        ],
        "key_features": [
            "60.0 hours on-demand high-definition video",
            "150 comprehensive lectures and code repositories",
            "Industry-recognized Certificate of Completion",
            "Direct access to mentor Q&A forum",
            "Full lifetime access on mobile and web"
        ],
        "modules": [
            {
                "title": "Module 1: Modern JavaScript & ES6+ Mastery",
                "order": 1,
                "lectures": [
                    {
                        "title": "Welcome to Full Stack JavaScript",
                        "description": "Course overview, roadmap, and local development environment setup.",
                        "order": 1,
                        "duration_seconds": 630,
                        "is_preview": True,
                        "storage_key": "videos/javascript/welcome.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "ES6+ Modern Syntax & Async JavaScript",
                        "description": "Arrow functions, destructuring, promises, and async/await in practice.",
                        "order": 2,
                        "duration_seconds": 920,
                        "is_preview": True,
                        "storage_key": "videos/javascript/async-js.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ElephantsDream.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Node.js Event Loop & Module System",
                        "description": "Understanding Node runtime, CommonJS vs ES Modules, and NPM ecosystem.",
                        "order": 3,
                        "duration_seconds": 840,
                        "is_preview": False,
                        "storage_key": "videos/javascript/nodejs-intro.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerBlazes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1627398242454-45a1465c2479?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: Backend Development with Express & MongoDB",
                "order": 2,
                "lectures": [
                    {
                        "title": "Express.js Architecture & REST Routing",
                        "description": "Building clean RESTful APIs, request validation, and modular routers.",
                        "order": 1,
                        "duration_seconds": 1150,
                        "is_preview": False,
                        "storage_key": "videos/javascript/express-api.mp4",
                        "sample_url": f"{SAMPLE_BASE}/Sintel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "MongoDB Schemas & Aggregation Pipelines",
                        "description": "Connecting Mongoose, writing efficient schemas, and data modeling.",
                        "order": 2,
                        "duration_seconds": 1280,
                        "is_preview": False,
                        "storage_key": "videos/javascript/mongodb-crud.mp4",
                        "sample_url": f"{SAMPLE_BASE}/TearsOfSteel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Frontend Mastery with React 19",
                "order": 3,
                "lectures": [
                    {
                        "title": "React Component Architecture & Hooks",
                        "description": "Building interactive UIs with useState, useEffect, and custom hooks.",
                        "order": 1,
                        "duration_seconds": 1400,
                        "is_preview": False,
                        "storage_key": "videos/javascript/react-hooks.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Authentication Flow with JWT & Cookies",
                        "description": "End-to-end authentication, secure cookie storage, and protected client routes.",
                        "order": 2,
                        "duration_seconds": 1100,
                        "is_preview": False,
                        "storage_key": "videos/javascript/jwt-auth.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerJoyrides.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 1,
        "title": "Complete Python Bootcamp",
        "slug": "complete-python-bootcamp",
        "short_code": "CPB",
        "subtitle": "Zero to Hero in Python Programming",
        "description": "Learn Python like a professional. Start from the basics and go all the way to creating your own applications, scripts, and games.",
        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Sarah Johnson",
        "category_id": 3,
        "category_name": "Technology",
        "level": "beginner",
        "rating": Decimal("4.85"),
        "reviews_count": 520,
        "duration_hours": Decimal("28.0"),
        "price": Decimal("59.99"),
        "discounted_price": Decimal("29.99"),
        "is_featured": True,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "Python programming fundamentals: variables, loops, conditionals, and functions",
            "Object-Oriented Programming (OOP) in Python with classes and inheritance",
            "Working with files, external packages, and virtual environments",
            "Building command-line utilities and automation scripts"
        ],
        "key_features": [
            "28.0 hours of comprehensive video training",
            "80 practice exercises and quizzes",
            "Downloadable cheat sheets & source code",
            "Certificate of Completion"
        ],
        "modules": [
            {
                "title": "Module 1: Python Fundamentals & Environment Setup",
                "order": 1,
                "lectures": [
                    {
                        "title": "Setting Up Python & VS Code",
                        "description": "Installation, virtual environment, and running your first script.",
                        "order": 1,
                        "duration_seconds": 540,
                        "is_preview": True,
                        "storage_key": "videos/python/setup.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Variables, Numbers & String Manipulation",
                        "description": "Core data types, string formatting, and mathematical operations.",
                        "order": 2,
                        "duration_seconds": 780,
                        "is_preview": True,
                        "storage_key": "videos/python/variables.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ElephantsDream.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Control Flow: If Statements, Loops & Range",
                        "description": "Branching logic, while loops, for loops, and comprehension syntax.",
                        "order": 3,
                        "duration_seconds": 820,
                        "is_preview": False,
                        "storage_key": "videos/python/control-flow.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerBlazes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: Data Structures & Functional Programming",
                "order": 2,
                "lectures": [
                    {
                        "title": "Lists, Tuples, Sets & Dictionaries",
                        "description": "Deep dive into built-in collections, key lookups, and memory efficiency.",
                        "order": 1,
                        "duration_seconds": 920,
                        "is_preview": False,
                        "storage_key": "videos/python/data-structures.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Functions, Scope, *args, **kwargs & Lambdas",
                        "description": "Writing modular code, default arguments, and first-class functions.",
                        "order": 2,
                        "duration_seconds": 880,
                        "is_preview": False,
                        "storage_key": "videos/python/functions.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Object-Oriented Programming & Real-World Projects",
                "order": 3,
                "lectures": [
                    {
                        "title": "Classes, Dunder Methods & Inheritance",
                        "description": "Object-oriented design patterns, polymorphism, and encapsulation.",
                        "order": 1,
                        "duration_seconds": 1050,
                        "is_preview": False,
                        "storage_key": "videos/python/oop.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerJoyrides.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Capstone: Building an Automated Web Scraper",
                        "description": "Putting everything together to build and deploy a real Python tool.",
                        "order": 2,
                        "duration_seconds": 1200,
                        "is_preview": False,
                        "storage_key": "videos/python/capstone.mp4",
                        "sample_url": f"{SAMPLE_BASE}/Sintel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 2,
        "title": "Udaan 90",
        "slug": "udaan-90",
        "short_code": "U90",
        "subtitle": "Fast Track Career & Interview Bootcamp",
        "description": "Accelerate your career readiness in 90 days with structured mentor guidance, resume enhancement, mock interviews, and industry-oriented projects.",
        "thumbnail_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Amit Patel",
        "category_id": 4,
        "category_name": "Career Growth",
        "level": "all_levels",
        "rating": Decimal("4.75"),
        "reviews_count": 185,
        "duration_hours": Decimal("90.0"),
        "price": Decimal("199.99"),
        "discounted_price": Decimal("149.99"),
        "is_featured": True,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "Structured 90-day career roadmap for tech and product roles",
            "Crack DSA and system design interviews with live patterns",
            "LinkedIn profile optimization and cold outreach strategies",
            "Real-world capstone project to highlight on your resume"
        ],
        "key_features": [
            "90 Days Intensive Learning & Mentorship",
            "1-on-1 Resume & Portfolio Review",
            "Mock Interviews with Senior Engineers",
            "Guaranteed Placement Referral Support"
        ],
        "modules": [
            {
                "title": "Module 1: Mindset & Technical Foundation",
                "order": 1,
                "lectures": [
                    {
                        "title": "Kickoff: The 90-Day Career Roadmap",
                        "description": "Goal setting, habit formation, and interview milestones.",
                        "order": 1,
                        "duration_seconds": 720,
                        "is_preview": True,
                        "storage_key": "videos/udaan/kickoff.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerBlazes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Target Company Research & Skill Gap Analysis",
                        "description": "Mapping out tiers, job requirements, and portfolio expectations.",
                        "order": 2,
                        "duration_seconds": 680,
                        "is_preview": True,
                        "storage_key": "videos/udaan/research.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: Coding Interviews & Core Problem Solving",
                "order": 2,
                "lectures": [
                    {
                        "title": "Mastering Common DSA Interview Patterns",
                        "description": "Sliding window, two pointers, and hash table strategies.",
                        "order": 1,
                        "duration_seconds": 980,
                        "is_preview": False,
                        "storage_key": "videos/udaan/dsa.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "System Design Fundamentals for Mid-Level Roles",
                        "description": "Load balancers, caching, databases, and microservices overview.",
                        "order": 2,
                        "duration_seconds": 1100,
                        "is_preview": False,
                        "storage_key": "videos/udaan/sysdesign.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerJoyrides.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Resume Polish, Outreach & Placement",
                "order": 3,
                "lectures": [
                    {
                        "title": "Crafting an ATS-Proof Tech Resume & LinkedIn Profile",
                        "description": "Keyword targeting, metric-driven bullet points, and recruiter discovery.",
                        "order": 1,
                        "duration_seconds": 840,
                        "is_preview": False,
                        "storage_key": "videos/udaan/resume.mp4",
                        "sample_url": f"{SAMPLE_BASE}/Sintel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Live Mock Interview & Salary Negotiation Strategies",
                        "description": "Handling behavioral questions, offer letters, and counter-offers.",
                        "order": 2,
                        "duration_seconds": 1250,
                        "is_preview": False,
                        "storage_key": "videos/udaan/negotiation.mp4",
                        "sample_url": f"{SAMPLE_BASE}/TearsOfSteel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 3,
        "title": "Success Fusion",
        "slug": "success-fusion",
        "short_code": "SF",
        "subtitle": "Leadership & Executive Productivity",
        "description": "Unlock your leadership potential, executive presence, and strategic thinking to lead teams effectively and drive business transformation.",
        "thumbnail_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Dr. Robert Brown",
        "category_id": 5,
        "category_name": "Leadership & Soft Skills",
        "level": "intermediate",
        "rating": Decimal("4.90"),
        "reviews_count": 210,
        "duration_hours": Decimal("15.0"),
        "price": Decimal("149.99"),
        "discounted_price": Decimal("99.99"),
        "is_featured": True,
        "is_popular": False,
        "is_published": True,
        "what_you_learn": [
            "Executive presence, assertive communication, and influence",
            "High-performance team management and conflict resolution",
            "Decision making under uncertainty and strategic thinking"
        ],
        "key_features": [
            "15.0 hours of executive masterclasses",
            "Downloadable leadership frameworks and templates",
            "Certificate in Executive Leadership"
        ],
        "modules": [
            {
                "title": "Module 1: Principles of Modern Leadership",
                "order": 1,
                "lectures": [
                    {
                        "title": "Defining Your Leadership Identity",
                        "description": "Authentic leadership, emotional intelligence, and values.",
                        "order": 1,
                        "duration_seconds": 600,
                        "is_preview": True,
                        "storage_key": "videos/leadership/intro.mp4",
                        "sample_url": f"{SAMPLE_BASE}/Sintel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Emotional Intelligence & Team Psychological Safety",
                        "description": "Fostering trust, innovation, and psychological safety in high-stakes environments.",
                        "order": 2,
                        "duration_seconds": 720,
                        "is_preview": True,
                        "storage_key": "videos/leadership/eq.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: High-Stakes Communication & Influence",
                "order": 2,
                "lectures": [
                    {
                        "title": "Executive Storytelling & Pitching to Stakeholders",
                        "description": "Transforming data and strategy into compelling executive narratives.",
                        "order": 1,
                        "duration_seconds": 810,
                        "is_preview": False,
                        "storage_key": "videos/leadership/storytelling.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ElephantsDream.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Managing Conflict & Delivering Constructive Feedback",
                        "description": "Frameworks for difficult peer discussions and performance improvement.",
                        "order": 2,
                        "duration_seconds": 750,
                        "is_preview": False,
                        "storage_key": "videos/leadership/feedback.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerBlazes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Strategic Execution & High Output Teams",
                "order": 3,
                "lectures": [
                    {
                        "title": "Time Audits, Deep Work & Prioritization Frameworks",
                        "description": "Eliminating busywork, Eisenhower Matrix, and time blocking for leaders.",
                        "order": 1,
                        "duration_seconds": 690,
                        "is_preview": False,
                        "storage_key": "videos/leadership/productivity.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Building Autonomous & Self-Driven Teams",
                        "description": "Effective delegation, outcome-oriented ownership, and accountability.",
                        "order": 2,
                        "duration_seconds": 860,
                        "is_preview": False,
                        "storage_key": "videos/leadership/teams.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 4,
        "title": "Business Analytics Fundamentals",
        "slug": "business-analytics-fundamentals",
        "short_code": "BAF",
        "subtitle": "Data-driven Decision Making",
        "description": "Learn how to analyze enterprise data, extract key metrics, and communicate actionable insights to stakeholders using modern business intelligence methods.",
        "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Jane Smith",
        "category_id": 2,
        "category_name": "Business & Management",
        "level": "beginner",
        "rating": Decimal("4.60"),
        "reviews_count": 89,
        "duration_hours": Decimal("20.0"),
        "price": Decimal("79.99"),
        "discounted_price": Decimal("49.99"),
        "is_featured": False,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "Understand business KPIs, cohorts, and customer acquisition metrics",
            "Transform raw Excel and SQL datasets into executive dashboards",
            "Data storytelling and presenting to senior management"
        ],
        "key_features": [
            "20.0 hours of practical business case studies",
            "Real company dataset exercises (eCommerce & SaaS)",
            "Certificate of Completion"
        ],
        "modules": [
            {
                "title": "Module 1: Introduction to Business Analytics",
                "order": 1,
                "lectures": [
                    {
                        "title": "The Role of Business Analytics in Modern Firms",
                        "description": "Descriptive, predictive, and prescriptive analytics overview.",
                        "order": 1,
                        "duration_seconds": 650,
                        "is_preview": True,
                        "storage_key": "videos/analytics/fundamentals.mp4",
                        "sample_url": f"{SAMPLE_BASE}/TearsOfSteel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Key Business Metrics: CAC, LTV, Churn & Retention",
                        "description": "Core unit economics for SaaS, eCommerce, and tech startups.",
                        "order": 2,
                        "duration_seconds": 780,
                        "is_preview": True,
                        "storage_key": "videos/analytics/kpis.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: Data Wrangling with Excel & SQL",
                "order": 2,
                "lectures": [
                    {
                        "title": "Advanced Excel: Pivot Tables, VLOOKUP & XLOOKUP",
                        "description": "Fast data aggregation, modeling, and automated formulas.",
                        "order": 1,
                        "duration_seconds": 890,
                        "is_preview": False,
                        "storage_key": "videos/analytics/excel.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ElephantsDream.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "SQL Querying: SELECT, JOINs, GROUP BY & Window Functions",
                        "description": "Querying relational databases to extract business insights.",
                        "order": 2,
                        "duration_seconds": 1040,
                        "is_preview": False,
                        "storage_key": "videos/analytics/sql.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerBlazes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Business Intelligence Dashboards & Reporting",
                "order": 3,
                "lectures": [
                    {
                        "title": "Building Executive Dashboards in PowerBI & Tableau",
                        "description": "Creating real-time interactive charts, heatmaps, and filters.",
                        "order": 1,
                        "duration_seconds": 980,
                        "is_preview": False,
                        "storage_key": "videos/analytics/dashboards.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Data Storytelling & Executive Presentation Strategy",
                        "description": "Presenting insights clearly to stakeholders and driving decisions.",
                        "order": 2,
                        "duration_seconds": 830,
                        "is_preview": False,
                        "storage_key": "videos/analytics/storytelling.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 5,
        "title": "Advanced Python Web Development",
        "slug": "advanced-python-web-development",
        "short_code": "PWD",
        "subtitle": "Master Django, REST APIs & Microservices",
        "description": "A comprehensive deep dive into building scalable web architectures using Python, Django REST Framework, Celery, and Redis.",
        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "John Doe",
        "category_id": 3,
        "category_name": "Technology",
        "level": "advanced",
        "rating": Decimal("4.80"),
        "reviews_count": 125,
        "duration_hours": Decimal("45.5"),
        "price": Decimal("99.99"),
        "discounted_price": Decimal("49.99"),
        "is_featured": True,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "Architect high-throughput REST APIs with Django REST Framework",
            "Implement asynchronous task queues with Celery and Redis",
            "Database query optimization, indexing, and PostgreSQL connection pooling",
            "Containerize and deploy with Docker and Kubernetes"
        ],
        "key_features": [
            "45.5 hours of advanced engineering content",
            "Production-ready codebase templates",
            "System design and microservice architecture modules"
        ],
        "modules": [
            {
                "title": "Module 1: Production Django & DRF Architecture",
                "order": 1,
                "lectures": [
                    {
                        "title": "DRF Serialization Deep Dive & Query Optimization",
                        "description": "Avoiding N+1 queries, select_related, and prefetch_related in real production APIs.",
                        "order": 1,
                        "duration_seconds": 890,
                        "is_preview": True,
                        "storage_key": "videos/python/drf-opt.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Custom Authentication & Permission Classes in DRF",
                        "description": "Token-based auth, JWT rotation, and object-level permissions.",
                        "order": 2,
                        "duration_seconds": 840,
                        "is_preview": True,
                        "storage_key": "videos/python/drf-auth.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: Asynchronous Workflows & Caching",
                "order": 2,
                "lectures": [
                    {
                        "title": "Background Job Queues with Celery & Redis",
                        "description": "Handling long-running tasks, email queues, and periodic cron jobs.",
                        "order": 1,
                        "duration_seconds": 1020,
                        "is_preview": False,
                        "storage_key": "videos/python/celery.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerJoyrides.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Redis Caching Strategies & Performance Tuning",
                        "description": "Cache invalidation patterns, view caching, and low-level cache API.",
                        "order": 2,
                        "duration_seconds": 930,
                        "is_preview": False,
                        "storage_key": "videos/python/caching.mp4",
                        "sample_url": f"{SAMPLE_BASE}/Sintel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Microservices, Docker & Production Cloud",
                "order": 3,
                "lectures": [
                    {
                        "title": "Containerizing Django with Multi-Stage Dockerfiles",
                        "description": "Optimizing image size, environment variables, and Docker Compose.",
                        "order": 1,
                        "duration_seconds": 960,
                        "is_preview": False,
                        "storage_key": "videos/python/docker.mp4",
                        "sample_url": f"{SAMPLE_BASE}/TearsOfSteel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "CI/CD Deployment Pipelines & Monitoring",
                        "description": "GitHub Actions, automated migrations, health checks, and Sentry.",
                        "order": 2,
                        "duration_seconds": 1150,
                        "is_preview": False,
                        "storage_key": "videos/python/cicd.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 6,
        "title": "Business Analytics with Python",
        "slug": "business-analytics-with-python",
        "short_code": "BAP",
        "subtitle": "Pandas, NumPy, and Business Intelligence",
        "description": "Transform messy raw datasets into executive insights using Python, Pandas, Matplotlib, and automated reporting pipelines.",
        "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Dr. Priya Sharma",
        "category_id": 2,
        "category_name": "Business & Management",
        "level": "intermediate",
        "rating": Decimal("4.70"),
        "reviews_count": 160,
        "duration_hours": Decimal("35.0"),
        "price": Decimal("119.99"),
        "discounted_price": Decimal("79.99"),
        "is_featured": False,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "Master Pandas and NumPy for high-speed data wrangling",
            "Build cohort analysis, churn prediction, and revenue models",
            "Create interactive business dashboards with Plotly and Streamlit"
        ],
        "key_features": [
            "35.0 hours hands-on coding",
            "10 real financial and product datasets",
            "Jupyter notebooks with turnkey solution code"
        ],
        "modules": [
            {
                "title": "Module 1: Python for Data Manipulation",
                "order": 1,
                "lectures": [
                    {
                        "title": "Pandas DataFrames: Cleaning & Aggregation",
                        "description": "Groupby, pivot tables, and time-series resampling for business reports.",
                        "order": 1,
                        "duration_seconds": 960,
                        "is_preview": True,
                        "storage_key": "videos/analytics/pandas-intro.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerJoyrides.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Handling Missing Data, Outliers & Data Imputation",
                        "description": "Techniques to clean inconsistent records and handle noisy real-world data.",
                        "order": 2,
                        "duration_seconds": 840,
                        "is_preview": True,
                        "storage_key": "videos/analytics/cleaning.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: Exploratory Analysis & Visualization",
                "order": 2,
                "lectures": [
                    {
                        "title": "Visualizing Distributions with Seaborn & Matplotlib",
                        "description": "Heatmaps, box plots, scatter plots, and multi-variable correlations.",
                        "order": 1,
                        "duration_seconds": 890,
                        "is_preview": False,
                        "storage_key": "videos/analytics/viz.mp4",
                        "sample_url": f"{SAMPLE_BASE}/Sintel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Cohort Analysis & Customer Churn Modeling",
                        "description": "Tracking user retention cohorts and predicting monthly churn risk.",
                        "order": 2,
                        "duration_seconds": 1050,
                        "is_preview": False,
                        "storage_key": "videos/analytics/churn.mp4",
                        "sample_url": f"{SAMPLE_BASE}/TearsOfSteel.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Interactive Dashboards & Automated Reports",
                "order": 3,
                "lectures": [
                    {
                        "title": "Building Real-Time Dashboards with Streamlit & Plotly",
                        "description": "Creating self-serve analytics tools for marketing and product managers.",
                        "order": 1,
                        "duration_seconds": 1120,
                        "is_preview": False,
                        "storage_key": "videos/analytics/streamlit.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Automating Executive PDF & Slack Digest Reports",
                        "description": "Scheduled report delivery to leadership via automated Python jobs.",
                        "order": 2,
                        "duration_seconds": 940,
                        "is_preview": False,
                        "storage_key": "videos/analytics/auto-reports.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ElephantsDream.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 7,
        "title": "UI/UX Design Fundamentals",
        "slug": "ui-ux-design-fundamentals",
        "short_code": "UI/UX",
        "subtitle": "Figma, Design Systems & Wireframing",
        "description": "Learn user research, wireframing, high-fidelity prototypes in Figma, and design systems from scratch.",
        "thumbnail_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?auto=format&fit=crop&w=800&q=80",
        "cover_image_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=1200&q=80",
        "instructor_name": "Jane Instructor",
        "category_id": 1,
        "category_name": "Design",
        "level": "beginner",
        "rating": Decimal("4.70"),
        "reviews_count": 240,
        "duration_hours": Decimal("18.0"),
        "price": Decimal("89.99"),
        "discounted_price": Decimal("59.99"),
        "is_featured": False,
        "is_popular": True,
        "is_published": True,
        "what_you_learn": [
            "User-centered design methodology and usability testing",
            "Master Figma components, autolayout, variants, and interactive prototypes",
            "Build scalable design systems for iOS, Android, and Web apps"
        ],
        "key_features": [
            "18.0 hours of step-by-step design training",
            "Figma project UI kits and source assets included",
            "Portfolio-ready mobile app case study"
        ],
        "modules": [
            {
                "title": "Module 1: UX Research & Wireframing",
                "order": 1,
                "lectures": [
                    {
                        "title": "Introduction to UX Thinking & Figma Basics",
                        "description": "Understanding user mental models and setting up Figma artboards.",
                        "order": 1,
                        "duration_seconds": 660,
                        "is_preview": True,
                        "storage_key": "videos/uiux/figma-intro.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Conducting User Interviews & Journey Mapping",
                        "description": "Empathy mapping, personas, and identifying user friction points.",
                        "order": 2,
                        "duration_seconds": 780,
                        "is_preview": True,
                        "storage_key": "videos/uiux/research.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ElephantsDream.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 2: High-Fidelity UI & Figma Prototyping",
                "order": 2,
                "lectures": [
                    {
                        "title": "Typography, Color Theory & Visual Hierarchy",
                        "description": "Creating aesthetic layouts that are accessible and easy to scan.",
                        "order": 1,
                        "duration_seconds": 890,
                        "is_preview": False,
                        "storage_key": "videos/uiux/visual.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerBlazes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Auto-Layout, Component Variants & Smart Animate",
                        "description": "Mastering interactive micro-animations and responsive card layouts.",
                        "order": 2,
                        "duration_seconds": 1050,
                        "is_preview": False,
                        "storage_key": "videos/uiux/autolayout.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerEscapes.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            },
            {
                "title": "Module 3: Design Systems & Developer Handoff",
                "order": 3,
                "lectures": [
                    {
                        "title": "Building a Reusable Design System with Design Tokens",
                        "description": "Color styles, typography tokens, buttons, and stateful components.",
                        "order": 1,
                        "duration_seconds": 940,
                        "is_preview": False,
                        "storage_key": "videos/uiux/tokens.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerFun.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?auto=format&fit=crop&w=640&q=80",
                    },
                    {
                        "title": "Conducting Usability Tests & Developer Specs Handoff",
                        "description": "Testing with real users and generating clean CSS/Kotlin design specs.",
                        "order": 2,
                        "duration_seconds": 880,
                        "is_preview": False,
                        "storage_key": "videos/uiux/handoff.mp4",
                        "sample_url": f"{SAMPLE_BASE}/ForBiggerJoyrides.mp4",
                        "thumbnail_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=640&q=80",
                    },
                ]
            }
        ]
    },
    {
        "id": 8,
        "title": "Unpublished Draft Course",
        "slug": "unpublished-draft-course",
        "short_code": "DR",
        "subtitle": "Internal Curriculum Review",
        "description": "Internal preview curriculum in draft state for instructor review, QA, and content evaluation before public release.",
        "thumbnail_url": "https://placehold.co/800x450/212529/ced4da?text=Draft+Course",
        "cover_image_url": "https://placehold.co/1200x500/343a40/dee2e6?text=Draft+Course+Cover",
        "instructor_name": "Baoiam Instructor",
        "category_id": 3,
        "category_name": "Technology",
        "level": "beginner",
        "rating": Decimal("0.00"),
        "reviews_count": 0,
        "duration_hours": Decimal("10.0"),
        "price": Decimal("0.00"),
        "discounted_price": None,
        "is_featured": False,
        "is_popular": False,
        "is_published": False,
        "what_you_learn": [
            "Curriculum outline under review",
            "Draft lecture notes and video rehearsals"
        ],
        "key_features": [
            "Draft status - visible only with include_drafts=true or Admin access"
        ],
        "modules": [
            {
                "title": "Draft Module 1: Pre-Release Overview",
                "order": 1,
                "lectures": [
                    {
                        "title": "Draft Lecture 1",
                        "description": "Draft rehearsal recording.",
                        "order": 1,
                        "duration_seconds": 300,
                        "is_preview": False,
                        "storage_key": "videos/draft/test.mp4",
                        "sample_url": f"{SAMPLE_BASE}/BigBuckBunny.mp4",
                        "thumbnail_url": "https://placehold.co/640x360/343a40/adb5bd?text=Draft+Lecture",
                    }
                ]
            }
        ]
    },
]


class Command(BaseCommand):
    help = "Seeds all 9 LMS courses with full metadata, Cloudflare R2 video keys, and modules/lectures."

    def add_arguments(self, parser):
        parser.add_argument(
            "--r2-base-url",
            default=os.environ.get("R2_PUBLIC_BASE_URL", getattr(settings, "R2_PUBLIC_BASE_URL", "")),
            help="Cloudflare R2 public URL base, e.g. https://pub-xxxxxxxx.r2.dev",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Clear and re-seed all courses with explicit IDs",
        )
        parser.add_argument(
            "--enroll-email",
            default="",
            help="Enroll a user in all seeded courses for testing",
        )

    def handle(self, *args, **opts):
        base_url = (opts["r2_base_url"] or "").rstrip("/")
        User = get_user_model()

        # Ensure primary instructor exists
        instructor = User.objects.filter(id=1).first()
        if not instructor:
            instructor = User.objects.filter(is_staff=True).first()
        if not instructor:
            instructor = User.objects.create_user(
                email="sarah.johnson@baoiam.com",
                password="Password123!",
                name="Sarah Johnson",
            )
            instructor.email_verified = True
            instructor.is_staff = True
            instructor.save()

        # Seed standard Categories
        category_defs = [
            ("Design", "design", 1),
            ("Business & Management", "business-management", 2),
            ("Technology", "technology", 3),
            ("Career Growth", "career-growth", 4),
            ("Leadership & Soft Skills", "leadership-soft-skills", 5),
        ]

        created_categories = {}
        for name, slug, order in category_defs:
            cat = Category.objects.filter(slug=slug).first()
            if not cat:
                cat = Category.objects.filter(name__iexact=name).first()
            if cat:
                cat.name = name
                cat.order = order
                cat.is_active = True
                cat.save()
            else:
                cat = Category.objects.create(name=name, slug=slug, order=order, is_active=True)
            created_categories[slug] = cat
            created_categories[name] = cat

        if opts["reset"]:
            self.stdout.write("Resetting existing dummy courses...")
            ids = [c["id"] for c in COURSES_DATA]
            slugs = [c["slug"] for c in COURSES_DATA]
            titles = [c["title"] for c in COURSES_DATA]
            Course.objects.filter(id__in=ids).delete()
            Course.objects.filter(slug__in=slugs).delete()
            Course.objects.filter(title__in=titles).delete()

        for c_data in COURSES_DATA:
            cid = c_data["id"]
            cat = created_categories.get(c_data["category_name"]) or created_categories.get("Technology")
            Course.objects.filter(slug=c_data["slug"]).exclude(id=cid).delete()

            course, created = Course.objects.update_or_create(
                id=cid,
                defaults={
                    "title": c_data["title"],
                    "slug": c_data["slug"],
                    "short_code": c_data["short_code"],
                    "subtitle": c_data["subtitle"],
                    "description": c_data["description"],
                    "thumbnail_url": c_data["thumbnail_url"],
                    "cover_image_url": c_data["cover_image_url"],
                    "instructor": instructor,
                    "instructor_name": c_data["instructor_name"],
                    "category": cat,
                    "level": c_data["level"],
                    "rating": c_data["rating"],
                    "reviews_count": c_data["reviews_count"],
                    "duration_hours": c_data["duration_hours"],
                    "price": c_data["price"],
                    "discounted_price": c_data["discounted_price"],
                    "is_featured": c_data["is_featured"],
                    "is_popular": c_data["is_popular"],
                    "is_published": c_data["is_published"],
                    "what_you_learn": c_data["what_you_learn"],
                    "key_features": c_data["key_features"],
                }
            )

            # Rebuild modules & lessons
            CourseModule.objects.filter(course=course).delete()
            total_lectures = 0

            for m_data in c_data.get("modules", []):
                module = CourseModule.objects.create(
                    course=course,
                    title=m_data["title"],
                    order=m_data["order"],
                )

                for l_data in m_data.get("lectures", []):
                    storage_key = l_data.get("storage_key", "")
                    sample_url = l_data.get("sample_url", "")
                    resolved_url = f"{base_url}/{storage_key}" if (base_url and storage_key) else sample_url

                    lesson = Lesson.objects.create(
                        module=module,
                        title=l_data["title"],
                        description=l_data.get("description", ""),
                        order=l_data["order"],
                        thumbnail_url=l_data.get("thumbnail_url"),
                        is_preview=l_data.get("is_preview", False),
                        storage_key=storage_key,
                        video_url=resolved_url,
                        duration_seconds=l_data.get("duration_seconds", 600),
                        published_at=date.today(),
                    )
                    total_lectures += 1

                    # Also create ContentItem for video so legacy /play/ API works
                    ContentItem.objects.create(
                        lesson=lesson,
                        content_type=ContentItem.ContentType.VIDEO,
                        title=f"{l_data['title']} (Video)",
                        url=resolved_url,
                        storage_key=storage_key,
                        duration_seconds=l_data.get("duration_seconds", 600),
                        order=1,
                    )

            # Update lessons count
            expected_count = total_lectures if total_lectures > 0 else 7
            course.lessons_count = expected_count
            course.save(update_fields=["lessons_count"])

            self.stdout.write(self.style.SUCCESS(
                f"[{'CREATED' if created else 'UPDATED'}] ID {course.id}: {course.title} (slug: {course.slug})"
            ))

        if opts["enroll_email"]:
            user = User.objects.filter(email__iexact=opts["enroll_email"]).first()
            if user:
                for c_data in COURSES_DATA:
                    c = Course.objects.get(id=c_data["id"])
                    CourseEnrollment.objects.get_or_create(
                        user=user,
                        course=c,
                        defaults={"total_lessons": c.lessons_count},
                    )
                self.stdout.write(self.style.SUCCESS(f"Enrolled {user.email} in all dummy courses."))

        self.stdout.write(self.style.SUCCESS("All 9 LMS courses seeded successfully!"))
