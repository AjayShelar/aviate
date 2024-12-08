from django.test import TestCase
from .models import Candidate

from rest_framework.test import APIClient
from rest_framework import status


class CandidateTests(TestCase):
    def setUp(self):
        Candidate.objects.all().delete()  # Ensure no leftover data from other tests
        Candidate.objects.create(name="Ajay Kumar", age=30, gender="M", email="ajay@example.com", phone_number="1234567890")
        Candidate.objects.create(name="Kumar Yadav", age=25, gender="M", email="kumar@example.com", phone_number="9876543210")
        Candidate.objects.create(name="Ajay Kumar Yadav", age=28, gender="M", email="ajay.yadav@example.com", phone_number="9988776655")
        Candidate.objects.create(name="Ravi Sharma", age=35, gender="M", email="ravi@example.com", phone_number="1122334455")

    def test_search_exact_match(self):
        """Test search with exact match for a candidate name"""
        response = self.client.get('/api/candidates/search/?q=Ajay Kumar')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)
        self.assertEqual(response.json()['results'][0]['name'], "Ajay Kumar")

    def test_search_partial_match(self):
        """Test search with partial match for a candidate name"""
        response = self.client.get('/api/candidates/search/?q=Ajay')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        self.assertIn("Ajay Kumar", [result['name'] for result in response.json()['results']])

    def test_search_no_match(self):
        """Test search with a query that has no matches"""
        response = self.client.get('/api/candidates/search/?q=Nonexistent Name')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 0)

    def test_search_empty_query(self):
        """Test search with an empty query parameter"""
        response = self.client.get('/api/candidates/search/?q=')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_search_sorted_by_relevance(self):
        """
        Test that search results are sorted by relevance.
        Candidates matching more terms should appear earlier in the results.
        """
        response = self.client.get('/api/candidates/search/?q=Ajay Kumar Yadav')
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']

        # Assert the order of results based on relevancy
        self.assertEqual(results[0]['name'], "Ajay Kumar Yadav")  # Highest relevancy
        self.assertEqual(results[1]['name'], "Ajay Kumar")        # Partial match
        self.assertEqual(results[2]['name'], "Kumar Yadav")       # Single term match

    def test_pagination(self):
        """Test pagination in the search results"""
        response = self.client.get('/api/candidates/search/?q=Ajay&page=1&page_size=2')
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        # Assert the number of results per page
        self.assertEqual(len(json_response['results']), 2)
        self.assertIn("next", json_response)
        self.assertIn("previous", json_response)

    def test_invalid_pagination(self):
        """Test handling of invalid pagination parameters"""
        response = self.client.get('/api/candidates/search/?q=Ajay&page=999&page_size=2')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/api/candidates/search/?q=Ajay&page=-1')
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/api/candidates/search/?q=Ajay&page_size=0')
        self.assertEqual(response.status_code, 400)

    def test_multi_term_query(self):
        """Test a query with multiple terms"""
        response = self.client.get('/api/candidates/search/?q=Ajay Yadav')
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']

        # Assert that all results contain at least one term
        for result in results:
            self.assertTrue("Ajay" in result['name'] or "Yadav" in result['name'])






class CandidateCreateAPITest(TestCase):
    def setUp(self):
        """
        Set up the API client for testing.
        """
        self.client = APIClient()
        self.valid_payload = {
            "name": "Ajay Kumar",
            "age": 30,
            "gender": "M",
            "email": "ajay@example.com",
            "phone_number": "1234567890"
        }

    def test_create_candidate_success(self):
        """
        Test creating a candidate with valid data.
        """
        response = self.client.post('/api/candidates/', data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Candidate.objects.count(), 1)
        self.assertEqual(Candidate.objects.first().name, "Ajay Kumar")

    def test_create_candidate_missing_field(self):
        """
        Test creating a candidate with missing required fields.
        """
        payload = {
            "name": "Ajay Kumar",
            "age": 30,
            "gender": "M",
            # Missing email
            "phone_number": "1234567890"
        }
        response = self.client.post('/api/candidates/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["error"])

    def test_create_candidate_invalid_email(self):
        """
        Test creating a candidate with an invalid email.
        """
        payload = {
            "name": "Ajay Kumar",
            "age": 30,
            "gender": "M",
            "email": "invalid-email",
            "phone_number": "1234567890"
        }
        response = self.client.post('/api/candidates/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["error"])

    def test_create_candidate_invalid_age(self):
        """
        Test creating a candidate with an invalid age.
        """
        payload = {
            "name": "Ajay Kumar",
            "age": 15,  # Invalid age, less than 18
            "gender": "M",
            "email": "ajay@example.com",
            "phone_number": "1234567890"
        }
        response = self.client.post('/api/candidates/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.json()["error"])

    def test_create_candidate_invalid_gender(self):
        """
        Test creating a candidate with an invalid gender.
        """
        payload = {
            "name": "Ajay Kumar",
            "age": 30,
            "gender": "Invalid",  # Invalid gender
            "email": "ajay@example.com",
            "phone_number": "1234567890"
        }
        response = self.client.post('/api/candidates/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gender", response.json()["error"])

    def test_create_candidate_duplicate_email(self):
        """
        Test creating a candidate with a duplicate email.
        """
        Candidate.objects.create(
            name="Existing Candidate",
            age=30,
            gender="M",
            email="ajay@example.com",
            phone_number="9876543210"
        )
        response = self.client.post('/api/candidates/', data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["error"])

    def test_create_candidate_invalid_phone_number(self):
        """
        Test creating a candidate with an invalid phone number.
        """
        payload = {
            "name": "Ajay Kumar",
            "age": 30,
            "gender": "M",
            "email": "ajay@example.com",
            "phone_number": "123"  # Invalid phone number, too short
        }
        response = self.client.post('/api/candidates/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.json()["error"])



from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Candidate


class CandidateUpdateDeleteAPITest(TestCase):
    def setUp(self):
        """
        Set up the API client and seed the database with a candidate.
        """
        self.client = APIClient()
        self.candidate = Candidate.objects.create(
            name="Ajay Kumar",
            age=30,
            gender="M",
            email="ajay@example.com",
            phone_number="1234567890"
        )
        self.update_payload = {
            "name": "Ajay Kumar Updated",
            "age": 35,
            "gender": "M",
            "email": "updated@example.com",
            "phone_number": "9876543210"
        }

    def test_update_candidate_success(self):
        """
        Test updating a candidate with valid data.
        """
        response = self.client.put(f'/api/candidates/{self.candidate.id}/', data=self.update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Ajay Kumar Updated")
        self.assertEqual(response.json()["email"], "updated@example.com")

        # Ensure the candidate is updated in the database
        candidate = Candidate.objects.get(id=self.candidate.id)
        self.assertEqual(candidate.name, "Ajay Kumar Updated")
        self.assertEqual(candidate.email, "updated@example.com")

    def test_update_candidate_invalid_email(self):
        """
        Test updating a candidate with an invalid email.
        """
        payload = self.update_payload.copy()
        payload["email"] = "invalid-email"
        response = self.client.put(f'/api/candidates/{self.candidate.id}/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json()["error"])

    def test_update_candidate_invalid_age(self):
        """
        Test updating a candidate with an invalid age.
        """
        payload = self.update_payload.copy()
        payload["age"] = 15  # Invalid age
        response = self.client.put(f'/api/candidates/{self.candidate.id}/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.json()["error"])

    def test_update_candidate_not_found(self):
        """
        Test updating a candidate that does not exist.
        """
        response = self.client.put('/api/candidates/9999/', data=self.update_payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_candidate(self):
        """
        Test partially updating a candidate.
        """
        partial_payload = {"name": "Ajay Partial Update"}
        response = self.client.patch(f'/api/candidates/{self.candidate.id}/', data=partial_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], "Ajay Partial Update")

        # Ensure other fields remain unchanged
        candidate = Candidate.objects.get(id=self.candidate.id)
        self.assertEqual(candidate.age, 30)
        self.assertEqual(candidate.email, "ajay@example.com")

    def test_delete_candidate_success(self):
        """
        Test deleting a candidate successfully.
        """
        response = self.client.delete(f'/api/candidates/{self.candidate.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the candidate is deleted from the database
        with self.assertRaises(Candidate.DoesNotExist):
            Candidate.objects.get(id=self.candidate.id)

    def test_delete_candidate_not_found(self):
        """
        Test deleting a candidate that does not exist.
        """
        response = self.client.delete('/api/candidates/9999/')
        self.assertEqual(response.status_code, 404)
        print(response.json())
        self.assertEqual(response.json()["error"], "An unexpected error occurred.")
        self.assertEqual(response.json()["detail"], "No Candidate matches the given query.")
    
    