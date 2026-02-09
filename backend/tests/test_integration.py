"""Integration tests for end-to-end workflows."""

import pytest


class TestBorrowReturnCycle:
    """Integration tests for complete borrow/return workflows."""

    def test_full_borrow_return_cycle_restores_availability(self, client):
        """Test that a complete borrow-return cycle restores book availability."""
        # Setup: Create a book with 3 copies
        book = client.post("/api/books", json={
            "title": "Integration Test Book",
            "author": "Test Author",
            "isbn": "978-1-111111-11-1",
            "totalCopies": 3
        }).json()
        
        # Setup: Create a member
        member = client.post("/api/members", json={
            "name": "Test Member",
            "email": "integration@test.com"
        }).json()
        
        # Verify initial state
        assert book["availableCopies"] == 3
        assert book["totalCopies"] == 3
        
        # Step 1: Borrow the book
        borrow_response = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": member["id"]
        })
        assert borrow_response.status_code == 200
        borrow_record = borrow_response.json()
        
        # Step 2: Verify availability decreased
        book_after_borrow = client.get(f"/api/books/{book['id']}").json()
        assert book_after_borrow["availableCopies"] == 2
        
        # Step 3: Verify member's borrowed books
        borrowed_books = client.get(f"/api/members/{member['id']}/borrowed").json()
        assert len(borrowed_books["records"]) == 1
        assert borrowed_books["records"][0]["bookId"] == book["id"]
        
        # Step 4: Return the book
        return_response = client.post(f"/api/borrows/{borrow_record['id']}/return")
        assert return_response.status_code == 200
        assert return_response.json()["status"] == "RETURNED"
        
        # Step 5: Verify availability restored
        book_after_return = client.get(f"/api/books/{book['id']}").json()
        assert book_after_return["availableCopies"] == 3
        
        # Step 6: Verify member has no active borrows
        borrowed_after_return = client.get(f"/api/members/{member['id']}/borrowed").json()
        assert len(borrowed_after_return["records"]) == 0


class TestMemberBorrowLimit:
    """Integration tests for member borrow limit enforcement."""

    def test_member_can_borrow_up_to_limit_then_borrow_again_after_returning(self, client):
        """Test that member can borrow again after returning books when at limit."""
        # Setup: Create member
        member = client.post("/api/members", json={
            "name": "Limit Test Member",
            "email": "limit.test@example.com"
        }).json()
        
        # Setup: Create 6 books (more than the limit of 5)
        books = []
        for i in range(6):
            book = client.post("/api/books", json={
                "title": f"Limit Test Book {i+1}",
                "author": "Test Author",
                "isbn": f"978-2-{i:06d}-00-{i}"
            }).json()
            books.append(book)
        
        # Step 1: Borrow 5 books (reach the limit)
        borrow_records = []
        for i in range(5):
            response = client.post("/api/borrows", json={
                "bookId": books[i]["id"],
                "memberId": member["id"]
            })
            assert response.status_code == 200, f"Should be able to borrow book {i+1}"
            borrow_records.append(response.json())
        
        # Step 2: Try to borrow 6th book - should fail
        response = client.post("/api/borrows", json={
            "bookId": books[5]["id"],
            "memberId": member["id"]
        })
        assert response.status_code == 400
        assert "maximum borrow limit" in response.json()["detail"].lower()
        
        # Step 3: Return one book
        return_response = client.post(f"/api/borrows/{borrow_records[0]['id']}/return")
        assert return_response.status_code == 200
        
        # Step 4: Now should be able to borrow 6th book
        response = client.post("/api/borrows", json={
            "bookId": books[5]["id"],
            "memberId": member["id"]
        })
        assert response.status_code == 200
        assert response.json()["bookId"] == books[5]["id"]


class TestBookAvailabilityWithMultipleBorrowers:
    """Integration tests for book availability with multiple borrowers."""

    def test_multiple_members_borrow_limited_copies(self, client):
        """Test that multiple members can borrow until copies run out."""
        # Setup: Create a book with 2 copies
        book = client.post("/api/books", json={
            "title": "Limited Copies Book",
            "author": "Test Author",
            "isbn": "978-3-222222-22-2",
            "totalCopies": 2
        }).json()
        
        # Setup: Create 3 members
        members = []
        for i in range(3):
            member = client.post("/api/members", json={
                "name": f"Member {i+1}",
                "email": f"member{i+1}@example.com"
            }).json()
            members.append(member)
        
        # Step 1: First member borrows - should succeed
        response1 = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": members[0]["id"]
        })
        assert response1.status_code == 200
        borrow1 = response1.json()
        
        # Step 2: Second member borrows - should succeed
        response2 = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": members[1]["id"]
        })
        assert response2.status_code == 200
        
        # Step 3: Verify no copies available
        book_status = client.get(f"/api/books/{book['id']}").json()
        assert book_status["availableCopies"] == 0
        
        # Step 4: Third member tries to borrow - should fail
        response3 = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": members[2]["id"]
        })
        assert response3.status_code == 400
        assert "not available" in response3.json()["detail"].lower()
        
        # Step 5: First member returns the book
        client.post(f"/api/borrows/{borrow1['id']}/return")
        
        # Step 6: Third member can now borrow
        response4 = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": members[2]["id"]
        })
        assert response4.status_code == 200


class TestMemberLifecycle:
    """Integration tests for complete member lifecycle."""

    def test_member_lifecycle_with_borrow_history(self, client):
        """Test member lifecycle: create, borrow, return, view history, deactivate."""
        # Step 1: Create member
        member = client.post("/api/members", json={
            "name": "Lifecycle Member",
            "email": "lifecycle@example.com",
            "phone": "555-1234",
            "address": "123 Test Lane"
        }).json()
        assert member["isActive"] is True
        
        # Step 2: Create books
        book1 = client.post("/api/books", json={
            "title": "Lifecycle Book 1",
            "author": "Author 1"
        }).json()
        book2 = client.post("/api/books", json={
            "title": "Lifecycle Book 2",
            "author": "Author 2"
        }).json()
        
        # Step 3: Borrow two books
        borrow1 = client.post("/api/borrows", json={
            "bookId": book1["id"],
            "memberId": member["id"]
        }).json()
        borrow2 = client.post("/api/borrows", json={
            "bookId": book2["id"],
            "memberId": member["id"]
        }).json()
        
        # Step 4: Verify borrowed books
        borrowed = client.get(f"/api/members/{member['id']}/borrowed").json()
        assert len(borrowed["records"]) == 2
        
        # Step 5: Return one book
        client.post(f"/api/borrows/{borrow1['id']}/return")
        
        # Step 6: Try to delete member with active borrow - should fail
        delete_response = client.delete(f"/api/members/{member['id']}")
        assert delete_response.status_code == 400
        assert "active borrow" in delete_response.json()["detail"].lower()
        
        # Step 7: Return second book
        client.post(f"/api/borrows/{borrow2['id']}/return")
        
        # Step 8: Verify borrow history still exists (via borrows endpoint)
        history = client.get(f"/api/borrows?memberId={member['id']}").json()
        assert history["totalCount"] == 2
        assert all(r["status"] == "RETURNED" for r in history["records"])
        
        # Step 9: Deactivate member (preferred over deletion to preserve history)
        update_response = client.put(f"/api/members/{member['id']}", json={
            "isActive": False
        })
        assert update_response.status_code == 200
        assert update_response.json()["isActive"] is False
        
        # Step 10: Deactivated member cannot borrow new books
        new_book = client.post("/api/books", json={
            "title": "New Book",
            "author": "New Author"
        }).json()
        borrow_response = client.post("/api/borrows", json={
            "bookId": new_book["id"],
            "memberId": member["id"]
        })
        assert borrow_response.status_code == 400
        assert "not active" in borrow_response.json()["detail"].lower()
    
    def test_member_without_history_can_be_deleted(self, client):
        """Test that a member with no borrow history can be deleted."""
        # Create member
        member = client.post("/api/members", json={
            "name": "Deletable Member",
            "email": "deletable@example.com"
        }).json()
        
        # Delete immediately (no borrow history)
        delete_response = client.delete(f"/api/members/{member['id']}")
        assert delete_response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/api/members/{member['id']}")
        assert get_response.status_code == 404


class TestBookLifecycle:
    """Integration tests for complete book lifecycle."""

    def test_book_lifecycle_with_borrow_history(self, client):
        """Test book lifecycle: create, update copies, borrow, return, verify state."""
        # Step 1: Create book with 2 copies
        book = client.post("/api/books", json={
            "title": "Lifecycle Book",
            "author": "Test Author",
            "isbn": "978-4-333333-33-3",
            "totalCopies": 2
        }).json()
        
        # Step 2: Create members
        member1 = client.post("/api/members", json={
            "name": "Book Test Member 1",
            "email": "booktest1@example.com"
        }).json()
        member2 = client.post("/api/members", json={
            "name": "Book Test Member 2",
            "email": "booktest2@example.com"
        }).json()
        
        # Step 3: Both members borrow the book
        borrow1 = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": member1["id"]
        }).json()
        borrow2 = client.post("/api/borrows", json={
            "bookId": book["id"],
            "memberId": member2["id"]
        }).json()
        
        # Step 4: Verify both copies borrowed
        book_status = client.get(f"/api/books/{book['id']}").json()
        assert book_status["availableCopies"] == 0
        assert book_status["totalCopies"] == 2
        
        # Step 5: Try to delete book with active borrows - should fail
        delete_response = client.delete(f"/api/books/{book['id']}")
        assert delete_response.status_code == 400
        assert "active borrow" in delete_response.json()["detail"].lower()
        
        # Step 6: Update book metadata while borrowed
        update_response = client.put(f"/api/books/{book['id']}", json={
            "title": "Updated Lifecycle Book",
            "genre": "Test Genre"
        })
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Lifecycle Book"
        
        # Step 7: Increase total copies (should increase available too)
        update_response = client.put(f"/api/books/{book['id']}", json={
            "totalCopies": 4
        })
        assert update_response.status_code == 200
        book_updated = update_response.json()
        # Available should increase by the difference (4-2=2), so 0+2=2
        assert book_updated["totalCopies"] == 4
        assert book_updated["availableCopies"] == 2
        
        # Step 8: Return both books
        client.post(f"/api/borrows/{borrow1['id']}/return")
        client.post(f"/api/borrows/{borrow2['id']}/return")
        
        # Step 9: Verify all copies available
        book_final = client.get(f"/api/books/{book['id']}").json()
        assert book_final["availableCopies"] == 4
        
        # Step 10: Verify borrow history preserved
        history = client.get(f"/api/borrows?bookId={book['id']}").json()
        assert history["totalCount"] == 2
        assert all(r["status"] == "RETURNED" for r in history["records"])
    
    def test_book_without_history_can_be_deleted(self, client):
        """Test that a book with no borrow history can be deleted."""
        # Create book
        book = client.post("/api/books", json={
            "title": "Deletable Book",
            "author": "Test Author",
            "isbn": "978-5-444444-44-4"
        }).json()
        
        # Delete immediately (no borrow history)
        delete_response = client.delete(f"/api/books/{book['id']}")
        assert delete_response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/api/books/{book['id']}")
        assert get_response.status_code == 404
