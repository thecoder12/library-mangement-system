"""Unit tests for Borrows API endpoints."""

import pytest


class TestBorrowBook:
    """Tests for POST /api/borrows endpoint."""

    def test_borrow_book_success(self, client, created_book, created_member):
        """Test successful book borrowing."""
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        
        response = client.post("/api/borrows", json=borrow_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["bookId"] == created_book["id"]
        assert data["memberId"] == created_member["id"]
        assert data["status"] == "BORROWED"
        assert "borrowDate" in data
        assert "dueDate" in data
        assert "id" in data

    def test_borrow_book_decreases_availability(self, client, created_book, created_member):
        """Test that borrowing decreases available copies."""
        initial_available = created_book["availableCopies"]
        
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        client.post("/api/borrows", json=borrow_data)
        
        # Check book availability
        response = client.get(f"/api/books/{created_book['id']}")
        data = response.json()
        assert data["availableCopies"] == initial_available - 1

    def test_borrow_book_not_available(self, client, sample_member_data):
        """Test borrowing when no copies available."""
        # Create book with 1 copy
        book = client.post("/api/books", json={
            "title": "Single Copy Book",
            "author": "Author",
            "totalCopies": 1
        }).json()
        
        # Create two members
        member1 = client.post("/api/members", json=sample_member_data).json()
        member2 = client.post("/api/members", json={
            **sample_member_data,
            "email": "member2@example.com"
        }).json()
        
        # First member borrows successfully
        client.post("/api/borrows", json={"bookId": book["id"], "memberId": member1["id"]})
        
        # Second member tries to borrow - should fail
        response = client.post("/api/borrows", json={"bookId": book["id"], "memberId": member2["id"]})
        
        assert response.status_code == 400
        assert "not available" in response.json()["detail"]

    def test_borrow_book_not_found(self, client, created_member):
        """Test borrowing non-existent book."""
        borrow_data = {
            "bookId": 99999,
            "memberId": created_member["id"]
        }
        
        response = client.post("/api/borrows", json=borrow_data)
        
        assert response.status_code == 404
        assert "Book" in response.json()["detail"]

    def test_borrow_member_not_found(self, client, created_book):
        """Test borrowing with non-existent member."""
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": 99999
        }
        
        response = client.post("/api/borrows", json=borrow_data)
        
        assert response.status_code == 404
        assert "Member" in response.json()["detail"]

    def test_borrow_inactive_member(self, client, created_book, created_member):
        """Test that inactive member cannot borrow."""
        # Deactivate member
        client.put(f"/api/members/{created_member['id']}", json={"isActive": False})
        
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        
        response = client.post("/api/borrows", json=borrow_data)
        
        assert response.status_code == 400
        assert "not active" in response.json()["detail"]

    def test_borrow_same_book_twice(self, client, created_book, created_member):
        """Test that same member cannot borrow same book twice."""
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        
        # First borrow succeeds
        client.post("/api/borrows", json=borrow_data)
        
        # Second borrow fails
        response = client.post("/api/borrows", json=borrow_data)
        
        assert response.status_code == 409
        assert "already has this book" in response.json()["detail"]


class TestReturnBook:
    """Tests for POST /api/borrows/{id}/return endpoint."""

    def test_return_book_success(self, client, created_book, created_member):
        """Test successful book return."""
        # Borrow first
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        borrow = client.post("/api/borrows", json=borrow_data).json()
        
        # Return
        response = client.post(f"/api/borrows/{borrow['id']}/return")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "RETURNED"
        assert "returnDate" in data

    def test_return_book_increases_availability(self, client, created_book, created_member):
        """Test that returning increases available copies."""
        initial_available = created_book["availableCopies"]
        
        # Borrow
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        borrow = client.post("/api/borrows", json=borrow_data).json()
        
        # Return
        client.post(f"/api/borrows/{borrow['id']}/return")
        
        # Check book availability
        response = client.get(f"/api/books/{created_book['id']}")
        data = response.json()
        assert data["availableCopies"] == initial_available

    def test_return_book_not_found(self, client):
        """Test returning non-existent borrow record."""
        response = client.post("/api/borrows/99999/return")
        
        assert response.status_code == 404

    def test_return_book_already_returned(self, client, created_book, created_member):
        """Test that already returned book cannot be returned again."""
        # Borrow
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        borrow = client.post("/api/borrows", json=borrow_data).json()
        
        # First return succeeds
        client.post(f"/api/borrows/{borrow['id']}/return")
        
        # Second return fails
        response = client.post(f"/api/borrows/{borrow['id']}/return")
        
        assert response.status_code == 400
        assert "already been returned" in response.json()["detail"]


class TestGetBorrowRecord:
    """Tests for GET /api/borrows/{id} endpoint."""

    def test_get_borrow_record_success(self, client, created_book, created_member):
        """Test successful borrow record retrieval."""
        # Create borrow
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        borrow = client.post("/api/borrows", json=borrow_data).json()
        
        response = client.get(f"/api/borrows/{borrow['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == borrow["id"]
        assert data["status"] == "BORROWED"

    def test_get_borrow_record_not_found(self, client):
        """Test getting non-existent borrow record."""
        response = client.get("/api/borrows/99999")
        
        assert response.status_code == 404


class TestListBorrowRecords:
    """Tests for GET /api/borrows endpoint."""

    def test_list_borrows_empty(self, client):
        """Test listing borrow records when none exist."""
        response = client.get("/api/borrows")
        
        assert response.status_code == 200
        data = response.json()
        assert data["records"] == []
        assert data["totalCount"] == 0

    def test_list_borrows_with_data(self, client, created_book, created_member):
        """Test listing borrow records with existing data."""
        # Create borrow
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        borrow = client.post("/api/borrows", json=borrow_data).json()
        
        response = client.get("/api/borrows")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) == 1
        assert data["records"][0]["id"] == borrow["id"]

    def test_list_borrows_filter_by_member(self, client, created_book, sample_member_data):
        """Test filtering borrow records by member."""
        # Create two members
        member1 = client.post("/api/members", json=sample_member_data).json()
        member2 = client.post("/api/members", json={
            **sample_member_data,
            "email": "member2@example.com"
        }).json()
        
        # Create book with 2 copies
        book = client.post("/api/books", json={
            "title": "Multi Copy Book",
            "author": "Author",
            "totalCopies": 2
        }).json()
        
        # Both members borrow
        client.post("/api/borrows", json={"bookId": book["id"], "memberId": member1["id"]})
        client.post("/api/borrows", json={"bookId": book["id"], "memberId": member2["id"]})
        
        # Filter by member1
        response = client.get(f"/api/borrows?member_id={member1['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) == 1
        assert data["records"][0]["memberId"] == member1["id"]

    def test_list_borrows_filter_by_status(self, client, created_book, created_member):
        """Test filtering borrow records by status."""
        # Create borrow
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        borrow = client.post("/api/borrows", json=borrow_data).json()
        
        # Filter by BORROWED status
        response = client.get("/api/borrows?status=BORROWED")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) == 1
        
        # Return the book
        client.post(f"/api/borrows/{borrow['id']}/return")
        
        # Filter by BORROWED status (should be empty now)
        response = client.get("/api/borrows?status=BORROWED")
        data = response.json()
        assert len(data["records"]) == 0
        
        # Filter by RETURNED status
        response = client.get("/api/borrows?status=RETURNED")
        data = response.json()
        assert len(data["records"]) == 1

    def test_list_borrows_pagination(self, client, sample_member_data):
        """Test borrow records pagination."""
        # Create multiple members to bypass the per-member borrow limit (5 books)
        members = []
        for i in range(3):
            member = client.post("/api/members", json={
                **sample_member_data,
                "email": f"member{i}@example.com"
            }).json()
            members.append(member)
        
        # Create multiple books and borrows (5 per member = 15 total)
        for i in range(15):
            book = client.post("/api/books", json={
                "title": f"Book {i}",
                "author": f"Author {i}"
            }).json()
            # Distribute borrows across members (5 each)
            member = members[i // 5]
            client.post("/api/borrows", json={"bookId": book["id"], "memberId": member["id"]})
        
        # Get first page
        response = client.get("/api/borrows?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["records"]) == 10
        assert data["totalCount"] == 15
        
        # Get second page
        response = client.get("/api/borrows?page=2&page_size=10")
        data = response.json()
        assert len(data["records"]) == 5
