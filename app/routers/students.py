from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from ..database import get_db
from ..models.student import Student
from ..schemas.student import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    # Check if roll number, phone, or email already exists
    result = await db.execute(
        select(Student).where(
            or_(
                Student.roll_number == student.roll_number,
                Student.phone == student.phone,
                Student.email == student.email
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Student with this roll number, phone, or email already exists"
        )
    
    # Create new student
    db_student = Student(**student.model_dump())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

@router.get("/", response_model=List[StudentResponse])
async def list_students(
    department: Optional[str] = None,
    semester: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Student)
    
    # Apply filters
    if department:
        query = query.where(Student.department.ilike(f"%{department}%"))
    if semester:
        query = query.where(Student.semester == semester)
    if search:
        query = query.where(
            or_(
                Student.name.ilike(f"%{search}%"),
                Student.roll_number.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%")
            )
        )
    
    result = await db.execute(query)
    students = result.scalars().all()
    return students

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    db_student = result.scalar_one_or_none()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check for unique constraints if updating roll number, phone, or email
    update_data = student_update.model_dump(exclude_unset=True)
    if any(field in update_data for field in ["roll_number", "phone", "email"]):
        query = select(Student).where(
            or_(
                Student.roll_number == update_data.get("roll_number", db_student.roll_number),
                Student.phone == update_data.get("phone", db_student.phone),
                Student.email == update_data.get("email", db_student.email)
            )
        ).where(Student.id != student_id)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Student with this roll number, phone, or email already exists"
            )
    
    # Update student fields
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    await db.commit()
    await db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student has any active book issues
    if student.issues:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete student with active book issues"
        )
    
    await db.delete(student)
    await db.commit()
    return {"message": "Student deleted successfully"} 