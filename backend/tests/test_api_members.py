"""Unit tests for Members API endpoints."""

import pytest


class TestCreateMember:
    """Tests for POST /api/members endpoint."""

    def test_create_member_success(self, client, sample_member_data):
        """Test successful member creation."""
        response = client.post("/api/members", json=sample_member_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_member_data["name"]
        assert data["email"] == sample_member_data["email"]
        assert data["phone"] == sample_member_data["phone"]
        assert data["isActive"] is True
        assert "id" in data

    def test_create_member_minimal_data(self, client):
        """Test member creation with minimal required fields."""
        minimal_data = {
            "name": "Jane Smith",
            "email": "jane.smith@example.com"
        }
        response = client.post("/api/members", json=minimal_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Smith"
        assert data["email"] == "jane.smith@example.com"

    def test_create_member_duplicate_email(self, client, sample_member_data):
        """Test that duplicate email is rejected."""
        # Create first member
        client.post("/api/members", json=sample_member_data)
        
        # Try to create another with same email
        response = client.post("/api/members", json=sample_member_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_member_missing_name(self, client):
        """Test that missing name is rejected."""
        data = {"email": "test@example.com"}
        response = client.post("/api/members", json=data)
        
        assert response.status_code == 422

    def test_create_member_missing_email(self, client):
        """Test that missing email is rejected."""
        data = {"name": "Test User"}
        response = client.post("/api/members", json=data)
        
        assert response.status_code == 422

    def test_create_member_invalid_email(self, client):
        """Test that invalid email format is rejected."""
        data = {
            "name": "Test User",
            "email": "invalid-email"
        }
        response = client.post("/api/members", json=data)
        
        assert response.status_code == 422

    def test_create_member_empty_name(self, client):
        """Test that empty name is rejected."""
        data = {
            "name": "",
            "email": "test@example.com"
        }
        response = client.post("/api/members", json=data)
        
        assert response.status_code == 422


class TestGetMember:
    """Tests for GET /api/members/{id} endpoint."""

    def test_get_member_success(self, client, created_member):
        """Test successful member retrieval."""
        member_id = created_member["id"]
        response = client.get(f"/api/members/{member_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == member_id
        assert data["name"] == created_member["name"]

    def test_get_member_not_found(self, client):
        """Test getting non-existent member."""
        response = client.get("/api/members/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestListMembers:
    """Tests for GET /api/members endpoint."""

    def test_list_members_empty(self, client):
        """Test listing members when none exist."""
        response = client.get("/api/members")
        
        assert response.status_code == 200
        data = response.json()
        assert data["members"] == []
        assert data["totalCount"] == 0

    def test_list_members_with_data(self, client, created_member):
        """Test listing members with existing data."""
        response = client.get("/api/members")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 1
        assert data["totalCount"] == 1
        assert data["members"][0]["id"] == created_member["id"]

    def test_list_members_pagination(self, client):
        """Test member listing pagination."""
        # Create multiple members
        for i in range(15):
            client.post("/api/members", json={
                "name": f"Member {i}",
                "email": f"member{i}@example.com"
            })
        
        # Get first page
        response = client.get("/api/members?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 10
        assert data["totalCount"] == 15
        assert data["page"] == 1
        
        # Get second page
        response = client.get("/api/members?page=2&page_size=10")
        data = response.json()
        assert len(data["members"]) == 5
        assert data["page"] == 2

    def test_list_members_search_by_name(self, client):
        """Test member search by name."""
        client.post("/api/members", json={"name": "Alice Johnson", "email": "alice@example.com"})
        client.post("/api/members", json={"name": "Bob Wilson", "email": "bob@example.com"})
        
        response = client.get("/api/members?search=Alice")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 1
        assert "Alice" in data["members"][0]["name"]

    def test_list_members_search_by_email(self, client):
        """Test member search by email."""
        client.post("/api/members", json={"name": "User 1", "email": "alice@example.com"})
        client.post("/api/members", json={"name": "User 2", "email": "bob@test.com"})
        
        response = client.get("/api/members?search=alice")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 1
        assert "alice" in data["members"][0]["email"]


class TestUpdateMember:
    """Tests for PUT /api/members/{id} endpoint."""

    def test_update_member_success(self, client, created_member):
        """Test successful member update."""
        member_id = created_member["id"]
        update_data = {"name": "Updated Name"}
        
        response = client.put(f"/api/members/{member_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == created_member["email"]  # Unchanged

    def test_update_member_multiple_fields(self, client, created_member):
        """Test updating multiple fields."""
        member_id = created_member["id"]
        update_data = {
            "name": "New Name",
            "phone": "555-9999",
            "address": "456 New Street"
        }
        
        response = client.put(f"/api/members/{member_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["phone"] == "555-9999"
        assert data["address"] == "456 New Street"

    def test_update_member_deactivate(self, client, created_member):
        """Test deactivating a member."""
        member_id = created_member["id"]
        
        response = client.put(f"/api/members/{member_id}", json={"isActive": False})
        
        assert response.status_code == 200
        data = response.json()
        assert data["isActive"] is False

    def test_update_member_not_found(self, client):
        """Test updating non-existent member."""
        response = client.put("/api/members/99999", json={"name": "New Name"})
        
        assert response.status_code == 404

    def test_update_member_duplicate_email(self, client, sample_member_data):
        """Test that updating to existing email is rejected."""
        # Create two members
        member1 = client.post("/api/members", json=sample_member_data).json()
        member2_data = {**sample_member_data, "email": "other@example.com"}
        member2 = client.post("/api/members", json=member2_data).json()
        
        # Try to update member2 with member1's email
        response = client.put(f"/api/members/{member2['id']}", json={"email": sample_member_data["email"]})
        
        assert response.status_code == 409


class TestDeleteMember:
    """Tests for DELETE /api/members/{id} endpoint."""

    def test_delete_member_success(self, client, created_member):
        """Test successful member deletion."""
        member_id = created_member["id"]
        
        response = client.delete(f"/api/members/{member_id}")
        
        assert response.status_code == 200
        
        # Verify member is deleted
        get_response = client.get(f"/api/members/{member_id}")
        assert get_response.status_code == 404

    def test_delete_member_not_found(self, client):
        """Test deleting non-existent member."""
        response = client.delete("/api/members/99999")
        
        assert response.status_code == 404

    def test_delete_member_with_active_borrow(self, client, created_book, created_member):
        """Test that member with active borrow cannot be deleted."""
        # Borrow a book
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        client.post("/api/borrows", json=borrow_data)
        
        # Try to delete member
        response = client.delete(f"/api/members/{created_member['id']}")
        
        assert response.status_code == 400
        assert "active borrow" in response.json()["detail"]


class TestGetMemberBorrowedBooks:
    """Tests for GET /api/members/{id}/borrowed endpoint."""

    def test_get_borrowed_books_empty(self, client, created_member):
        """Test getting borrowed books when member has none."""
        response = client.get(f"/api/members/{created_member['id']}/borrowed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["records"] == []

    def test_get_borrowed_books_with_data(self, client, created_book, created_member):
        """Test getting borrowed books with active borrows."""
        # Borrow a book
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        client.post("/api/borrows", json=borrow_data)
        
        response = client.get(f"/api/members/{created_member['id']}/borrowed")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) == 1
        assert data["member"]["id"] == created_member["id"]

    def test_get_borrowed_books_member_not_found(self, client):
        """Test getting borrowed books for non-existent member."""
        response = client.get("/api/members/99999/borrowed")
        
        assert response.status_code == 404
