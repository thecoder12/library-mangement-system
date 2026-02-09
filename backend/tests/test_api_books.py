"""Unit tests for Books API endpoints."""

import pytest


class TestCreateBook:
    """Tests for POST /api/books endpoint."""

    def test_create_book_success(self, client, sample_book_data):
        """Test successful book creation."""
        response = client.post("/api/books", json=sample_book_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_book_data["title"]
        assert data["author"] == sample_book_data["author"]
        assert data["isbn"] == sample_book_data["isbn"]
        assert data["totalCopies"] == sample_book_data["totalCopies"]
        assert data["availableCopies"] == sample_book_data["totalCopies"]
        assert "id" in data

    def test_create_book_minimal_data(self, client):
        """Test book creation with minimal required fields."""
        minimal_data = {
            "title": "Minimal Book",
            "author": "Author Name"
        }
        response = client.post("/api/books", json=minimal_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Minimal Book"
        assert data["totalCopies"] == 1  # Default value

    def test_create_book_duplicate_isbn(self, client, sample_book_data):
        """Test that duplicate ISBN is rejected."""
        # Create first book
        client.post("/api/books", json=sample_book_data)
        
        # Try to create another with same ISBN
        response = client.post("/api/books", json=sample_book_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_book_missing_title(self, client):
        """Test that missing title is rejected."""
        data = {"author": "Test Author"}
        response = client.post("/api/books", json=data)
        
        assert response.status_code == 422

    def test_create_book_missing_author(self, client):
        """Test that missing author is rejected."""
        data = {"title": "Test Book"}
        response = client.post("/api/books", json=data)
        
        assert response.status_code == 422

    def test_create_book_invalid_total_copies_zero(self, client):
        """Test that zero total copies is rejected."""
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "totalCopies": 0
        }
        response = client.post("/api/books", json=data)
        
        assert response.status_code == 422

    def test_create_book_invalid_total_copies_negative(self, client):
        """Test that negative total copies is rejected."""
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "totalCopies": -5
        }
        response = client.post("/api/books", json=data)
        
        assert response.status_code == 422

    def test_create_book_total_copies_exceeds_max(self, client):
        """Test that total copies exceeding max is rejected."""
        data = {
            "title": "Test Book",
            "author": "Test Author",
            "totalCopies": 100000  # Exceeds 10000 limit
        }
        response = client.post("/api/books", json=data)
        
        assert response.status_code == 422


class TestGetBook:
    """Tests for GET /api/books/{id} endpoint."""

    def test_get_book_success(self, client, created_book):
        """Test successful book retrieval."""
        book_id = created_book["id"]
        response = client.get(f"/api/books/{book_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == created_book["title"]

    def test_get_book_not_found(self, client):
        """Test getting non-existent book."""
        response = client.get("/api/books/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestListBooks:
    """Tests for GET /api/books endpoint."""

    def test_list_books_empty(self, client):
        """Test listing books when none exist."""
        response = client.get("/api/books")
        
        assert response.status_code == 200
        data = response.json()
        assert data["books"] == []
        assert data["totalCount"] == 0

    def test_list_books_with_data(self, client, created_book):
        """Test listing books with existing data."""
        response = client.get("/api/books")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["books"]) == 1
        assert data["totalCount"] == 1
        assert data["books"][0]["id"] == created_book["id"]

    def test_list_books_pagination(self, client):
        """Test book listing pagination."""
        # Create multiple books
        for i in range(15):
            client.post("/api/books", json={
                "title": f"Book {i}",
                "author": f"Author {i}"
            })
        
        # Get first page
        response = client.get("/api/books?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["books"]) == 10
        assert data["totalCount"] == 15
        assert data["page"] == 1
        
        # Get second page
        response = client.get("/api/books?page=2&page_size=10")
        data = response.json()
        assert len(data["books"]) == 5
        assert data["page"] == 2

    def test_list_books_search_by_title(self, client):
        """Test book search by title."""
        client.post("/api/books", json={"title": "Python Programming", "author": "Author A"})
        client.post("/api/books", json={"title": "Java Basics", "author": "Author B"})
        
        response = client.get("/api/books?search=Python")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["books"]) == 1
        assert "Python" in data["books"][0]["title"]

    def test_list_books_search_by_author(self, client):
        """Test book search by author."""
        client.post("/api/books", json={"title": "Book 1", "author": "John Smith"})
        client.post("/api/books", json={"title": "Book 2", "author": "Jane Doe"})
        
        response = client.get("/api/books?search=John")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["books"]) == 1
        assert "John" in data["books"][0]["author"]


class TestUpdateBook:
    """Tests for PUT /api/books/{id} endpoint."""

    def test_update_book_success(self, client, created_book):
        """Test successful book update."""
        book_id = created_book["id"]
        update_data = {"title": "Updated Title"}
        
        response = client.put(f"/api/books/{book_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["author"] == created_book["author"]  # Unchanged

    def test_update_book_multiple_fields(self, client, created_book):
        """Test updating multiple fields."""
        book_id = created_book["id"]
        update_data = {
            "title": "New Title",
            "author": "New Author",
            "genre": "Non-fiction"
        }
        
        response = client.put(f"/api/books/{book_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["author"] == "New Author"
        assert data["genre"] == "Non-fiction"

    def test_update_book_not_found(self, client):
        """Test updating non-existent book."""
        response = client.put("/api/books/99999", json={"title": "New Title"})
        
        assert response.status_code == 404

    def test_update_book_duplicate_isbn(self, client, sample_book_data):
        """Test that updating to existing ISBN is rejected."""
        # Create two books
        book1 = client.post("/api/books", json=sample_book_data).json()
        book2_data = {**sample_book_data, "isbn": "978-1-234567-89-0"}
        book2 = client.post("/api/books", json=book2_data).json()
        
        # Try to update book2 with book1's ISBN
        response = client.put(f"/api/books/{book2['id']}", json={"isbn": sample_book_data["isbn"]})
        
        assert response.status_code == 409


class TestDeleteBook:
    """Tests for DELETE /api/books/{id} endpoint."""

    def test_delete_book_success(self, client, created_book):
        """Test successful book deletion."""
        book_id = created_book["id"]
        
        response = client.delete(f"/api/books/{book_id}")
        
        assert response.status_code == 200
        
        # Verify book is deleted
        get_response = client.get(f"/api/books/{book_id}")
        assert get_response.status_code == 404

    def test_delete_book_not_found(self, client):
        """Test deleting non-existent book."""
        response = client.delete("/api/books/99999")
        
        assert response.status_code == 404

    def test_delete_book_with_active_borrow(self, client, created_book, created_member):
        """Test that book with active borrow cannot be deleted."""
        # Borrow the book
        borrow_data = {
            "bookId": created_book["id"],
            "memberId": created_member["id"]
        }
        client.post("/api/borrows", json=borrow_data)
        
        # Try to delete book
        response = client.delete(f"/api/books/{created_book['id']}")
        
        assert response.status_code == 400
        assert "active borrow" in response.json()["detail"]
