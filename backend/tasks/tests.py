from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
class TaskApiTests(TestCase):
 def setUp(self):
  self.client=APIClient()
  self.user=get_user_model().objects.create_user(username='tester',password='Testpass123!')
  self.client.force_authenticate(user=self.user)
 def test_crud_and_status(self):
  r=self.client.post('/api/tasks/',{'title':'First task','status':'pending'},format='json'); self.assertEqual(r.status_code,201)
  task_id=r.data['id']
  self.assertEqual(self.client.get('/api/tasks/').status_code,200)
  self.assertEqual(self.client.patch(f'/api/tasks/{task_id}/',{'status':'completed'},format='json').status_code,200)
  self.assertEqual(self.client.delete(f'/api/tasks/{task_id}/').status_code,204)
 def test_private_tasks(self):
  other=get_user_model().objects.create_user(username='other',password='Testpass123!')
  self.client.force_authenticate(user=other)
  self.assertEqual(self.client.get('/api/tasks/').data,[])
 def test_status_defaults_to_pending(self):
  r=self.client.post('/api/tasks/',{'title':'No status given'},format='json'); self.assertEqual(r.status_code,201)
  self.assertEqual(r.data['status'],'pending')
 def test_create_with_chosen_status(self):
  r=self.client.post('/api/tasks/',{'title':'Already started','status':'in_progress'},format='json'); self.assertEqual(r.status_code,201)
  self.assertEqual(r.data['status'],'in_progress')
 def test_invalid_status_is_rejected(self):
  r=self.client.post('/api/tasks/',{'title':'Bad status','status':'archived'},format='json'); self.assertEqual(r.status_code,400)
 def test_edit_title(self):
  task_id=self.client.post('/api/tasks/',{'title':'Old title'},format='json').data['id']
  r=self.client.patch(f'/api/tasks/{task_id}/',{'title':'New title'},format='json'); self.assertEqual(r.status_code,200)
  self.assertEqual(r.data['title'],'New title')
 def test_cannot_access_another_users_task(self):
  task_id=self.client.post('/api/tasks/',{'title':'Private task'},format='json').data['id']
  other=get_user_model().objects.create_user(username='intruder',password='Testpass123!')
  self.client.force_authenticate(user=other)
  self.assertEqual(self.client.get(f'/api/tasks/{task_id}/').status_code,404)
  self.assertEqual(self.client.delete(f'/api/tasks/{task_id}/').status_code,404)
