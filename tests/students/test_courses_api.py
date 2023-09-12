import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Student, Course


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_first_course(client, course_factory):
    course = course_factory(_quantity=1)
    course_id = course[0].id
    response = client.get(f'/api/v1/courses/{course_id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == course[0].name


@pytest.mark.django_db
def test_course_list(client, course_factory):
    course = course_factory(_quantity=25)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(course)
    for i, m in enumerate(data):
        assert m['name'] == course[i].name


@pytest.mark.django_db
def test_course_filter_id(client, course_factory):
    course = course_factory(_quantity=15)
    response = client.get('/api/v1/courses/', data={'id': course[0].id})
    assert response.status_code == 200
    data = response.json()
    assert data[0]['name'] == course[0].name


@pytest.mark.django_db
def test_course_filter_name(client, course_factory):
    course = course_factory(_quantity=15)
    response = client.get('/api/v1/courses/', data={'name': course[0].name})
    assert response.status_code == 200
    data = response.json()
    for i, c in enumerate(data):
        assert c['name'] == course[0].name


@pytest.mark.django_db
def test_create_course(client, student_factory):
    student = student_factory(_quantity=2)
    response = client.post('/api/v1/courses/', data={'name': 'python_course',
                                                     'students': [i.id for i in student]})
    assert response.status_code == 201


@pytest.mark.django_db
def test_patch_course(client, course_factory):
    student = Student.objects.create(name='Vasya', birth_date='1812-01-01')
    course = course_factory(_quantity=1)
    response = client.patch(f'/api/v1/courses/{course[0].id}/', data={'students': [student.id]})
    assert response.status_code == 200
    data = response.json()
    assert data['students'] == [student.id]


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    course = course_factory(_quantity=2)
    response = client.delete(f'/api/v1/courses/{course[0].id}/')
    assert response.status_code == 204


@pytest.mark.parametrize(
    'max_count, students_count, status_code',
    [(20, 20, 201), (20, 12, 201), (20, 25, 201)])
@pytest.mark.django_db
def test_max_students(settings,
                      client,
                      course_factory,
                      student_factory,
                      max_count,
                      students_count,
                      status_code):
    settings.MAX_STUDENTS_PER_COURSE = max_count
    students = student_factory(_quantity=students_count)
    response = client.post('/api/v1/courses/', data={
        'name': 'python',
        'students': [i.id for i in students]
    })
    assert response.status_code == status_code


